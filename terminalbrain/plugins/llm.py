"""Optional LLM module for Terminal Brain.

Provides local LLM support via Ollama and llama.cpp.
Install with: terminal-brain install llm

"""


def init():
    """Initialize LLM module."""
    return {
        "name": "llm",
        "backends": ["ollama", "llamacpp"],
        "description": "Local LLM inference for Terminal Brain",
    }


class OllamaBackend:
    """Ollama local LLM backend."""
    
    def __init__(self, model: str = "mistral", api_base: str = "http://localhost:11434"):
        self.model = model
        self.api_base = api_base
    
    async def infer(self, prompt: str) -> str:
        """Run inference on local model."""
        try:
            import ollama
            response = ollama.generate(model=self.model, prompt=prompt)
            return response["response"]
        except ImportError:
            raise RuntimeError("ollama package not installed. Run: terminal-brain install llm")
        except Exception as e:
            raise RuntimeError(f"Ollama inference failed: {e}")


class LlamaCppBackend:
    """llama.cpp local LLM backend."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
    
    async def infer(self, prompt: str) -> str:
        """Run inference using llama.cpp."""
        try:
            from llama_cpp import Llama
            llm = Llama(model_path=self.model_path)
            output = llm(prompt)
            return output["choices"][0]["text"]
        except ImportError:
            raise RuntimeError("llama-cpp-python not installed. Run: terminal-brain install llm")
        except Exception as e:
            raise RuntimeError(f"llama.cpp inference failed: {e}")
