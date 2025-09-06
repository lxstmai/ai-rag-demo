"""
Tests for the RAG system
"""
import pytest
import sys
import os

# Add the path to the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.indexer import WebsiteIndexer
from core.retriever import ContextRetriever
from core.llm_client import LLMClient, RAGPipeline
from utils.text_processing import clean_text, chunk_text, is_valid_url

class TestTextProcessing:
    """Tests for text processing"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  This   is a test    text  \n\n  with extra   spaces  "
        clean = clean_text(dirty_text)
        assert clean == "This is a test text with extra spaces"
    
    def test_chunk_text(self):
        """Test splitting text into chunks"""
        text = " ".join(["word"] * 100)  # 100 words
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 20 for chunk in chunks)
    
    def test_is_valid_url(self):
        """Test URL validation"""
        assert is_valid_url("https://example.com") == True
        assert is_valid_url("http://localhost:8080") == True
        assert is_valid_url("invalid-url") == False
        assert is_valid_url("") == False

class TestRAGComponents:
    """Tests for RAG system components"""
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model"""
        class MockModel:
            def encode(self, texts, normalize_embeddings=True):
                import numpy as np
                # Return random embeddings
                return np.random.rand(len(texts), 384)
        return MockModel()
    
    @pytest.fixture
    def mock_chroma_collection(self):
        """Mock ChromaDB collection"""
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
                # Return mock results
                return {
                    'documents': [['Test document 1', 'Test document 2']],
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
        """Test context retrieval"""
        retriever = ContextRetriever(mock_embedding_model, mock_chroma_collection)
        
        result = retriever.find_relevant_context("test query")
        
        assert 'context' in result
        assert 'chunks' in result
        assert 'sources' in result
        assert result['total_found'] == 2
    
    def test_rag_pipeline(self, mock_embedding_model, mock_chroma_collection):
        """Test RAG pipeline"""
        retriever = ContextRetriever(mock_embedding_model, mock_chroma_collection)
        
        # Mock LLM client
        class MockLLMClient:
            def generate_answer(self, query, context, max_tokens=1024):
                return "Test answer", "Test prompt"
        
        llm_client = MockLLMClient()
        pipeline = RAGPipeline(retriever, llm_client)
        
        result = pipeline.ask("test question")
        
        assert result['success'] == True
        assert result['answer'] == "Test answer"
        assert 'sources' in result

class TestIntegration:
    """Integration tests"""
    
    def test_system_initialization(self):
        """Test system initialization"""
        # Check that modules are imported without errors
        from utils.config import EMBEDDING_MODEL, CHROMA_DB_PATH
        assert EMBEDDING_MODEL is not None
        assert CHROMA_DB_PATH is not None
    
    def test_web_app_import(self):
        """Test web application import"""
        try:
            from web.app import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"Web application is unavailable: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
    
