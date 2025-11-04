"""
LLM service for chatbot functionality
"""
import json
from typing import Dict, List, Optional, AsyncIterator
from groq import Groq, AsyncGroq
from django.conf import settings
import asyncio

# Initialize Groq clients
groq_client = Groq(api_key=settings.GROQ_API_KEY)
async_groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        self.model = model
        self.max_tokens = 2000
        self.temperature = 0.7
    
    def generate_response(
        self, 
        messages: List[Dict], 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated response text
        """
        # Build message list
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        try:
            response = groq_client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def generate_response_async(
        self, 
        messages: List[Dict], 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Async version of generate_response
        """
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        try:
            response = await async_groq_client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Async LLM generation failed: {str(e)}")
    
    async def generate_streaming_response(
        self,
        messages: List[Dict],
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the LLM
        
        Args:
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Yields:
            Response chunks as they arrive
        """
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        try:
            stream = await async_groq_client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response
        
        Args:
            text: LLM response text that may contain JSON
            
        Returns:
            Parsed JSON dict or None
        """
        # Try to find JSON in the text
        import re
        
        # Look for JSON between ```json and ```
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON-like structure
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def truncate_messages(self, messages: List[Dict], max_tokens: int = 3000) -> List[Dict]:
        """
        Truncate message history to fit within token limit
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens allowed
            
        Returns:
            Truncated message list
        """
        total_tokens = 0
        truncated_messages = []
        
        # Start from the most recent messages
        for message in reversed(messages):
            message_tokens = self.count_tokens(message['content'])
            
            if total_tokens + message_tokens > max_tokens:
                break
                
            truncated_messages.insert(0, message)
            total_tokens += message_tokens
        
        return truncated_messages
