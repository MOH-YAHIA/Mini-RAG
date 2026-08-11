from .BaseController import BaseController
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os 
from models import ProcessTypeEnums
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ProcessController(BaseController):
    def __init__(self, project_id):
        super().__init__()

        self.project_id = project_id

    def load_document(self,asset_name: str) -> List[Document]:
        """
        Loads a document based on its extension using lightweight loaders.
        
        :return: List of LangChain Document objects
        """
        path = os.path.join(self.projects_directory,self.project_id, asset_name)

        # Invariant: Check if file exists before processing
        if not os.path.exists(path):
            return None

        ext = '.' + path.split('.')[-1].lower()

        # Strategy pattern mapping extension -> lightweight loader
        if ext == ProcessTypeEnums.TXT.value:
            loader = TextLoader(str(path), encoding="utf-8")
        elif ext == ProcessTypeEnums.PDF.value:
            loader = PyPDFLoader(str(path))
        else:
            return None

        return loader.load()


    def split_documents(
        self,
        documents: List[Document], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[Document]:
        """
        Splits a list of LangChain Document objects into smaller chunks recursively.

        :param documents: List of input Document objects
        :param chunk_size: Maximum character size for each chunk
        :param chunk_overlap: Number of characters to overlap between adjacent chunks
        :return: List of chunked Document objects preserving original metadata
        """
        # Guard clause: check for empty inputs
        if not documents:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

        try:
            chunks =  splitter.split_documents(documents)
        except Exception as e:
            self.logger.error(f"Error while splitting documents: {e}")
            return None
        return chunks