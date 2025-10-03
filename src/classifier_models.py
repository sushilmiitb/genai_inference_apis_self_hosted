from pydantic import BaseModel, Field
from typing import List, Optional

# Request model for a single text
class TextItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the text")
    text: str = Field(..., description="The text to classify")

# Request model for a single topic
class TopicItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the topic")
    topic: str = Field(..., description="The topic/category name")

# Request model for the batch classification
class ClassifyTextsRequest(BaseModel):
    texts: List[TextItem] = Field(..., description="List of texts to classify", min_items=1)
    topics: List[TopicItem] = Field(..., description="List of topics to classify into", min_items=1)
    provider: Optional[str] = Field(None, description="Preferred model provider (e.g., 'GEMINI', 'MOCK')")
    model_name: Optional[str] = Field(None, description="Preferred model name (e.g., 'gemini-2.5-flash')")

# Response model for a single classification result
class ClassificationResult(BaseModel):
    text_id: str = Field(..., description="ID of the classified text")
    topic_ids: List[str] = Field(..., description="List of topic IDs the text belongs to (empty if none)")

# Response model for the batch classification
class ClassifyTextsResponse(BaseModel):
    results: List[ClassificationResult] = Field(..., description="Classification results for each text")
