from .locales import rag_prompts_en, rag_prompts_ar
from .TemplatesEnums import TemplatesEnums

class TemplateParser:
    def __init__(self, locale: str, default_locale: str = TemplatesEnums.LOCAL_EN):
        self.locale = locale
        self.default_locale = default_locale
        self.rag_locale_prompts = {
            TemplatesEnums.LOCAL_EN: rag_prompts_en,
            TemplatesEnums.LOCAL_AR: rag_prompts_ar
        }
        self.set_rag_prompts()

    def set_rag_prompts(self):
        self.rag_prompts = self.rag_locale_prompts.get(self.locale, self.rag_locale_prompts.get(self.default_locale))

    def set_local(self, locale: str):
        self.locale = locale
        self.set_rag_prompts()

    def get_rag_prompt(self, prompt_name: str):
        return self.rag_prompts.get(prompt_name, None)

    