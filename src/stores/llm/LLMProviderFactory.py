from .LLMEnums import LLMEnums
from .providers.OpenAIProvider import OpenAIProvider
from helpers.config import Settings
class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config

    def get_provider(self):
        if self.config.PROVIDER == LLMEnums.OPENAI.value:
            client =  OpenAIProvider(
                base_api_key = self.config.OPENAI_BASE_API_KEY,
                base_url = self.config.OPENAI_BASE_URL,
               
            )
        client.set_generation_model(self.config.GENERATION_MODEL_ID)
        client.set_embedding_model(self.config.EMBEDDING_MODEL_ID, self.config.EMBEDDING_DIM)

        client.set_model_config( default_generation_input_max_characters=self.config.GENERATION_DAFAULT_INPUT_MAX_CHARACTERS,
                        default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_OUTPUT_MAX_TOKENS,
                        default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE)

        return client
