# 🚀 Deployment Guide

This guide covers deployment options for the AI RAG System Demo.

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Git
- API keys (DeepSeek/OpenAI)

## 🏠 Local Development

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ai_rag_demo

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python run_demo.py
```

### Development Server

The development server runs on http://localhost:5000 with:
- Auto-reload on code changes
- Debug mode enabled
- Detailed error messages

## 🐳 Docker Deployment

### Build Image

```bash
# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE'
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run_demo.py"]
DOCKERFILE

# Build image
docker build -t ai-rag-demo .
```

### Run Container

```bash
# Run with environment variables
docker run -p 5000:5000 \
  -e DEEPSEEK_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  ai-rag-demo

# Or with .env file
docker run -p 5000:5000 --env-file .env ai-rag-demo
```

## ☁️ Cloud Deployment

### Heroku

1. **Create Heroku App**:
```bash
heroku create your-app-name
```

2. **Set Environment Variables**:
```bash
heroku config:set DEEPSEEK_API_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key
```

3. **Deploy**:
```bash
git push heroku main
```

### AWS EC2

1. **Launch EC2 Instance** (Ubuntu 20.04+)
2. **Install Dependencies**:
```bash
sudo apt update
sudo apt install python3 python3-pip nginx
```

3. **Deploy Application**:
```bash
git clone <repository-url>
cd ai_rag_demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Nginx**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. **Run with Gunicorn**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.web.app:app
```

### Google Cloud Platform

1. **Create App Engine**:
```yaml
# app.yaml
runtime: python39
entrypoint: gunicorn -b :$PORT src.web.app:app

env_variables:
  DEEPSEEK_API_KEY: "your_key"
  OPENAI_API_KEY: "your_key"
```

2. **Deploy**:
```bash
gcloud app deploy
```

## 🔧 Production Configuration

### Environment Variables

```env
# API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=production_collection

# RAG Configuration
TOP_K_RESULTS=5
CHUNK_SIZE=300
CHUNK_OVERLAP=50

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

### Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **HTTPS**: Use SSL certificates in production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Input Validation**: Validate all user inputs
5. **Error Handling**: Don't expose sensitive error details

### Performance Optimization

1. **Caching**: Implement Redis for caching
2. **Database**: Use persistent ChromaDB storage
3. **Load Balancing**: Use multiple worker processes
4. **CDN**: Serve static files through CDN

## 📊 Monitoring

### Health Checks

```bash
# Check if service is running
curl http://localhost:5000/api/stats

# Expected response:
{
  "total_documents": 100,
  "indexed_urls": 5,
  "llm_available": true
}
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Backup ChromaDB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Restore
tar -xzf chroma_backup_20231201.tar.gz
```

### Configuration Backup

```bash
# Backup configuration
cp .env .env.backup
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**:
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

2. **API Key Errors**:
```bash
# Verify environment variables
echo $DEEPSEEK_API_KEY
```

3. **Memory Issues**:
```bash
# Monitor memory usage
htop
# Restart service if needed
```

4. **Database Issues**:
```bash
# Check ChromaDB status
ls -la chroma_db/
# Recreate if corrupted
rm -rf chroma_db/
```

### Log Analysis

```bash
# View application logs
tail -f app.log

# Check system logs
journalctl -u your-service-name -f
```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Instances**: Run multiple app instances
3. **Shared Database**: Use external ChromaDB instance
4. **Caching Layer**: Implement Redis cluster

### Vertical Scaling

1. **More CPU**: Increase instance size
2. **More Memory**: Add RAM for larger models
3. **SSD Storage**: Use faster storage for database
4. **GPU Support**: Add GPU for faster embeddings

## 🔐 Security Checklist

- [ ] API keys stored securely
- [ ] HTTPS enabled
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Error messages sanitized
- [ ] Database access restricted
- [ ] Regular security updates
- [ ] Monitoring and alerting setup
