# 📚 API Documentation

Complete API reference for the AI RAG System Demo.

## 🌐 Base URL

```
http://localhost:5000
```

## 📋 Endpoints

### 1. Web Interface

#### GET /

Returns the main web interface.

**Response**: HTML page with the RAG system interface.

---

### 2. Indexing

#### POST /api/index

Index a website for search.

**Request Body**:
```json
{
  "url": "https://example.com",
  "max_pages": 10
}
```

**Parameters**:
- `url` (string, required): Website URL to index
- `max_pages` (integer, optional): Maximum pages to index (default: 10)

**Response**:
```json
{
  "success": true,
  "total_urls": 5,
  "indexed_count": 5,
  "errors": []
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'
```

---

### 3. Query

#### POST /api/query

Search and generate answers using RAG pipeline.

**Request Body**:
```json
{
  "query": "What is artificial intelligence?"
}
```

**Parameters**:
- `query` (string, required): Question to ask

**Response**:
```json
{
  "success": true,
  "query": "What is artificial intelligence?",
  "answer": "Based on the indexed content...",
  "context": "Relevant context from documents...",
  "sources": ["https://example.com"],
  "chunks": [
    {
      "text": "Document text...",
      "similarity": 0.85,
      "rank": 1,
      "metadata": {
        "url": "https://example.com",
        "title": "Page Title",
        "chunk_index": 0,
        "total_chunks": 5
      }
    }
  ],
  "llm_available": true,
  "full_prompt": "Context: ...\n\nQuestion: ..."
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

---

### 4. Search

#### POST /api/search

Search for relevant documents without LLM generation.

**Request Body**:
```json
{
  "query": "machine learning",
  "top_k": 5
}
```

**Parameters**:
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results (default: 5)

**Response**:
```json
{
  "success": true,
  "query": "machine learning",
  "results": [
    {
      "text": "Document text...",
      "similarity": 0.92,
      "metadata": {
        "url": "https://example.com",
        "title": "Page Title"
      }
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3}'
```

---

### 5. Statistics

#### GET /api/stats

Get system statistics and status.

**Response**:
```json
{
  "total_documents": 150,
  "indexed_urls": 5,
  "collection_name": "demo_collection",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "llm_available": true
}
```

**Example**:
```bash
curl http://localhost:5000/api/stats
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `EMBEDDING_MODEL` | Sentence transformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHROMA_DB_PATH` | ChromaDB storage path | `./chroma_db` |
| `CHROMA_COLLECTION_NAME` | Collection name | `demo_collection` |
| `TOP_K_RESULTS` | Default search results | `5` |
| `CHUNK_SIZE` | Text chunk size | `300` |
| `CHUNK_OVERLAP` | Chunk overlap | `50` |
| `FLASK_HOST` | Server host | `0.0.0.0` |
| `FLASK_PORT` | Server port | `5000` |
| `FLASK_DEBUG` | Debug mode | `True` |

---

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 🚨 Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information"
}
```

### Common Errors

1. **Invalid URL**:
```json
{
  "success": false,
  "error": "Invalid URL format"
}
```

2. **API Key Missing**:
```json
{
  "success": false,
  "error": "API key not configured"
}
```

3. **No Documents Found**:
```json
{
  "success": false,
  "error": "No documents in database"
}
```

---

## 🔍 Search Parameters

### Chunking Configuration

- **Chunk Size**: Maximum characters per chunk
- **Overlap**: Characters overlapping between chunks
- **Strategy**: Fixed-size chunks with overlap

### Search Configuration

- **Similarity Threshold**: Minimum similarity score
- **Top K**: Maximum number of results
- **Metadata Filtering**: Filter by URL, title, etc.

---

## 🧪 Testing

### Test API Endpoints

```bash
# Test indexing
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "max_pages": 1}'

# Test query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'

# Test search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test search"}'

# Test stats
curl http://localhost:5000/api/stats
```

### Performance Testing

```bash
# Load test with Apache Bench
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p query.json http://localhost:5000/api/query
```

---

## 📈 Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:

1. **Request Rate Limiting**: Limit requests per IP
2. **API Key Quotas**: Limit usage per API key
3. **Resource Limits**: Limit indexing and query resources

---

## 🔐 Security

### Authentication

Currently no authentication is required. For production:

1. **API Key Authentication**: Require API keys for all requests
2. **JWT Tokens**: Implement token-based authentication
3. **OAuth**: Integrate with OAuth providers

### Input Validation

- URL validation for indexing
- Query sanitization
- Size limits for requests
- Content type validation

---

## 📚 SDK Examples

### Python SDK

```python
import requests

class RAGClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def index_website(self, url, max_pages=10):
        response = requests.post(
            f"{self.base_url}/api/index",
            json={"url": url, "max_pages": max_pages}
        )
        return response.json()
    
    def query(self, question):
        response = requests.post(
            f"{self.base_url}/api/query",
            json={"query": question}
        )
        return response.json()
    
    def search(self, query, top_k=5):
        response = requests.post(
            f"{self.base_url}/api/search",
            json={"query": query, "top_k": top_k}
        )
        return response.json()
    
    def get_stats(self):
        response = requests.get(f"{self.base_url}/api/stats")
        return response.json()

# Usage
client = RAGClient()
result = client.query("What is AI?")
print(result['answer'])
```

### JavaScript SDK

```javascript
class RAGClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async indexWebsite(url, maxPages = 10) {
        const response = await fetch(`${this.baseUrl}/api/index`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, max_pages: maxPages })
        });
        return response.json();
    }
    
    async query(question) {
        const response = await fetch(`${this.baseUrl}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: question })
        });
        return response.json();
    }
    
    async search(query, topK = 5) {
        const response = await fetch(`${this.baseUrl}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: topK })
        });
        return response.json();
    }
    
    async getStats() {
        const response = await fetch(`${this.baseUrl}/api/stats`);
        return response.json();
    }
}

// Usage
const client = new RAGClient();
const result = await client.query('What is AI?');
console.log(result.answer);
```
