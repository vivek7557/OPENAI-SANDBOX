import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import time
import json
from typing import List, Dict, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="StoryWeaver - Dynamic Visual Storytelling",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.scene-card {
    border: 2px solid #e1e5e9;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.scene-card.active {
    border-color: #667eea;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.feature-card {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem;
    text-align: center;
}

.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)

class StoryScene:
    def __init__(self, id: int, prompt: str):
        self.id = id
        self.prompt = prompt
        self.image = None
        self.generated = False

class StoryWeaver:
    def __init__(self):
        self.api_key = None
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Initialize Gemini API"""
        # Get API key from secrets or user input
        if 'gemini_api_key' in st.secrets:
            self.api_key = st.secrets['gemini_api_key']
        else:
            self.api_key = st.sidebar.text_input(
                "Enter your Gemini API Key", 
                type="password",
                help="Get your API key from Google AI Studio"
            )
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                st.sidebar.success("✅ Gemini API Connected")
            except Exception as e:
                st.sidebar.error(f"❌ API Error: {str(e)}")
    
    def generate_image(self, prompt: str, reference_image: Optional[Image.Image] = None) -> Optional[str]:
        """Generate image using Gemini 2.5 Flash Image"""
        if not self.model:
            st.error("Please configure your Gemini API key first")
            return None
        
        try:
            # Enhance prompt for better storytelling
            enhanced_prompt = f"""
            Create a high-quality, cinematic image for a visual story:
            {prompt}
            
            Style: Consistent character design, detailed background, professional illustration quality.
            Maintain visual consistency if this is part of a story sequence.
            """
            
            inputs = [enhanced_prompt]
            if reference_image:
                inputs.append(reference_image)
            
            # Note: This is a placeholder for the actual Gemini 2.5 Flash Image API
            # Replace with actual API call when available
            response = self.model.generate_content(inputs)
            
            # For demo purposes, return a placeholder
            # In real implementation, extract image from response
            return f"data:image/png;base64,{self.create_placeholder_image(prompt)}"
            
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None
    
    def create_placeholder_image(self, prompt: str) -> str:
        """Create placeholder image for demo"""
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        img = Image.new('RGB', (512, 512), color='#667eea')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"Scene:\n{prompt[:50]}..."
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (512 - text_width) // 2
        y = (512 - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font, align='center')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str

def main():
    # Initialize session state
    if 'story_scenes' not in st.session_state:
        st.session_state.story_scenes = [
            StoryScene(1, "A brave knight standing at a castle gate at dawn"),
            StoryScene(2, "The same knight entering a dark, mysterious forest"),
            StoryScene(3, "The knight discovering a magical glowing sword in a cave")
        ]
    
    if 'current_scene' not in st.session_state:
        st.session_state.current_scene = 0
    
    if 'reference_image' not in st.session_state:
        st.session_state.reference_image = None
    
    # Initialize StoryWeaver
    story_weaver = StoryWeaver()
    
    # Header
    st.markdown('<h1 class="main-header">StoryWeaver</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">Dynamic Visual Storytelling with Gemini 2.5 Flash Image</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar Controls
    with st.sidebar:
        st.header("🎛️ Story Controls")
        
        # Story Theme
        story_theme = st.selectbox(
            "Story Theme",
            ["Fantasy Adventure", "Sci-Fi Epic", "Mystery Thriller", "Adventure Quest"]
        )
        
        # Character Consistency
        character_consistency = st.checkbox("Character Consistency", value=True)
        
        # Reference Image Upload
        st.subheader("📸 Reference Image")
        uploaded_file = st.file_uploader(
            "Upload character reference", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image for character consistency across scenes"
        )
        
        if uploaded_file:
            st.session_state.reference_image = Image.open(uploaded_file)
            st.image(st.session_state.reference_image, caption="Reference Image", width=200)
        
        # Action Buttons
        st.subheader("🎬 Actions")
        
        if st.button("🪄 Generate All Scenes", use_container_width=True):
            generate_all_scenes(story_weaver)
        
        if st.button("▶️ Play Story", use_container_width=True):
            play_story_sequence()
        
        if st.button("➕ Add New Scene", use_container_width=True):
            add_new_scene()
        
        # Export Options
        st.subheader("💾 Export")
        if st.button("📥 Download Story", use_container_width=True):
            export_story()
    
    # Main Content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📖 Story Scenes")
        
        # Scene list
        for i, scene in enumerate(st.session_state.story_scenes):
            is_active = i == st.session_state.current_scene
            
            with st.container():
                if is_active:
                    st.markdown(f'<div class="scene-card active">', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
                
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    if st.button(f"Scene {i + 1}", key=f"scene_btn_{i}"):
                        st.session_state.current_scene = i
                        st.experimental_rerun()
                
                with col_b:
                    if scene.generated:
                        st.success("✅")
                    else:
                        if st.button("🪄", key=f"gen_btn_{i}", help="Generate this scene"):
                            generate_single_scene(story_weaver, i)
                
                # Editable prompt
                new_prompt = st.text_area(
                    f"Scene {i + 1} Description",
                    value=scene.prompt,
                    key=f"prompt_{i}",
                    height=80,
                    label_visibility="collapsed"
                )
                
                if new_prompt != scene.prompt:
                    st.session_state.story_scenes[i].prompt = new_prompt
                    st.session_state.story_scenes[i].generated = False
                    st.session_state.story_scenes[i].image = None
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.header(f"🎭 Scene {st.session_state.current_scene + 1} Viewer")
        
        current_scene = st.session_state.story_scenes[st.session_state.current_scene]
        
        # Navigation buttons
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.button("⬅️ Previous", disabled=st.session_state.current_scene == 0):
                st.session_state.current_scene = max(0, st.session_state.current_scene - 1)
                st.experimental_rerun()
        
        with col_info:
            st.markdown(f"**Scene {st.session_state.current_scene + 1} of {len(st.session_state.story_scenes)}**")
        
        with col_next:
            if st.button("Next ➡️", disabled=st.session_state.current_scene == len(st.session_state.story_scenes) - 1):
                st.session_state.current_scene = min(len(st.session_state.story_scenes) - 1, st.session_state.current_scene + 1)
                st.experimental_rerun()
        
        # Image display
        if current_scene.image:
            st.image(current_scene.image, caption=f"Scene {st.session_state.current_scene + 1}")
        else:
            st.info("🎨 Generate this scene to see the image")
            if st.button(f"Generate Scene {st.session_state.current_scene + 1}", use_container_width=True):
                generate_single_scene(story_weaver, st.session_state.current_scene)
        
        # Scene description
        st.markdown("### 📝 Scene Description")
        st.markdown(f"*{current_scene.prompt}*")
        
        # Edit scene
        st.markdown("### ✏️ Quick Edit")
        edit_instruction = st.text_input(
            "Modify this scene (e.g., 'make it darker', 'add a dragon'):",
            key="edit_instruction"
        )
        
        if st.button("Apply Edit") and edit_instruction:
            apply_scene_edit(story_weaver, st.session_state.current_scene, edit_instruction)
    
    # Features section
    st.markdown("---")
    st.header("🌟 Gemini 2.5 Flash Image Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎭 Character Consistency</h4>
            <p>Maintains the same character appearance across all story scenes using advanced identity preservation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>✏️ Dynamic Editing</h4>
            <p>Real-time scene modification with natural language prompts for instant visual changes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🧠 World Knowledge</h4>
            <p>Contextual understanding for rich, detailed scene generation with narrative coherence</p>
        </div>
        """, unsafe_allow_html=True)

def generate_single_scene(story_weaver: StoryWeaver, scene_index: int):
    """Generate a single scene"""
    with st.spinner(f"Generating Scene {scene_index + 1}..."):
        scene = st.session_state.story_scenes[scene_index]
        image = story_weaver.generate_image(
            scene.prompt, 
            st.session_state.reference_image
        )
        
        if image:
            scene.image = image
            scene.generated = True
            st.success(f"✅ Scene {scene_index + 1} generated!")
            st.experimental_rerun()

def generate_all_scenes(story_weaver: StoryWeaver):
    """Generate all scenes"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, scene in enumerate(st.session_state.story_scenes):
        if not scene.generated:
            status_text.text(f"Generating Scene {i + 1}...")
            progress_bar.progress((i + 1) / len(st.session_state.story_scenes))
            
            image = story_weaver.generate_image(
                scene.prompt,
                st.session_state.reference_image
            )
            
            if image:
                scene.image = image
                scene.generated = True
            
            time.sleep(1)  # Rate limiting
    
    status_text.text("All scenes generated!")
    st.success("🎉 All scenes have been generated!")

def play_story_sequence():
    """Play through story sequence automatically"""
    st.info("🎬 Playing story sequence...")
    for i in range(len(st.session_state.story_scenes)):
        st.session_state.current_scene = i
        time.sleep(2)  # 2 seconds per scene
        st.experimental_rerun()

def add_new_scene():
    """Add a new scene to the story"""
    new_scene = StoryScene(
        id=len(st.session_state.story_scenes) + 1,
        prompt=f"Continue the story from scene {len(st.session_state.story_scenes)}..."
    )
    st.session_state.story_scenes.append(new_scene)
    st.experimental_rerun()

def apply_scene_edit(story_weaver: StoryWeaver, scene_index: int, edit_instruction: str):
    """Apply edit to current scene"""
    scene = st.session_state.story_scenes[scene_index]
    
    # Combine original prompt with edit instruction
    edited_prompt = f"{scene.prompt}. {edit_instruction}"
    
    with st.spinner("Applying edit..."):
        image = story_weaver.generate_image(
            edited_prompt,
            st.session_state.reference_image
        )
        
        if image:
            scene.image = image
            scene.generated = True
            st.success("✅ Edit applied!")
            st.experimental_rerun()

def export_story():
    """Export story as JSON"""
    story_data = {
        "scenes": [
            {
                "id": scene.id,
                "prompt": scene.prompt,
                "generated": scene.generated
            }
            for scene in st.session_state.story_scenes
        ]
    }
    
    st.download_button(
        label="📥 Download Story JSON",
        data=json.dumps(story_data, indent=2),
        file_name="storyweaver_story.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()