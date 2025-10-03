from abc import ABC, abstractmethod
from typing import List, Optional
from .classifier_models import TextItem, TopicItem, ClassificationResult
import os
from .config import DEFAULT_TEXT_CLASSIFIER_BACKEND
# Import GeminiClient for Gemini backend
from .gemini_client import GeminiClient

# Abstract base class for all classifier backends
class TextClassifierBackend(ABC):
    @abstractmethod
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        """
        Classify each text into the given topics.
        Returns a list of ClassificationResult objects.
        """
        pass

# Mock backend implementation (existing logic)
class MockTextClassifier(TextClassifierBackend):
    def __init__(self, model_name: Optional[str] = None):
        pass  # model_name ignored for mock
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        results = []
        for text_item in texts:
            matched_topic_ids = [
                topic.id for topic in topics if topic.topic.lower() in text_item.text.lower()
            ]
            results.append(ClassificationResult(text_id=text_item.id, topic_ids=matched_topic_ids))
        return results

# Gemini backend implementation
class GeminiTextClassifier(TextClassifierBackend):
    def __init__(self, model_name: Optional[str] = None):
        self.client = GeminiClient(model_name=model_name)
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        texts_dicts = [{"id": t.id, "text": t.text} for t in texts]
        topics_dicts = [{"id": t.id, "topic": t.topic} for t in topics]
        id_to_topic_ids = self.client.classify_texts(texts_dicts, topics_dicts)
        results = []
        for text in texts:
            topic_ids = id_to_topic_ids.get(text.id, [])
            results.append(ClassificationResult(text_id=text.id, topic_ids=topic_ids))
        return results

# Factory function to select backend

def get_classifier_backend(provider: Optional[str] = None, model_name: Optional[str] = None) -> TextClassifierBackend:
    backend_type = (provider or DEFAULT_TEXT_CLASSIFIER_BACKEND).upper()
    if backend_type == "GEMINI":
        return GeminiTextClassifier(model_name=model_name)
    return MockTextClassifier(model_name=model_name)
