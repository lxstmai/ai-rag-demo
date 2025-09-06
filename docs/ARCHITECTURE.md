# 🏗️ System Architecture

This document describes the architecture of the AI RAG System Demo.

## 📊 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   API Gateway   │    │   RAG Engine    │
│                 │◄──►│                 │◄──►│                 │
│  - HTML/JS UI   │    │  - Flask App    │    │  - Indexer      │
│  - API Calls    │    │  - REST API     │    │  - Retriever    │
│                 │    │  - Error Handle │    │  - LLM Client   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Vector DB     │    │   LLM APIs      │
                       │                 │    │                 │
                       │  - ChromaDB     │    │  - DeepSeek     │
                       │  - Embeddings   │    │  - OpenAI       │
                       │  - Metadata     │    │  - Responses    │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Core Components

### 1. Web Interface (`src/web/app.py`)

**Responsibilities**:
- HTTP request handling
- API endpoint management
- Error handling and logging
- Static file serving

**Key Features**:
- RESTful API design
- CORS support
- JSON request/response handling
- Web interface integration

### 2. Indexer (`src/core/indexer.py`)

**Responsibilities**:
- Website crawling and parsing
- Content extraction and cleaning
- Text chunking with overlap
- Vector embedding generation
- Database storage

**Key Features**:
- Multi-page website indexing
- HTML content extraction
- Smart text chunking
- Metadata preservation
- Error handling for failed requests

### 3. Retriever (`src/core/retriever.py`)

**Responsibilities**:
- Semantic similarity search
- Result ranking and filtering
- Context assembly
- Metadata retrieval

**Key Features**:
- Vector similarity search
- Configurable result limits
- Similarity scoring
- Source attribution

### 4. LLM Client (`src/core/llm_client.py`)

**Responsibilities**:
- LLM API integration
- Prompt engineering
- Response processing
- Error handling

**Key Features**:
- Multiple LLM provider support
- Context-aware prompting
- Response validation
- Fallback mechanisms

### 5. Text Processing (`src/utils/text_processing.py`)

**Responsibilities**:
- Text cleaning and normalization
- HTML parsing and extraction
- Chunking algorithms
- URL validation

**Key Features**:
- BeautifulSoup integration
- Text preprocessing
- Chunk overlap handling
- Special character handling

### 6. Configuration (`src/utils/config.py`)

**Responsibilities**:
- Environment variable management
- Default value handling
- Configuration validation
- Model parameter setup

**Key Features**:
- Environment-based configuration
- Validation and error checking
- Default parameter management
- API key management

## 🔄 Data Flow

### 1. Indexing Flow

```
Website URL → Crawler → HTML Parser → Text Extractor → Chunker → Embedder → Vector DB
     │           │           │             │            │          │           │
     ▼           ▼           ▼             ▼            ▼          ▼           ▼
  Validation  Request    BeautifulSoup  Text Clean   Overlap   Sentence    ChromaDB
              Headers    Parsing       Processing   Chunks    Transformers Storage
```

### 2. Query Flow

```
User Query → Embedder → Vector Search → Result Ranking → Context Assembly → LLM → Response
     │          │            │              │                │              │        │
     ▼          ▼            ▼              ▼                ▼              ▼        ▼
  Input      Sentence    ChromaDB      Similarity       Metadata      DeepSeek   JSON
 Validation  Transformers Query        Scoring         Aggregation    API        Response
```

## 🗄️ Data Storage

### ChromaDB Structure

```
Collection: demo_collection
├── Documents
│   ├── ID: unique_document_id
│   ├── Text: chunked_text_content
│   └── Metadata:
│       ├── url: source_url
│       ├── title: page_title
│       ├── chunk_index: chunk_number
│       └── total_chunks: total_chunks_in_document
└── Embeddings
    └── Vector: 384-dimensional embedding (all-MiniLM-L6-v2)
```

### File System Structure

```
ai_rag_demo/
├── chroma_db/           # ChromaDB persistent storage
│   ├── chroma.sqlite3   # SQLite database
│   └── collections/     # Collection data
├── .env                 # Environment configuration
├── logs/                # Application logs (if configured)
└── temp/                # Temporary files (if any)
```

## 🔌 API Design

### RESTful Endpoints

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/` | Web interface | - | HTML |
| POST | `/api/index` | Index website | URL, max_pages | Index result |
| POST | `/api/query` | RAG query | Query string | Answer + sources |
| POST | `/api/search` | Search only | Query string | Search results |
| GET | `/api/stats` | System stats | - | Statistics |

### Request/Response Format

**Request**:
```json
{
  "url": "https://example.com",
  "max_pages": 10
}
```

**Response**:
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

## �� AI/ML Components

### Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Language**: Multilingual
- **Performance**: Fast inference, good quality

### LLM Integration

- **Primary**: DeepSeek API
- **Fallback**: OpenAI API
- **Prompt Engineering**: Context-aware prompting
- **Response Processing**: JSON parsing and validation

### Text Processing

- **Chunking**: Fixed-size chunks with overlap
- **Preprocessing**: HTML cleaning, text normalization
- **Encoding**: UTF-8 with special character handling

## ⚡ Performance Considerations

### Caching Strategy

- **Model Caching**: Embedding model loaded once
- **Database Caching**: ChromaDB in-memory caching
- **Response Caching**: No current implementation

### Scalability

- **Horizontal**: Multiple app instances with load balancer
- **Vertical**: More CPU/memory for larger datasets
- **Database**: External ChromaDB for shared storage

### Optimization

- **Batch Processing**: Multiple documents at once
- **Async Operations**: Non-blocking I/O where possible
- **Memory Management**: Efficient embedding storage

## 🔒 Security Architecture

### Input Validation

- URL format validation
- Query sanitization
- Size limits on requests
- Content type validation

### API Security

- No authentication (development mode)
- CORS configuration
- Error message sanitization
- Rate limiting (recommended for production)

### Data Privacy

- No user data collection
- Local storage only
- API key protection
- Secure configuration management

## �� Deployment Architecture

### Development

```
Local Machine
├── Python Virtual Environment
├── ChromaDB (local file)
├── Flask Development Server
└── Direct API access
```

### Production

```
Load Balancer (nginx)
├── App Instance 1 (Gunicorn)
├── App Instance 2 (Gunicorn)
├── Shared ChromaDB
├── Redis Cache (optional)
└── Monitoring/Logging
```

## 📊 Monitoring and Observability

### Metrics

- Request count and latency
- Indexing success rate
- Search result quality
- LLM API response times
- Memory and CPU usage

### Logging

- Application logs
- Error tracking
- Performance metrics
- User activity (anonymized)

### Health Checks

- Database connectivity
- LLM API availability
- Model loading status
- System resource usage

## 🔄 Error Handling

### Error Types

1. **Input Errors**: Invalid URLs, malformed requests
2. **Network Errors**: API timeouts, connection failures
3. **Processing Errors**: Parsing failures, encoding issues
4. **Storage Errors**: Database connection, disk space
5. **LLM Errors**: API failures, rate limits

### Error Recovery

- Graceful degradation
- Retry mechanisms
- Fallback responses
- User-friendly error messages

## 🧪 Testing Architecture

### Test Types

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **API Tests**: Endpoint functionality testing
- **Performance Tests**: Load and stress testing

### Test Coverage

- Core functionality
- Error scenarios
- Edge cases
- API contracts

## 🔮 Future Enhancements

### Planned Features

- Multi-language support
- Advanced chunking strategies
- Real-time indexing
- User authentication
- Analytics dashboard
- Multi-modal support

### Architecture Improvements

- Microservices architecture
- Event-driven processing
- Advanced caching layers
- Distributed storage
- Auto-scaling capabilities
