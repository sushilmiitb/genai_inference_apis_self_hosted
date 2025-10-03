from pydantic import BaseModel, Field
from typing import List, Optional

class TextItem(BaseModel):
    """
    Represents a single text to be classified.
    """
    id: str = Field(..., description="Unique identifier for the text.")
    text: str = Field(..., description="The text to classify.")

class TopicItem(BaseModel):
    """
    Represents a single topic/category for classification.
    """
    id: str = Field(..., description="Unique identifier for the topic.")
    topic: str = Field(..., description="The topic/category name.")

class ClassifyTextsRequest(BaseModel):
    """
    Request model for batch text classification.
    - provider: Optional. Preferred model provider (e.g., 'GEMINI', 'MOCK'). If not provided, uses config default.
    - model_name: Optional. Preferred model name (e.g., 'gemini-2.5-flash'). If not provided, uses config default for the provider.
    """
    texts: List[TextItem] = Field(..., description="List of texts to classify.", min_items=1, example=[{"id": "t1", "text": "Example text."}])
    topics: List[TopicItem] = Field(..., description="List of topics to classify into.", min_items=1, example=[{"id": "p", "topic": "Politics"}])
    provider: Optional[str] = Field(None, description="Preferred model provider (e.g., 'GEMINI', 'MOCK'). Optional.", example="GEMINI")
    model_name: Optional[str] = Field(None, description="Preferred model name (e.g., 'gemini-2.5-flash'). Optional.", example="gemini-2.5-flash")

class ClassificationResult(BaseModel):
    """
    Classification result for a single text.
    """
    text_id: str = Field(..., description="ID of the classified text.")
    topic_ids: List[str] = Field(..., description="List of topic IDs the text belongs to (empty if none).")

class ClassifyTextsResponse(BaseModel):
    """
    Response model for batch text classification.
    """
    results: List[ClassificationResult] = Field(..., description="Classification results for each text.", example=[{"text_id": "t1", "topic_ids": ["p"]}])
