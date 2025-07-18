from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def set_generation_model(self, model_id: str):
        """Set the generation model to be used."""
        pass  

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model to be used."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_output_tokens: int = None, temperature: float = None , chat_history: list = []) -> str:
        """Generate text based on the provided prompt."""
        pass

    
    @abstractmethod
    def embed_text(self, text: str, document_type: str = None) -> list:
        """Embed the provided text and return the embeddings."""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> str:
        """Construct a prompt using the query and context."""
        pass