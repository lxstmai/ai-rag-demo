# 🤖 AI RAG System Demo

A demonstration project of a RAG (Retrieval-Augmented Generation) system for creating AI assistants based on web content.

## ✨ Features

- **🌐 Website Indexing**: Automatic parsing and extraction of text content
- **🔍 Semantic Search**: Search for relevant information using vector embeddings
- **🤖 AI Assistant**: Generate answers based on found context
- **🌐 Web Interface**: Intuitive API and web interface for interaction
- **📊 Monitoring**: System statistics and search quality

## 🏗️ Architecture

```
src/
├── core/              # Core system logic
│   ├── indexer.py     # Website indexing and parsing
│   ├── retriever.py   # Relevant context search
│   └── llm_client.py  # LLM integration (DeepSeek/OpenAI)
├── web/               # Web interface
│   └── app.py         # Flask application with API
└── utils/             # Utility functions
    ├── text_processing.py
    └── config.py
```

## 🛠️ Technologies

- **Python 3.8+**
- **Flask** - web framework
- **ChromaDB** - vector database
- **Sentence Transformers** - embedding models
- **BeautifulSoup** - HTML parsing
- **Requests** - HTTP client

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai_rag_demo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env file and add your API keys
# DEEPSEEK_API_KEY=your_deepseek_api_key
# OPENAI_API_KEY=your_openai_api_key
```

### 4. Run Demo

```bash
# Start the demo
python run_demo.py
```

Open your browser: http://localhost:5000

## 📖 Usage Examples

### Basic Usage

```python
from src.core.indexer import WebsiteIndexer
from src.core.retriever import ContextRetriever
from src.core.llm_client import RAGPipeline

# Initialize components
indexer = WebsiteIndexer(embedding_model, chroma_collection)
retriever = ContextRetriever(embedding_model, chroma_collection)
rag_pipeline = RAGPipeline(retriever, llm_client)

# Index a website
result = indexer.index_website("https://example.com", max_pages=5)

# Search and generate answer
response = rag_pipeline.query("What is this website about?")
print(response['answer'])
```

### API Usage

```bash
# Index a website
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'

# Query the system
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/ -v
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - detailed setup instructions
- [API Documentation](docs/API.md) - complete API reference
- [Architecture Overview](docs/ARCHITECTURE.md) - system architecture
- [Deployment Guide](DEPLOYMENT.md) - production deployment

## 🔧 Configuration

### Environment Variables

- `DEEPSEEK_API_KEY` - DeepSeek API key
- `OPENAI_API_KEY` - OpenAI API key
- `EMBEDDING_MODEL` - Sentence transformer model
- `CHROMA_DB_PATH` - ChromaDB storage path
- `CHUNK_SIZE` - Text chunk size for indexing
- `TOP_K_RESULTS` - Number of search results

### Model Configuration

The system uses `sentence-transformers/all-MiniLM-L6-v2` by default for embeddings. You can change this in the configuration.

## 🚀 Deployment

### Local Development

```bash
python run_demo.py
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the [troubleshooting guide](DEPLOYMENT.md#troubleshooting)
2. Review the logs
3. Create an issue on GitHub

## 🙏 Acknowledgments

- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) for embeddings
- [Flask](https://flask.palletsprojects.com/) for the web framework
