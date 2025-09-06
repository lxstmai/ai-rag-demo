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
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")
        
        if not self.api_key:
            raise ValueError(f"API ключ для {self.provider} не установлен")
    
    def generate_answer(self, query: str, context: str, max_tokens: int = 1024) -> Tuple[str, str]:
        """
        Генерирует ответ на основе запроса и контекста
        
        Args:
            query: Пользовательский запрос
            context: Релевантный контекст
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            tuple: (ответ, полный промпт)
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
        Возвращает системный промпт
        """
        return (
            "Ты — полезный AI-ассистент, который отвечает на вопросы пользователей "
            "на основе предоставленного контекста.\n\n"
            "Правила:\n"
            "1. Отвечай ТОЛЬКО на основе предоставленного контекста\n"
            "2. Если в контексте нет информации для ответа, честно скажи об этом\n"
            "3. Будь вежливым и дружелюбным\n"
            "4. Структурируй ответ, если это уместно\n"
            "5. Не придумывай информацию, которой нет в контексте"
        )
    
    def _format_user_prompt(self, query: str, context: str) -> str:
        """
        Форматирует пользовательский промпт
        """
        return f"""Контекст:
---
{context}
---

Вопрос: {query}

Пожалуйста, ответь на вопрос, используя только информацию из предоставленного контекста."""
    
    def _make_api_request(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Выполняет запрос к API
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
        
        return "Извините, не удалось получить ответ от AI."
    
    def test_connection(self) -> bool:
        """
        Тестирует подключение к API
        """
        try:
            test_prompt = "Привет! Это тестовое сообщение."
            response, _ = self.generate_answer(test_prompt, "Тестовый контекст", 50)
            return "error" not in response.lower()
        except Exception:
            return False


class RAGPipeline:
    """
    Полный пайплайн RAG: поиск контекста + генерация ответа
    """
    
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client
    
    def ask(self, query: str, top_k: int = None) -> dict:
        """
        Выполняет полный цикл RAG: поиск + генерация
        
        Args:
            query: Пользовательский запрос
            top_k: Количество релевантных чанков для поиска
            
        Returns:
            dict: Результат с ответом и метаданными
        """
        # 1. Поиск релевантного контекста
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
                "answer": "Извините, не удалось найти релевантную информацию для ответа на ваш вопрос.",
                "context": "",
                "sources": context_result.get("sources", []),
                "chunks": context_result.get("chunks", []),
                "success": False
            }
        
        # 2. Генерация ответа
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
