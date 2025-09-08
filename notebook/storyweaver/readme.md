# StoryWeaver - Project Links & Submission Package

## 🔗 Essential Links for Judges

### 1. **Live Demo Application**
- **Primary**: `https://storyweaver-demo.streamlit.app/` (Deploy to Streamlit Cloud)
- **Backup**: `https://your-vercel-deployment.vercel.app/` (If using React version)
- **Local**: Include localhost screenshots if deployment issues occur

### 2. **Source Code Repository**
- **GitHub Main**: `https://github.com/yourusername/storyweaver-nano-banana`
- **Structure**:
  ```
  storyweaver/
  ├── app.py                 # Main Streamlit application
  ├── requirements.txt       # Python dependencies
  ├── README.md             # Detailed setup instructions
  ├── .streamlit/
  │   └── config.toml       # Streamlit configuration
  ├── assets/
  │   ├── demo_images/      # Sample reference images
  │   └── screenshots/      # App interface screenshots
  └── docs/
      ├── API_INTEGRATION.md # Gemini API setup guide
      └── FEATURES.md       # Feature documentation
  ```

### 3. **Video Demonstration**
- **YouTube**: `https://youtu.be/your-video-id` (Public, no login required)
- **Alternative**: Upload directly to Kaggle submission
- **Backup**: Vimeo or direct MP4 file

## 📁 Files to Upload to Kaggle

### Code Files
1. **app.py** - Complete Streamlit application
2. **requirements.txt** - Python dependencies
3. **config.json** - Configuration settings
4. **README.md** - Setup and usage instructions

### Documentation Files
1. **GEMINI_INTEGRATION.md** - Detailed API integration writeup
2. **FEATURES_DEMO.pdf** - Visual feature explanation
3. **ARCHITECTURE.md** - Technical architecture overview

### Demo Assets
1. **demo_video.mp4** - 2-minute demonstration video
2. **screenshots/** - Interface screenshots
3. **sample_outputs/** - Example generated images (if available)

## 🎯 Quick Deployment Commands

### Streamlit Cloud Deployment
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "StoryWeaver - Nano Banana Hackathon submission"
git branch -M main
git remote add origin https://github.com/yourusername/storyweaver-nano-banana.git
git push -u origin main

# 2. Deploy to Streamlit Cloud
# Go to share.streamlit.io
# Connect GitHub repo
# App will be live at: https://storyweaver-demo.streamlit.app/
```

### Alternative: Railway Deployment
```bash
# Quick deployment to Railway
railway login
railway init
railway up
# Live at: https://storyweaver-production.up.railway.app/
```

## 🎥 Video Demo Checklist

### Must-Have Shots (2 minutes max):
- [ ] **Opening**: App interface + title (0-10s)
- [ ] **Character Upload**: Reference image upload (10-20s)
- [ ] **Scene Generation**: Multiple scenes with same character (20-50s)
- [ ] **Dynamic Editing**: Edit scene with natural language (50-80s)
- [ ] **Story Flow**: Play through complete story (80-110s)
- [ ] **Closing**: Gemini 2.5 features summary (110-120s)

### Video Specs:
- **Length**: 2 minutes maximum
- **Quality**: 1080p minimum
- **Format**: MP4 (most compatible)
- **Audio**: Clear narration explaining features
- **Captions**: Include for accessibility

## 📝 Kaggle Submission Template

### Project Description
```
StoryWeaver - Dynamic Visual Storytelling with Gemini 2.5 Flash Image

🎯 INNOVATION: First visual storytelling platform leveraging Gemini 2.5's character consistency, dynamic editing, and world knowledge for narrative coherence.

🔗 LIVE DEMO: https://storyweaver-demo.streamlit.app/
🎥 VIDEO DEMO: https://youtu.be/your-video-id
💻 SOURCE CODE: https://github.com/yourusername/storyweaver-nano-banana

Key Features:
✅ Character consistency across story scenes
✅ Natural language scene editing
✅ Dynamic story flow and narrative coherence
✅ Real-time Gemini 2.5 Flash Image integration

Built with: Python, Streamlit, Gemini 2.5 Flash Image API
```

### Technical Links
```
📁 Complete Source Code: [GitHub Repository]
🚀 Live Application: [Streamlit/Railway URL]
🎬 Demo Video: [YouTube/Direct Link]
📊 Project Documentation: [Uploaded Files]
🔧 Setup Instructions: See README.md
```

## 🚨 Emergency Backup Links

If primary deployments fail:

### 1. **Code Sharing**
- **GitHub Gist**: For quick code sharing
- **CodeSandbox**: For React version
- **Repl.it**: For Python version with live preview

### 2. **Video Hosting**
- **Primary**: YouTube (unlisted but publicly accessible)
- **Backup**: Vimeo, Loom, or direct file upload
- **Emergency**: Screen recording software with local file

### 3. **Documentation**
- **Google Drive**: Public folder with all files
- **Dropbox**: Shared folder link
- **GitHub Pages**: Static documentation site

## 📋 Final Submission Checklist

### Required Elements:
- [ ] **Video Demo**: 2 minutes, publicly accessible
- [ ] **Live Demo**: Working application URL
- [ ] **Source Code**: GitHub repository with setup instructions
- [ ] **Gemini Integration Writeup**: 200 words explaining API usage

### Bonus Elements:
- [ ] **Technical Documentation**: Architecture and design decisions
- [ ] **Feature Walkthrough**: Detailed feature explanations
- [ ] **Future Roadmap**: Potential enhancements and applications
- [ ] **Screenshots**: High-quality interface screenshots

## 🎯 Judge-Friendly Presentation

### Make It Easy for Judges:
1. **One-Click Demo**: Live app accessible without setup
2. **Clear Video**: Shows all features in 2 minutes
3. **Clean Code**: Well-commented, easy to understand
4. **Setup Instructions**: Step-by-step deployment guide
5. **Feature Summary**: Quick bullet points of capabilities

### Scoring Optimization:
- **Innovation (40%)**: Emphasize unique Gemini 2.5 capabilities
- **Technical (30%)**: Show robust implementation and API integration
- **Impact (20%)**: Demonstrate real-world applications
- **Presentation (10%)**: Professional video and documentation

## 📞 Support Resources

If you need help with any deployment:
1. **Streamlit**: https://docs.streamlit.io/streamlit-community-cloud
2. **Railway**: https://docs.railway.app/
3. **Vercel**: https://vercel.com/docs
4. **GitHub**: https://docs.github.com/en/repositories

Remember: Even if the live demo has issues, a well-presented concept with clean code and good documentation can still score highly! Focus on showing the innovation and potential impact.
