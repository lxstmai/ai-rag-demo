"""
Flask application for RAG system
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# add path to modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline
from utils.config import (
    EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME,
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG
)

# model initialization
print("🔄 Загружаем модели...")
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    
    # load embedding model
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"✅ Embedding model loaded: {EMBEDDING_MODEL}")
    
    # initialize ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME
    )
    print(f"✅ ChromaDB collection ready: {CHROMA_COLLECTION_NAME}")
    
except Exception as e:
    print(f"❌ Initialization error: {e}")
    sys.exit(1)

# create Flask application
app = Flask(__name__)
CORS(app)

# initialize system components
indexer = WebsiteIndexer(embedding_model, chroma_collection)
retriever = ContextRetriever(embedding_model, chroma_collection)

# try to initialize LLM client
try:
    llm_client = LLMClient("deepseek")
    rag_pipeline = RAGPipeline(retriever, llm_client)
    llm_available = True
    print("✅ LLM client initialized")
except Exception as e:
    print(f"⚠️ LLM недоступен: {e}")
    llm_client = None
    rag_pipeline = None
    llm_available = False

# HTML шаблон для веб-интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI RAG System Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .section { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        .section h2 { margin-top: 0; color: #333; }
        input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result { background: white; padding: 15px; border-radius: 4px; margin-top: 10px; }
        .error { background: #f8d7da; color: #721c24; }
        .success { background: #d4edda; color: #155724; }
        .loading { color: #007bff; }
        .source { font-size: 0.9em; color: #666; margin-top: 10px; }
        .chunk { background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .similarity { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <h1>🤖 AI RAG System Demo</h1>
    <p>Демонстрация системы RAG (Retrieval-Augmented Generation) для создания AI-ассистентов</p>
    
    <div class="container">
        <div class="section">
            <h2>📄 Website Indexing</h2>
            <input type="url" id="websiteUrl" placeholder="https://example.com" />
            <input type="number" id="maxPages" placeholder="Максимум страниц (по умолчанию: 10)" value="10" />
            <button onclick="indexWebsite()">Индексировать сайт</button>
            <div id="indexResult"></div>
        </div>
        
        <div class="section">
            <h2>🔍 Search and Answer</h2>
            <textarea id="query" placeholder="Ваш вопрос..." rows="3"></textarea>
            <button onclick="askQuestion()" id="askBtn">Задать вопрос</button>
            <div id="queryResult"></div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 System Statistics</h2>
        <button onclick="getStats()">Обновить статистику</button>
        <div id="statsResult"></div>
    </div>

    <script>
        async function indexWebsite() {
            const url = document.getElementById('websiteUrl').value;
            const maxPages = document.getElementById('maxPages').value || 10;
            const resultDiv = document.getElementById('indexResult');
            
            if (!url) {
                resultDiv.innerHTML = '<div class="result error">Введите URL сайта</div>';
                return;
            }
            
            resultDiv.innerHTML = '<div class="result loading">🔄 Indexing website...</div>';
            
            try {
                const response = await fetch('/api/index', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, max_pages: parseInt(maxPages) })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <div class="result success">
                            ✅ Indexing completed!<br>
                            Проиндексировано: ${data.indexed_count}/${data.total_urls} страниц<br>
                            ${data.errors.length > 0 ? 'Ошибки: ' + data.errors.length : ''}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="result error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        }
        
        async function askQuestion() {
            const query = document.getElementById('query').value;
            const resultDiv = document.getElementById('queryResult');
            const askBtn = document.getElementById('askBtn');
            
            if (!query) {
                resultDiv.innerHTML = '<div class="result error">Введите вопрос</div>';
                return;
            }
            
            askBtn.disabled = true;
            askBtn.textContent = 'Обрабатываем...';
            resultDiv.innerHTML = '<div class="result loading">🔄 Searching for answer...</div>';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    let sourcesHtml = '';
                    if (data.sources && data.sources.length > 0) {
                        sourcesHtml = `<div class="source"><strong>Источники:</strong><br>${data.sources.map(s => `<a href="${s}" target="_blank">${s}</a>`).join('<br>')}</div>`;
                    }
                    
                    let chunksHtml = '';
                    if (data.chunks && data.chunks.length > 0) {
                        chunksHtml = '<div class="source"><strong>Найденные фрагменты:</strong></div>';
                        data.chunks.forEach(chunk => {
                            chunksHtml += `
                                <div class="chunk">
                                    <div class="similarity">Схожесть: ${(chunk.similarity * 100).toFixed(1)}%</div>
                                    <div>${chunk.text.substring(0, 200)}...</div>
                                </div>
                            `;
                        });
                    }
                    
                    resultDiv.innerHTML = `
                        <div class="result success">
                            <strong>Answer:</strong><br>
                            ${data.answer}<br>
                            ${sourcesHtml}
                            ${chunksHtml}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="result error">❌ ${data.answer}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            } finally {
                askBtn.disabled = false;
                askBtn.textContent = 'Задать вопрос';
            }
        }
        
        async function getStats() {
            const resultDiv = document.getElementById('statsResult');
            resultDiv.innerHTML = '<div class="result loading">🔄 Загружаем статистику...</div>';
            
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                resultDiv.innerHTML = `
                    <div class="result success">
                        <strong>System Statistics:</strong><br>
                        📄 Всего документов: ${data.total_documents}<br>
                        �� Проиндексированных URL: ${data.indexed_urls}<br>
                        🤖 LLM доступен: ${data.llm_available ? '✅ Да' : '❌ Нет'}<br>
                        📚 Collection: ${data.collection_name}
                    </div>
                `;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        }
        
        // Загружаем статистику при загрузке страницы
        window.onload = getStats;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница с веб-интерфейсом"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/index', methods=['POST'])
def api_index():
    """API для индексации веб-сайта"""
    try:
        data = request.get_json()
        url = data.get('url')
        max_pages = data.get('max_pages', 10)
        
        if not url:
            return jsonify({"error": "URL не указан"}), 400
        
        result = indexer.index_website(url, max_pages)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def api_query():
    """API for search and answer generation"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "Query not specified"}), 400
        
        if not llm_available:
            # If LLM unavailable, return only search results
            context_result = retriever.find_relevant_context(query)
            return jsonify({
                "answer": "LLM недоступен. Вот найденная информация:",
                "context": context_result.get("context", ""),
                "sources": context_result.get("sources", []),
                "chunks": context_result.get("chunks", []),
                "success": True,
                "llm_available": False
            })
        
        # Use full RAG pipeline
        result = rag_pipeline.ask(query)
        result["llm_available"] = True
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API для получения статистики системы"""
    try:
        collection_info = retriever.get_collection_info()
        
        return jsonify({
            "total_documents": collection_info.get("total_documents", 0),
            "indexed_urls": len(collection_info.get("sample_urls", [])),
            "llm_available": llm_available,
            "collection_name": collection_info.get("collection_name", "unknown"),
            "embedding_model": EMBEDDING_MODEL
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def api_search():
    """API for search without answer generation"""
    try:
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({"error": "Query not specified"}), 400
        
        result = retriever.find_relevant_context(query, top_k)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"🚀 Запускаем сервер на {FLASK_HOST}:{FLASK_PORT}")
    print(f"🌐 Откройте браузер: http://localhost:{FLASK_PORT}")
    print(f"📚 Embedding model: {EMBEDDING_MODEL}")
    print(f"🤖 LLM доступен: {'✅ Да' if llm_available else '❌ Нет'}")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )
