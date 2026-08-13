from .ProviderInterface import ProviderInterface
from ..LLMEnums import OpenAIEnums, LLMEnums
from openai import OpenAI
import logging

class OpenAIProvider(ProviderInterface):

    def __init__(self, base_api_key: str, base_url: str=None):
        
        self.base_api_key = base_api_key
        self.base_url = base_url

      
        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_dim = None

        self.client = OpenAI(
            api_key = self.base_api_key,
            base_url = self.base_url
        )

        self.logger = logging.getLogger(__name__)

    def set_model_config(self, default_generation_input_max_characters = 1000, default_generation_max_output_tokens = 1000, default_generation_temperature = 0.1):
        self.default_generation_input_max_characters = default_generation_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_dim: int):
        self.embedding_model_id = model_id
        self.embedding_dim = embedding_dim

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        try:
            return response.choices[0].message["content"]
        except Exception as e:
            self.logger.error(f"Error while generating text with OpenAI with Exception{e}")
            return None

    def embed_text(self, text: str, document_type: str = None):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )

        try:
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error while embedding text with OpenAI with Exception{e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
    


    
    def get_status(self):
        return {
            "provider": LLMEnums.OPENAI.value,
            "api_url": self.base_url,
            "api_key": self.base_api_key,
            "generation_model_id": self.generation_model_id,
            "embedding_model_id": self.embedding_model_id,
            "embedding_dim": self.embedding_dim,
            "default_generation_input_max_characters": self.default_generation_input_max_characters,
            "default_generation_max_output_tokens": self.default_generation_max_output_tokens,
            "default_generation_temperature": self.default_generation_temperature
        }