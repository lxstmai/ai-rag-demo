"""
Продвинутый пример использования RAG системы
"""
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline

def demonstrate_advanced_features():
    """Демонстрирует продвинутые возможности системы"""
    print("🔬 Продвинутые возможности RAG системы")
    
    # Инициализация (аналогично basic_usage.py)
    from sentence_transformers import SentenceTransformer
    import chromadb
    from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME
    
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    
    retriever = ContextRetriever(embedding_model, chroma_collection)
    
    # 1. Keyword Search
    print("\n🔑 Keyword Search")
    keywords = ["машинное обучение", "нейронные сети", "алгоритмы"]
    keyword_result = retriever.search_by_keywords(keywords, top_k=3)
    print(f"Найдено по ключевым словам: {keyword_result.get('total_found', 0)} результатов")
    
    # 2. Similar Documents Search
    print("\n🔍 Similar Documents Search")
    try:
        # Получаем ID первого документа
        all_docs = chroma_collection.get(limit=1, include=['metadatas'])
        if all_docs['ids']:
            doc_id = all_docs['ids'][0]
            similar_docs = retriever.get_similar_documents(doc_id, top_k=3)
            print(f"Найдено похожих документов: {similar_docs.get('total_found', 0)}")
            
            if similar_docs.get('similar_documents'):
                print("Самый похожий документ:")
                doc = similar_docs['similar_documents'][0]
                print(f"  Схожесть: {doc['similarity']:.2f}")
                print(f"  Текст: {doc['text'][:100]}...")
    except Exception as e:
        print(f"Ошибка поиска похожих документов: {e}")
    
    # 3. Анализ качества поиска
    print("\n📈 Анализ качества поиска")
    test_queries = [
        "Что такое искусственный интеллект?",
        "Как работают нейронные сети?",
        "Применение машинного обучения",
        "Алгоритмы глубокого обучения"
    ]
    
    for query in test_queries:
        result = retriever.find_relevant_context(query, top_k=2)
        if result.get('chunks'):
            avg_similarity = sum(chunk['similarity'] for chunk in result['chunks']) / len(result['chunks'])
            print(f"  '{query}': средняя схожесть {avg_similarity:.2f}")
        else:
            print(f"  '{query}': результаты не найдены")
    
    # 4. Сравнение разных провайдеров LLM
    print("\n🤖 Сравнение LLM провайдеров")
    test_query = "Объясни принципы работы машинного обучения"
    
    # Тестируем DeepSeek (если доступен)
    try:
        deepseek_client = LLMClient("deepseek")
        deepseek_pipeline = RAGPipeline(retriever, deepseek_client)
        deepseek_result = deepseek_pipeline.ask(test_query)
        print(f"DeepSeek ответ: {deepseek_result['answer'][:100]}...")
    except Exception as e:
        print(f"DeepSeek недоступен: {e}")
    
    # Тестируем OpenAI (если доступен)
    try:
        openai_client = LLMClient("openai")
        openai_pipeline = RAGPipeline(retriever, openai_client)
        openai_result = openai_pipeline.ask(test_query)
        print(f"OpenAI ответ: {openai_result['answer'][:100]}...")
    except Exception as e:
        print(f"OpenAI недоступен: {e}")
    
    # 5. Экспорт и анализ данных
    print("\n📊 Экспорт и анализ данных")
    collection_info = retriever.get_collection_info()
    print(f"Общая статистика:")
    print(f"  Всего документов: {collection_info.get('total_documents', 0)}")
    print(f"  Коллекция: {collection_info.get('collection_name', 'unknown')}")
    
    # Получаем все метаданные для анализа
    try:
        all_metadata = chroma_collection.get(include=['metadatas'])
        if all_metadata['metadatas']:
            # Анализируем источники
            sources = {}
            for metadata in all_metadata['metadatas']:
                if 'url' in metadata:
                    url = metadata['url']
                    sources[url] = sources.get(url, 0) + 1
            
            print(f"  Уникальных источников: {len(sources)}")
            print("  Топ-3 источника:")
            for url, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    {url}: {count} фрагментов")
    except Exception as e:
        print(f"Ошибка анализа данных: {e}")

def benchmark_performance():
    """Бенчмарк производительности системы"""
    print("\n⚡ Бенчмарк производительности")
    
    import time
    from sentence_transformers import SentenceTransformer
    import chromadb
    from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME
    
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    retriever = ContextRetriever(embedding_model, chroma_collection)
    
    # Тест скорости поиска
    test_queries = [
        "машинное обучение",
        "нейронные сети",
        "искусственный интеллект",
        "глубокое обучение",
        "алгоритмы"
    ]
    
    total_time = 0
    for query in test_queries:
        start_time = time.time()
        result = retriever.find_relevant_context(query)
        end_time = time.time()
        
        query_time = end_time - start_time
        total_time += query_time
        print(f"  '{query}': {query_time:.3f}с, найдено {result.get('total_found', 0)} результатов")
    
    avg_time = total_time / len(test_queries)
    print(f"Среднее время поиска: {avg_time:.3f}с")

if __name__ == "__main__":
    demonstrate_advanced_features()
    benchmark_performance()
