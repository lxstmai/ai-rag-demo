"""
Поиск релевантного контекста для RAG системы
"""
from typing import List, Dict, Any
from utils.config import TOP_K_RESULTS


class ContextRetriever:
    """
    Класс для поиска релевантного контекста по запросу
    """
    
    def __init__(self, embedding_model, chroma_collection):
        self.embedding_model = embedding_model
        self.chroma_collection = chroma_collection
    
    def find_relevant_context(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Находит релевантный контекст для запроса
        
        Args:
            query: Поисковый запрос
            top_k: Количество результатов для возврата
            
        Returns:
            dict: Релевантный контекст и метаданные
        """
        if not query or not query.strip():
            return {
                "context": "",
                "chunks": [],
                "sources": [],
                "error": "Пустой запрос"
            }
        
        if top_k is None:
            top_k = TOP_K_RESULTS
        
        try:
            # Create embedding for query
            query_embedding = self.embedding_model.encode(
                [query], 
                normalize_embeddings=True
            )[0]
            
            # Search for similar documents
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            chunks = []
            sources = set()
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Calculate similarity (1 - distance)
                similarity = 1 - distance if distance is not None else 0
                
                chunk_info = {
                    "text": doc,
                    "metadata": metadata,
                    "similarity": similarity,
                    "rank": i + 1
                }
                chunks.append(chunk_info)
                
                # Collect sources
                if 'url' in metadata:
                    sources.add(metadata['url'])
            
            # Form context for LLM
            context_parts = []
            for chunk in chunks:
                title = chunk['metadata'].get('title', 'Без заголовка')
                text = chunk['text']
                context_parts.append(f"[{title}]\n{text}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            return {
                "context": context,
                "chunks": chunks,
                "sources": list(sources),
                "total_found": len(chunks),
                "query": query
            }
            
        except Exception as e:
            return {
                "context": "",
                "chunks": [],
                "sources": [],
                "error": f"Search error: {str(e)}"
            }
    
    def search_by_keywords(self, keywords: List[str], top_k: int = None) -> Dict[str, Any]:
        """
        Поиск по ключевым словам
        
        Args:
            keywords: Список ключевых слов
            top_k: Количество результатов
            
        Returns:
            dict: Результаты поиска
        """
        if not keywords:
            return {"error": "Не указаны ключевые слова"}
        
        # Combine keywords into query
        query = " ".join(keywords)
        return self.find_relevant_context(query, top_k)
    
    def get_similar_documents(self, document_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Находит документы, похожие на указанный
        
        Args:
            document_id: ID документа
            top_k: Количество похожих документов
            
        Returns:
            dict: Похожие документы
        """
        try:
            # Get document by ID
            results = self.chroma_collection.get(
                ids=[document_id],
                include=['documents', 'embeddings', 'metadatas']
            )
            
            if not results['documents']:
                return {"error": "Документ не найден"}
            
            # Search for similar documents
            similar_results = self.chroma_collection.query(
                query_embeddings=results['embeddings'],
                n_results=top_k + 1,  # +1 потому что сам документ тоже будет в результатах
                include=['documents', 'metadatas', 'distances']
            )
            
            # Filter original document
            documents = similar_results['documents'][0][1:]  # Skip first (original)
            metadatas = similar_results['metadatas'][0][1:]
            distances = similar_results['distances'][0][1:]
            
            similar_docs = []
            for doc, metadata, distance in zip(documents, metadatas, distances):
                similarity = 1 - distance if distance is not None else 0
                similar_docs.append({
                    "text": doc,
                    "metadata": metadata,
                    "similarity": similarity
                })
            
            return {
                "similar_documents": similar_docs,
                "total_found": len(similar_docs)
            }
            
        except Exception as e:
            return {"error": f"Error searching similar documents: {str(e)}"}
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о коллекции
        """
        try:
            count = self.chroma_collection.count()
            
            # Get several document examples
            sample_results = self.chroma_collection.get(
                limit=5,
                include=['metadatas']
            )
            
            sample_urls = []
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    if 'url' in metadata:
                        sample_urls.append(metadata['url'])
            
            return {
                "total_documents": count,
                "sample_urls": sample_urls,
                "collection_name": self.chroma_collection.name
            }
            
        except Exception as e:
            return {"error": f"Error getting information: {str(e)}"}
