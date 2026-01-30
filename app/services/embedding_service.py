from abc import ABC, abstractmethod
from typing import List, Optional
import openai
from app.config import settings
from app.core.exceptions import AIServiceError
from app.logging_config import get_logger
logger = get_logger(__name__)

class EmbeddingProvider(ABC):

    @abstractmethod
    def embed_text(self, text:str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):

    def __init__(self):
        if not settings.is_openai_configured:
            logger.warning("OpenAI API key not configured")
        else:
            openai.api_key = settings.OPENAI_API_KEY

    def embed_text(self, text: str) -> List[float]:

        if not settings.is_openai_configured:
            raise AIServiceError("OpenAI API key not configured")

        try:
            response = openai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("embedding_failed", error=str(e), text_length=len(text))
            raise AIServiceError(f"Failed to generate embedding: {str(e)}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not settings.is_openai_configured:
            raise AIServiceError("OpenAI API key not configured")

        try:
            response = openai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input = texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error("batch_embedding_failed", error=str(e), batch_size=len(texts))
            raise AIServiceError(f"Failed to generate embeddings: {str(e)}")

def get_embedding_service() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider()