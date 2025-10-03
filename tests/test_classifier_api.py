import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test data for the /classify-texts endpoint
TEXTS = [
    {"id": "t1", "text": "This is about sports and health."},
    {"id": "t2", "text": "Politics and economy are discussed here."},
    {"id": "t3", "text": "No matching topic in this text."}
]
TOPICS = [
    {"id": "s", "topic": "sports"},
    {"id": "h", "topic": "health"},
    {"id": "p", "topic": "politics"}
]

# 1. Happy path: Valid request with multiple texts and topics
#    Should return correct topic_ids for each text
def test_classify_texts_happy_path():
    response = client.post(
        "/classify-texts",
        json={"texts": TEXTS, "topics": TOPICS}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # Check that IDs are preserved and topic_ids are correct
    for result in data["results"]:
        assert "text_id" in result
        assert "topic_ids" in result
    # t1 should match 'sports' and 'health'
    t1_result = next(r for r in data["results"] if r["text_id"] == "t1")
    assert set(t1_result["topic_ids"]) == {"s", "h"}
    # t2 should match 'politics'
    t2_result = next(r for r in data["results"] if r["text_id"] == "t2")
    assert set(t2_result["topic_ids"]) == {"p"}
    # t3 should match nothing
    t3_result = next(r for r in data["results"] if r["text_id"] == "t3")
    assert t3_result["topic_ids"] == []

# 2. Edge case: Empty texts list
#    Should return 422 (validation error)
def test_classify_texts_empty_texts():
    response = client.post(
        "/classify-texts",
        json={"texts": [], "topics": TOPICS}
    )
    assert response.status_code == 422

# 3. Edge case: Empty topics list
#    Should return 422 (validation error)
def test_classify_texts_empty_topics():
    response = client.post(
        "/classify-texts",
        json={"texts": TEXTS, "topics": []}
    )
    assert response.status_code == 422

# 4. Invalid request: Missing required fields
#    Should return 422 (validation error)
def test_classify_texts_missing_fields():
    response = client.post(
        "/classify-texts",
        json={"texts": TEXTS}  # Missing 'topics'
    )
    assert response.status_code == 422
    response = client.post(
        "/classify-texts",
        json={"topics": TOPICS}  # Missing 'texts'
    )
    assert response.status_code == 422

# 5. Large batch: Many texts and topics (optional scalability test)
def test_classify_texts_large_batch():
    many_texts = [{"id": f"t{i}", "text": f"Text {i} about sports."} for i in range(100)]
    many_topics = [{"id": f"s{i}", "topic": f"sports"} for i in range(10)]
    response = client.post(
        "/classify-texts",
        json={"texts": many_texts, "topics": many_topics}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 100
    for result in data["results"]:
        assert "text_id" in result
        assert isinstance(result["topic_ids"], list)
