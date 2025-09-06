"""
Advanced example of using a RAG system
"""
import sys
import os

# Add the path to the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline

def demonstrate_advanced_features():
    """Demonstrates the advanced features of the system"""
    print("🔬 Advanced features of the RAG system")
    
    # Initialization (similar to basic_usage.py)
    from sentence_transformers import SentenceTransformer
    import chromadb
    from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME
    
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    
    retriever = ContextRetriever(embedding_model, chroma_collection)
    
    # 1. Keyword Search
    print("\n🔑 Keyword Search")
    keywords = ["machine learning", "neural networks", "algorithms"]
    keyword_result = retriever.search_by_keywords(keywords, top_k=3)
    print(f"Found by keywords: {keyword_result.get('total_found', 0)} results")
    
    # 2. Similar Documents Search
    print("\n🔍 Similar Documents Search")
    try:
        # Get the ID of the first document
        all_docs = chroma_collection.get(limit=1, include=['metadatas'])
        if all_docs['ids']:
            doc_id = all_docs['ids'][0]
            similar_docs = retriever.get_similar_documents(doc_id, top_k=3)
            print(f"Found similar documents: {similar_docs.get('total_found', 0)}")
            
            if similar_docs.get('similar_documents'):
                print("Most similar document:")
                doc = similar_docs['similar_documents'][0]
                print(f"  Similarity: {doc['similarity']:.2f}")
                print(f"  Text: {doc['text'][:100]}...")
    except Exception as e:
        print(f"Error searching for similar documents: {e}")
    
    # 3. Search Quality Analysis
    print("\n📈 Search Quality Analysis")
    test_queries = [
        "What is artificial intelligence?",
        "How do neural networks work?",
        "Application of machine learning",
        "Deep learning algorithms"
    ]
    
    for query in test_queries:
        result = retriever.find_relevant_context(query, top_k=2)
        if result.get('chunks'):
            avg_similarity = sum(chunk['similarity'] for chunk in result['chunks']) / len(result['chunks'])
            print(f"  '{query}': average similarity {avg_similarity:.2f}")
        else:
            print(f"  '{query}': results not found")
    
    # 4. Comparison of different LLM providers
    print("\n🤖 Comparison of LLM providers")
    test_query = "Explain the principles of machine learning"
    
    # Testing DeepSeek (if available)
    try:
        deepseek_client = LLMClient("deepseek")
        deepseek_pipeline = RAGPipeline(retriever, deepseek_client)
        deepseek_result = deepseek_pipeline.ask(test_query)
        print(f"DeepSeek response: {deepseek_result['answer'][:100]}...")
    except Exception as e:
        print(f"DeepSeek is unavailable: {e}")
    
    # Testing OpenAI (if available)
    try:
        openai_client = LLMClient("openai")
        openai_pipeline = RAGPipeline(retriever, openai_client)
        openai_result = openai_pipeline.ask(test_query)
        print(f"OpenAI response: {openai_result['answer'][:100]}...")
    except Exception as e:
        print(f"OpenAI is unavailable: {e}")
    
    # 5. Data Export and Analysis
    print("\n📊 Data Export and Analysis")
    collection_info = retriever.get_collection_info()
    print(f"General statistics:")
    print(f"  Total documents: {collection_info.get('total_documents', 0)}")
    print(f"  Collection: {collection_info.get('collection_name', 'unknown')}")
    
    # Get all metadata for analysis
    try:
        all_metadata = chroma_collection.get(include=['metadatas'])
        if all_metadata['metadatas']:
            # Analyze sources
            sources = {}
            for metadata in all_metadata['metadatas']:
                if 'url' in metadata:
                    url = metadata['url']
                    sources[url] = sources.get(url, 0) + 1
            
            print(f"  Unique sources: {len(sources)}")
            print("  Top-3 sources:")
            for url, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    {url}: {count} fragments")
    except Exception as e:
        print(f"Error in data analysis: {e}")

def benchmark_performance():
    """System performance benchmark"""
    print("\n⚡ Performance Benchmark")
    
    import time
    from sentence_transformers import SentenceTransformer
    import chromadb
    from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME
    
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    retriever = ContextRetriever(embedding_model, chroma_collection)
    
    # Search speed test
    test_queries = [
        "machine learning",
        "neural networks",
        "artificial intelligence",
        "deep learning",
        "algorithms"
    ]
    
    total_time = 0
    for query in test_queries:
        start_time = time.time()
        result = retriever.find_relevant_context(query)
        end_time = time.time()
        
        query_time = end_time - start_time
        total_time += query_time
        print(f"  '{query}': {query_time:.3f}s, found {result.get('total_found', 0)} results")
    
    avg_time = total_time / len(test_queries)
    print(f"Average search time: {avg_time:.3f}s")

if __name__ == "__main__":
    demonstrate_advanced_features()
    benchmark_performance()
