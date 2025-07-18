from ...LLMInterface import LLMInterface
from ...LLMEnums import CoHereEnums, DocumentTypeEnum
import logging
import cohere

class CohereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):

        self.api_key = api_key 
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    
    def set_generation_model(self, model_id: str):
        """Set the generation model to be used."""
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model to be used."""
        self.embedding_model_id = model_id 
        self.embedding_size = embedding_size
    
    def process_text(self, text: str):
        """Process the text to fit within the maximum character limit."""
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, max_output_tokens: int = None, temperature: float = None, chat_history: list = []) -> str:
        """Generate text based on the provided prompt."""
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            messages=[
                self.construct_prompt(self.process_text(prompt), "user")
            ],
            temperature=temperature,
            max_tokens=max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Failed to generate text.")
            return None

        return response.text if response else None
    
    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value
        
        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"]
        )
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Failed to embed text.")
            return None
        
        return response.embeddings.float[0] 


    def construct_prompt(self, prompt, role):
        return {"role": role, "text": prompt}
    

