"""
Тесты для RAG системы
"""
import pytest
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline
from utils.text_processing import clean_text, chunk_text, is_valid_url

class TestTextProcessing:
    """Тесты для обработки текста"""
    
    def test_clean_text(self):
        """Тест очистки текста"""
        dirty_text = "  Это   тестовый    текст  \n\n  с лишними   пробелами  "
        clean = clean_text(dirty_text)
        assert clean == "Это тестовый текст с лишними пробелами"
    
    def test_chunk_text(self):
        """Тест разбивки текста на чанки"""
        text = " ".join(["слово"] * 100)  # 100 слов
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 20 for chunk in chunks)
    
    def test_is_valid_url(self):
        """Тест валидации URL"""
        assert is_valid_url("https://example.com") == True
        assert is_valid_url("http://localhost:8080") == True
        assert is_valid_url("invalid-url") == False
        assert is_valid_url("") == False

class TestRAGComponents:
    """Тесты для компонентов RAG системы"""
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Мок модель эмбеддингов"""
        class MockModel:
            def encode(self, texts, normalize_embeddings=True):
                import numpy as np
                # Возвращаем случайные эмбеддинги
                return np.random.rand(len(texts), 384)
        return MockModel()
    
    @pytest.fixture
    def mock_chroma_collection(self):
        """Мок ChromaDB коллекция"""
        class MockCollection:
            def __init__(self):
                self.data = []
                self.name = "test_collection"
            
            def add(self, embeddings, documents, metadatas, ids):
                for i, (emb, doc, meta, id_) in enumerate(zip(embeddings, documents, metadatas, ids)):
                    self.data.append({
                        'embedding': emb,
                        'document': doc,
                        'metadata': meta,
                        'id': id_
                    })
            
            def query(self, query_embeddings, n_results, include):
                # Возвращаем мок результаты
                return {
                    'documents': [['Тестовый документ 1', 'Тестовый документ 2']],
                    'metadatas': [[{'url': 'https://test.com'}, {'url': 'https://test2.com'}]],
                    'distances': [[0.1, 0.2]]
                }
            
            def count(self):
                return len(self.data)
            
            def get(self, **kwargs):
                return {
                    'metadatas': [{'url': 'https://test.com'}],
                    'ids': ['test_id']
                }
        
        return MockCollection()
    
    def test_context_retriever(self, mock_embedding_model, mock_chroma_collection):
        """Тест поиска контекста"""
        retriever = ContextRetriever(mock_embedding_model, mock_chroma_collection)
        
        result = retriever.find_relevant_context("тестовый запрос")
        
        assert 'context' in result
        assert 'chunks' in result
        assert 'sources' in result
        assert result['total_found'] == 2
    
    def test_rag_pipeline(self, mock_embedding_model, mock_chroma_collection):
        """Тест RAG пайплайна"""
        retriever = ContextRetriever(mock_embedding_model, mock_chroma_collection)
        
        # Мок LLM клиент
        class MockLLMClient:
            def generate_answer(self, query, context, max_tokens=1024):
                return "Тестовый ответ", "Тестовый промпт"
        
        llm_client = MockLLMClient()
        pipeline = RAGPipeline(retriever, llm_client)
        
        result = pipeline.ask("тестовый вопрос")
        
        assert result['success'] == True
        assert result['answer'] == "Тестовый ответ"
        assert 'sources' in result

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_system_initialization(self):
        """Тест инициализации системы"""
        # Проверяем, что модули импортируются без ошибок
        from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH
        assert EMBEDDING_MODEL is not None
        assert CHROMA_DB_PATH is not None
    
    def test_web_app_import(self):
        """Тест импорта веб-приложения"""
        try:
            from web.app import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"Веб-приложение недоступно: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
