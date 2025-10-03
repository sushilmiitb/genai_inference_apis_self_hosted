from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict

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

# Response model for a single classification result
class ClassificationResult(BaseModel):
    text_id: str = Field(..., description="ID of the classified text")
    topic_ids: List[str] = Field(..., description="List of topic IDs the text belongs to (empty if none)")

# Response model for the batch classification
class ClassifyTextsResponse(BaseModel):
    results: List[ClassificationResult] = Field(..., description="Classification results for each text")

router = APIRouter()

@router.post("/classify-texts", response_model=ClassifyTextsResponse)
def classify_texts(request: ClassifyTextsRequest) -> ClassifyTextsResponse:
    """
    Classify a batch of texts into the given topics.
    Returns only topic IDs for which the classifier is confident; otherwise, the list is empty.
    This is a mock implementation for testing the API contract.
    """
    results = []
    for text_item in request.texts:
        # Mock logic: assign the first topic if the text contains the topic name (case-insensitive)
        matched_topic_ids = [
            topic.id for topic in request.topics if topic.topic.lower() in text_item.text.lower()
        ]
        # Only return topic IDs if there is a confident match (mock: substring match)
        results.append(ClassificationResult(text_id=text_item.id, topic_ids=matched_topic_ids))
    return ClassifyTextsResponse(results=results)
