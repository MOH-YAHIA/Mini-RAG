from .BaseController import BaseController
from models import Project,Chunk
from typing import List
from stores.llm.templates import TemplateParser
from stores.llm.LLMEnums import OpenAIEnums

class RagController(BaseController):
    def __init__(self,llm_provider, vector_db_provider):
        super().__init__()

        self.llm_provider = llm_provider
        self.vector_db_provider = vector_db_provider

    def get_project_collection(self,project_id):
        return f"collection_{project_id}".strip()

    
    def embed_chunks(self, project : Project , chunks: List[Chunk], embedding_size:int , distance_method: str):
        collection_name = self.get_project_collection(project.project_id)

        chunks_text = [chunk.chunk_text for chunk in chunks]
        chunks_metadata = [chunk.chunk_metadata for chunk in chunks]

        chunks_embeddings = [self.llm_provider.embed_text(chunk_text)
                             for chunk_text in chunks_text]

        success = self.vector_db_provider.create_collection(collection_name = collection_name,
                                                  embedding_size = embedding_size,
                                                  distance_method = distance_method,
                                                  )

        if not success:
            return False
        
        success = self.vector_db_provider.insert_many(collection_name = collection_name,
                                            texts = chunks_text,
                                            vectors = chunks_embeddings,
                                            metadata = chunks_metadata)

        if not success:
            return False
        
        return True

        
    def search_vector_db(self, project: Project, text: str, limit: int = 10):

            # step1: get collection name
            collection_name = self.get_project_collection(project_id=project.project_id)

            # step2: get text embedding vector
            vector = self.llm_provider.embed_text(text=text)

            if not vector or len(vector) == 0:
                return False

            # step3: do semantic search
            results = self.vector_db_provider.search_by_vector(
                collection_name=collection_name,
                vector=vector,
                limit=limit
            )

            if not results:
                return False

            retrieved_documents_with_scores = [{"text":result.dict().get("payload").get("text"), "score":result.dict().get("score")} for result in results]
            return retrieved_documents_with_scores

    
    def get_project_collection_info(self,project: Project):
        collection_name = self.get_project_collection(project_id=project.project_id)
        if not self.vector_db_provider.is_collection_existed(collection_name=collection_name):
            return None
        collection_info = self.vector_db_provider.get_collection_info(collection_name=collection_name)

        return collection_info

    def answer_rag_question(self, locale : str ,  project: Project, question: str, limit: int = 10):

        templete_parser = TemplateParser(locale=locale)
        system_prompt = templete_parser.get_rag_prompt(prompt_name="system").substitute()
        document_prompt = templete_parser.get_rag_prompt(prompt_name="retrieved_document")
        footer_prompt = templete_parser.get_rag_prompt(prompt_name="footer").substitute()

        retrieved_documents_with_scores = self.search_vector_db(project=project, text=question, limit=limit)
        if not retrieved_documents_with_scores:
            return None, None

        docs_text = [retrieved_document_with_scores["text"] for retrieved_document_with_scores in retrieved_documents_with_scores]
        retrived_text = "\n\n" + "\n\n".join([document_prompt.substitute(retrieved_text=doc_text) for doc_text in docs_text])

        system_prompt += retrived_text
        system_prompt += footer_prompt

        chat_history = [
            self.llm_provider.construct_prompt(prompt=system_prompt, role=OpenAIEnums.SYSTEM.value)
        ]

        answer =  self.llm_provider.generate_text(prompt=question, chat_history=chat_history)

        return answer,chat_history