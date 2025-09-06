"""
Client for working with language models
"""
import requests
import json
from typing import Optional, Tuple
from utils.config import DEEPSEEK_API_KEY, OPENAI_API_KEY


class LLMClient:
    """
    Client for working with various LLM APIs
    """
    
    def __init__(self, provider: str = "deepseek"):
        self.provider = provider.lower()
        self.api_key = None
        
        if self.provider == "deepseek":
            self.api_key = DEEPSEEK_API_KEY
            self.api_url = "https://api.deepseek.com/chat/completions"
        elif self.provider == "openai":
            self.api_key = OPENAI_API_KEY
            self.api_url = "https://api.openai.com/v1/chat/completions"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if not self.api_key:
            raise ValueError(f"API key for {self.provider} is not set")
    
    def generate_answer(self, query: str, context: str, max_tokens: int = 1024) -> Tuple[str, str]:
        """
        Generates an answer based on the query and context
        
        Args:
            query: The user's query
            context: Relevant context
            max_tokens: The maximum number of tokens in the response
            
        Returns:
            tuple: (answer, full prompt)
        """
        system_prompt = self._get_system_prompt()
        user_prompt = self._format_user_prompt(query, context)
        
        try:
            response = self._make_api_request(system_prompt, user_prompt, max_tokens)
            return response, user_prompt
        except Exception as e:
            error_msg = f"Error when calling {self.provider} API: {str(e)}"
            return error_msg, user_prompt
    
    def _get_system_prompt(self) -> str:
        """
        Returns the system prompt
        """
        return (
            "You are a helpful AI assistant that answers user questions "
            "based on the provided context.\n\n"
            "Rules:\n"
            "1. Answer ONLY based on the provided context\n"
            "2. If the context does not contain information to answer, honestly say so\n"
            "3. Be polite and friendly\n"
            "4. Structure the answer if appropriate\n"
            "5. Do not invent information that is not in the context"
        )
    
    def _format_user_prompt(self, query: str, context: str) -> str:
        """
        Formats the user prompt
        """
        return f"""Context:
---
{context}
---

Question: {query}

Please answer the question using only the information from the provided context."""
    
    def _make_api_request(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Executes a request to the API
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.provider == "deepseek":
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": max_tokens,
                "stream": False
            }
        elif self.provider == "openai":
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        response_json = response.json()
        
        if self.provider == "deepseek":
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
        elif self.provider == "openai":
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
        
        return "Sorry, failed to get a response from the AI."
    
    def test_connection(self) -> bool:
        """
        Tests the connection to the API
        """
        try:
            test_prompt = "Hello! This is a test message."
            response, _ = self.generate_answer(test_prompt, "Test context", 50)
            return "error" not in response.lower()
        except Exception:
            return False


class RAGPipeline:
    """
    Full RAG pipeline: context retrieval + answer generation
    """
    
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client
    
    def ask(self, query: str, top_k: int = None) -> dict:
        """
        Executes the full RAG cycle: retrieval + generation
        
        Args:
            query: The user's query
            top_k: The number of relevant chunks to retrieve
            
        Returns:
            dict: A result with the answer and metadata
        """
        # 1. Retrieve relevant context
        context_result = self.retriever.find_relevant_context(query, top_k)
        
        if context_result.get("error"):
            return {
                "answer": f"Search error: {context_result['error']}",
                "context": "",
                "sources": [],
                "chunks": [],
                "success": False
            }
        
        if not context_result.get("context"):
            return {
                "answer": "Sorry, I could not find relevant information to answer your question.",
                "context": "",
                "sources": context_result.get("sources", []),
                "chunks": context_result.get("chunks", []),
                "success": False
            }
        
        # 2. Generate the answer
        answer, full_prompt = self.llm_client.generate_answer(
            query, 
            context_result["context"]
        )
        
        return {
            "answer": answer,
            "context": context_result["context"],
            "sources": context_result.get("sources", []),
            "chunks": context_result.get("chunks", []),
            "full_prompt": full_prompt,
            "success": True,
            "query": query
        }
        
