# 🚀 Gradio Data Agent Setup Guide

## 📦 Installation

### 1. Create Requirements File
Create a `requirements.txt` file:

```txt
gradio>=4.0.0
pandas>=1.5.0
sqlalchemy>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
pymysql>=1.1.0
psycopg2-binary>=2.9.0
numpy>=1.24.0
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🔧 Configuration Options

### Option 1: Environment Variables (.env file)
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Option 2: Direct Input in UI
The Gradio interface allows you to input all configuration directly in the web UI.

## 🚀 Running the Application

### Basic Launch
```bash
python gradio_data_agent.py
```

### Advanced Launch Options
```python
# In your script, modify the launch parameters:
demo.launch(
    server_name="0.0.0.0",     # Allow external access
    server_port=7860,          # Custom port
    share=True,                # Create public Gradio link
    debug=True,                # Debug mode
    auth=("username", "password")  # Add authentication
)
```

## 🌐 Deployment Options

### 1. Hugging Face Spaces (Free & Easy)

Create a new Space on [Hugging Face](https://huggingface.co/spaces):

1. **Create new Space**
   - Choose "Gradio" as SDK
   - Upload your files

2. **Files to include:**
   - `app.py` (rename your gradio_data_agent.py)
   - `requirements.txt`
   - `README.md`

3. **Set environment variables** in Space settings:
   ```
   OPENAI_API_KEY=your_key_here
   ```

### 2. Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 3. Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 7860

CMD ["python", "gradio_data_agent.py"]
```

Build and run:
```bash
docker build -t gradio-data-agent .
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key gradio-data-agent
```

### 4. Cloud Platforms

#### Google Cloud Run
```bash
gcloud run deploy gradio-data-agent \
    --image gcr.io/PROJECT-ID/gradio-data-agent \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars OPENAI_API_KEY=your_key
```

#### AWS ECS/Fargate
Use AWS CLI or console to deploy the Docker container.

## 🎯 Key Features of Gradio Version

### ✅ **Advantages over Streamlit:**
- **Simpler deployment** - Single file, fewer dependencies
- **Better sharing** - Built-in public link generation
- **Mobile friendly** - Responsive design out of the box
- **API generation** - Automatic API endpoint creation
- **HuggingFace integration** - Easy deployment to HF Spaces

### 🔧 **Interface Features:**
1. **Configuration Tab** - Set up database and OpenAI
2. **Query Interface** - Main chat interface
3. **Examples Tab** - Pre-built query examples
4. **CSV Upload** - Direct file upload support
5. **Real-time Results** - Instant query processing

## 📊 Usage Examples

### Business Queries
```python
# Sales Analysis
"Show me monthly sales by region"
"Which products have declining trends?"
"Find our top customers by revenue"

# Customer Analytics  
"Segment customers by purchase behavior"
"Calculate customer lifetime value"
"Show churn rate by cohort"

# Operational Reports
"Which inventory items need restocking?"
"Show employee performance metrics"
"Calculate operational costs by department"
```

## 🔒 Security & Production Setup

### Authentication
```python
# Add password protection
demo.launch(auth=("admin", "secure_password"))

# Or custom authentication function
def authenticate(username, password):
    return username == "admin" and password == "your_secure_password"

demo.launch(auth=authenticate)
```

### Database Security
```python
# Use read-only database user
db_config = {
    'type': 'mysql',
    'host': 'your-db-host.com',
    'database': 'company_db',
    'user': 'readonly_user',  # Read-only permissions
    'password': 'secure_password'
}
```

### Query Validation
```python
# Add query validation in production
def validate_query(sql_query):
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']
    return not any(keyword in sql_query.upper() for keyword in dangerous_keywords)
```

## 📱 Mobile & Sharing

### Public Links
```python
# Generate public Gradio link (temporary)
demo.launch(share=True)

# Custom domain (for permanent deployment)
demo.launch(server_name="your-domain.com", server_port=80)
```

### API Usage
Gradio automatically creates API endpoints:
```bash
# Get API info
curl http://localhost:7860/api

# Use the API
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{"data": ["your query", "sql", true]}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Use different port
   demo.launch(server_port=7861)
   ```

2. **OpenAI Rate Limits**
   - Check your API usage at platform.openai.com
   - Add retry logic for rate limited requests

3. **Database Connection Issues**
   - Verify credentials and network access
   - Check firewall settings
   - Use connection pooling for high traffic

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Launch with debug
demo.launch(debug=True)
```

## 🚀 Advanced Features

### Custom Themes
```python
import gradio as gr

# Use custom theme
demo = gr.Blocks(theme=gr.themes.Glass())
# or
demo = gr.Blocks(theme="huggingface")
```

### Concurrent Users
```python
# Handle multiple users
demo.launch(
    max_threads=10,  # Max concurrent users
    show_error=True  # Show detailed errors
)
```

### Monitoring
```python
# Add usage analytics
def log_query(query, user_ip):
    with open("query_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {user_ip} - {query}\n")
```

## 📈 Performance Tips

1. **Database Connection Pooling**
2. **Query Result Caching**
3. **Async Processing for Large Queries**
4. **Rate Limiting for OpenAI API**
5. **Result Pagination for Large Datasets**

## 💡 Next Steps

1. **Test locally** with sample data
2. **Configure your company database**
3. **Deploy to cloud platform**
4. **Set up monitoring and logging**
5. **Add custom business logic**
6. **Train team on usage**

The Gradio version is perfect for rapid prototyping and easy sharing with your team!