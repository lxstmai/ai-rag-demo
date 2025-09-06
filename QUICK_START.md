# 🚀 Quick Start Guide

This guide will help you quickly set up and run the AI RAG System Demo.

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

## ⚡ Quick Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai_rag_demo
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run Demo

```bash
python run_demo.py
```

The system will:
1. Load embedding models
2. Initialize ChromaDB
3. Start the web server
4. Open http://localhost:5000 in your browser

## 🌐 Web Interface

Once running, you can:

1. **Index Websites**: Add websites to the knowledge base
2. **Search**: Ask questions about indexed content
3. **View Statistics**: Monitor system performance

## 📖 API Examples

### Index a Website

```bash
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'
```

### Query the System

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

### Get System Statistics

```bash
curl http://localhost:5000/api/stats
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python -m pytest tests/ -v
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Error**: Make sure virtual environment is activated
2. **API Key Error**: Verify your API keys in .env file
3. **Port Already in Use**: Change FLASK_PORT in .env file

### Logs

Check the console output for detailed error messages.

## 📚 Next Steps

- Read [API Documentation](docs/API.md) for detailed API usage
- Check [Architecture Overview](docs/ARCHITECTURE.md) to understand the system
- See [Deployment Guide](DEPLOYMENT.md) for production setup

## 🆘 Need Help?

- Check the [troubleshooting section](DEPLOYMENT.md#troubleshooting)
- Review the [FAQ section](README.md#faq)
- Create an issue on GitHub
