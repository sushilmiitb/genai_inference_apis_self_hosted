from abc import ABC, abstractmethod
from typing import List, Optional
from .classifier_models import TextItem, TopicItem, ClassificationResult
from .config import (
    DEFAULT_TEXT_CLASSIFIER_BACKEND,
    GEMINI_RATE_LIMIT_PER_MINUTE,
    GEMINI_RATE_LIMIT_PER_DAY,
)
from .gemini_client import GeminiClient
from fastapi import HTTPException
from limits import RateLimitItemPerMinute, RateLimitItemPerDay
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter

# --- Generic Rate Limiter Abstraction ---
class RateLimiter(ABC):
    @abstractmethod
    def check_limit(self, key: str) -> Optional[str]:
        """
        Returns None if under limit, or a string reason if limit exceeded.
        """
        pass

class InMemoryRateLimiter(RateLimiter):
    def __init__(self, per_minute: int = None, per_day: int = None):
        self.limiter = MovingWindowRateLimiter(MemoryStorage())
        self.minute_limit = RateLimitItemPerMinute(per_minute) if per_minute else None
        self.day_limit = RateLimitItemPerDay(per_day) if per_day else None
    def check_limit(self, key: str) -> Optional[str]:
        if self.minute_limit and not self.limiter.hit(self.minute_limit, key):
            return f"Rate limit exceeded: {self.minute_limit.amount} requests per minute."
        if self.day_limit and not self.limiter.hit(self.day_limit, key):
            return f"Rate limit exceeded: {self.day_limit.amount} requests per day."
        return None

# Abstract base class for all classifier backends
class TextClassifierBackend(ABC):
    @abstractmethod
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        """
        Classify each text into the given topics.
        Returns a list of ClassificationResult objects.
        """
        pass

# Mock backend implementation (with rate limiting for testability)
class MockTextClassifier(TextClassifierBackend):
    def __init__(self, model_name: Optional[str] = None, rate_limiter: Optional[RateLimiter] = None):
        self.rate_limiter = rate_limiter or InMemoryRateLimiter(per_minute=10, per_day=100)  # Example limits for mock
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        key = "mock_global"
        reason = self.rate_limiter.check_limit(key)
        if reason:
            raise HTTPException(status_code=429, detail=f"Mock {reason}")
        results = []
        for text_item in texts:
            matched_topic_ids = [
                topic.id for topic in topics if topic.topic.lower() in text_item.text.lower()
            ]
            results.append(ClassificationResult(text_id=text_item.id, topic_ids=matched_topic_ids))
        return results

# Gemini backend implementation (with rate limiting)
class GeminiTextClassifier(TextClassifierBackend):
    def __init__(self, model_name: Optional[str] = None, rate_limiter: Optional[RateLimiter] = None):
        self.client = GeminiClient(model_name=model_name)
        self.rate_limiter = rate_limiter or InMemoryRateLimiter(
            per_minute=GEMINI_RATE_LIMIT_PER_MINUTE, per_day=GEMINI_RATE_LIMIT_PER_DAY
        )
    def classify(self, texts: List[TextItem], topics: List[TopicItem]) -> List[ClassificationResult]:
        key = "gemini_global"
        reason = self.rate_limiter.check_limit(key)
        if reason:
            raise HTTPException(status_code=429, detail=f"Gemini {reason}")
        texts_dicts = [{"id": t.id, "text": t.text} for t in texts]
        topics_dicts = [{"id": t.id, "topic": t.topic} for t in topics]
        id_to_topic_ids = self.client.classify_texts(texts_dicts, topics_dicts)
        results = []
        for text in texts:
            topic_ids = id_to_topic_ids.get(text.id, [])
            results.append(ClassificationResult(text_id=text.id, topic_ids=topic_ids))
        return results

# Factory function to select backend

def get_classifier_backend(provider: Optional[str] = None, model_name: Optional[str] = None, rate_limiter: Optional[RateLimiter] = None) -> TextClassifierBackend:
    backend_type = (provider or DEFAULT_TEXT_CLASSIFIER_BACKEND).upper()
    if backend_type == "GEMINI":
        return GeminiTextClassifier(model_name=model_name, rate_limiter=rate_limiter)
    return MockTextClassifier(model_name=model_name, rate_limiter=rate_limiter)
