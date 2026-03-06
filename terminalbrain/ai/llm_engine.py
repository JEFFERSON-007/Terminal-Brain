"""
LLM inference engine for Terminal Brain
"""

import asyncio
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import json


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if backend is available"""
        pass


class OllamaBackend(LLMBackend):
    """Ollama local LLM backend"""

    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            import ollama

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": temperature},
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error: {str(e)}"

    async def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            import ollama

            # Try to list models
            models = ollama.list()
            return True
        except Exception:
            return False


class OpenAIBackend(LLMBackend):
    """OpenAI API backend"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            import openai

            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Linux command expert. Provide concise, accurate terminal commands.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    async def is_available(self) -> bool:
        """Check if API key is valid"""
        try:
            import openai

            openai.api_key = self.api_key
            openai.Model.list()
            return True
        except Exception:
            return False


class LocalMLBackend(LLMBackend):
    """Local machine learning model backend"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using local model"""
        # This would integrate with locally loaded models
        return "Local ML not yet implemented"

    async def is_available(self) -> bool:
        """Check if local model is available"""
        return self.model is not None


class LLMEngine:
    """Unified LLM engine supporting multiple backends"""

    def __init__(self, backend_type: str = "ollama", **kwargs):
        self.backend_type = backend_type
        self.backend: Optional[LLMBackend] = None

        if backend_type == "ollama":
            self.backend = OllamaBackend(
                model=kwargs.get("model", "mistral"),
                base_url=kwargs.get("base_url", "http://localhost:11434"),
            )
        elif backend_type == "openai":
            self.backend = OpenAIBackend(
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "gpt-3.5-turbo"),
            )
        elif backend_type == "local":
            self.backend = LocalMLBackend(model_path=kwargs.get("model_path"))

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response"""
        if not self.backend:
            return "No backend configured"

        return await self.backend.generate(prompt, **kwargs)

    async def is_available(self) -> bool:
        """Check if LLM backend is available"""
        if not self.backend:
            return False
        return await self.backend.is_available()

    async def generate_command(self, description: str, **kwargs) -> str:
        """Generate Linux command from description"""
        prompt = f"""Generate a Linux command for the following task:

Task: {description}

Respond with ONLY the command, no explanation."""

        return await self.generate(prompt, **kwargs)

    async def explain_command(self, command: str, **kwargs) -> str:
        """Explain what a command does"""
        prompt = f"""Explain this Linux command in simple terms:

Command: {command}

Provide a brief, clear explanation."""

        return await self.generate(prompt, **kwargs)

    async def fix_command(self, broken_command: str, error: str, **kwargs) -> str:
        """Suggest fixes for a broken command"""
        prompt = f"""Fix this Linux command that produced an error:

Original command: {broken_command}
Error: {error}

Suggest the corrected command."""

        return await self.generate(prompt, **kwargs)

    async def generate_script(self, description: str, **kwargs) -> str:
        """Generate a shell script from description"""
        prompt = f"""Generate a bash script for the following task:

Task: {description}

Return only the script code, starting with #!/bin/bash"""

        return await self.generate(prompt, **kwargs)

    async def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Generate responses for multiple prompts"""
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
