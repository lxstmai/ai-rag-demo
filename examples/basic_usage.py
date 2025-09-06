"""
Базовый пример использования RAG системы
"""
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline
from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME

def main():
    print("🚀 RAG System Demo")
    
    # Инициализация компонентов
    print("📦 Loading models...")
    from sentence_transformers import SentenceTransformer
    import chromadb
    
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    
    # Создаем компоненты системы
    indexer = WebsiteIndexer(embedding_model, chroma_collection)
    retriever = ContextRetriever(embedding_model, chroma_collection)
    
    # Example 1: Website Indexing
    print("\n📄 Example 1: Website Indexing")
    website_url = "https://example.com"  # Замените на реальный сайт
    result = indexer.index_website(website_url, max_pages=3)
    print(f"Indexing result: {result}")
    
    # Example 2: Context Search
    print("\n🔍 Example 2: Relevant Context Search")
    query = "Что такое искусственный интеллект?"
    context_result = retriever.find_relevant_context(query)
    print(f"Found .* relevant fragments")
    
    if context_result.get('chunks'):
        print("First fragment:")
        print(f"  Text: {context_result['chunks'][0]['text'][:100]}...")
        print(f"  Similarity: {context_result['chunks'][0]['similarity']:.2f}")
    
    # Example 3: Full RAG Pipeline (если LLM доступен)
    print("\n🤖 Example 3: Full RAG Pipeline")
    try:
        llm_client = LLMClient("deepseek")
        rag_pipeline = RAGPipeline(retriever, llm_client)
        
        answer_result = rag_pipeline.ask(query)
        print(f"Answer: {answer_result['answer']}")
        print(f"Sources: {answer_result['sources']}")
        
    except Exception as e:
        print(f"LLM недоступен: {e}")
        print("Для использования LLM установите API ключ в .env файле")
    
    # Example 4: System Statistics
    print("\n📊 Example 4: System Statistics")
    stats = retriever.get_collection_info()
    print(f"Total documents: {stats.get('total_documents', 0)}")
    print(f"URL examples: {stats.get('sample_urls', [])}")

if __name__ == "__main__":
    main()
