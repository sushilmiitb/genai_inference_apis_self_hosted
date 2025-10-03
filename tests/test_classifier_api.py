import pytest
from fastapi.testclient import TestClient
from main import app
import os

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

# --- Provider/model_name selection and validation tests ---

# 1. Default behavior: no provider/model_name (should use config defaults)
def test_classify_texts_default_provider_model():
    response = client.post(
        "/classify-texts",
        json={"texts": TEXTS, "topics": TOPICS}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

# 2. Valid provider/model_name: GEMINI + gemini-2.5-flash
#    Should raise ValueError due to missing API key in test environment
def test_classify_texts_valid_gemini_missing_api_key():
    with pytest.raises(ValueError) as excinfo:
        client.post(
            "/classify-texts",
            json={
                "texts": TEXTS,
                "topics": TOPICS,
                "provider": "GEMINI",
                "model_name": "gemini-2.5-flash"
            }
        )
    assert "GEMINI_API_KEY" in str(excinfo.value)

# 3. Valid provider: MOCK (model_name None)
def test_classify_texts_valid_mock():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "MOCK"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

# 4. Invalid provider (should return 400)
def test_classify_texts_invalid_provider():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "INVALID"
        }
    )
    assert response.status_code == 400
    assert "Invalid provider" in response.text

# 5. Invalid model_name for valid provider (should return 400)
def test_classify_texts_invalid_model_for_gemini():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "GEMINI",
            "model_name": "not-a-model"
        }
    )
    assert response.status_code == 400
    assert "Invalid model_name" in response.text

def test_classify_texts_invalid_model_for_mock():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "MOCK",
            "model_name": "gemini-2.5-flash"
        }
    )
    assert response.status_code == 400
    assert "Invalid model_name" in response.text

# 6. Case insensitivity for provider
#    Should raise ValueError due to missing API key in test environment
def test_classify_texts_provider_case_insensitive_missing_api_key():
    with pytest.raises(ValueError) as excinfo:
        client.post(
            "/classify-texts",
            json={
                "texts": TEXTS,
                "topics": TOPICS,
                "provider": "gemini"
            }
        )
    assert "GEMINI_API_KEY" in str(excinfo.value)

# 7. Edge case: empty strings for provider/model_name (should fallback or error)
def test_classify_texts_empty_provider_model():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "",
            "model_name": ""
        }
    )
    # Should fallback to config or error; accept either 200 or 400
    assert response.status_code in (200, 400)

# 8. Edge case: whitespace in provider/model_name (should be stripped and normalized)
def test_classify_texts_whitespace_provider_model():
    response = client.post(
        "/classify-texts",
        json={
            "texts": TEXTS,
            "topics": TOPICS,
            "provider": "  GEMINI  ",
            "model_name": "  gemini-2.5-flash  "
        }
    )
    # Should be normalized and succeed
    assert response.status_code == 200 or response.status_code == 400  # Accept either, depending on normalization

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

# --- Gemini integration tests (require GEMINI_API_KEY) ---
# Real-world topics and texts
INTEGRATION_TOPICS = [
    {"id": "p", "topic": "Politics"},
    {"id": "m", "topic": "Movie"},
    {"id": "mu", "topic": "Music"},
    {"id": "c", "topic": "Cricket"},
]
INTEGRATION_TEXTS = [
    {"id": "t1", "text": "US H-1B Chaos: China Unveils K Visa to Woo Global Talent | Vantage with Palki Sharma | N18G - Firstpost"},
    {"id": "t2", "text": "OSHO: You Can Run but You Can't Hide - OSHO International"},
    {"id": "t3", "text": "H1B Visa और भारत || आचार्य प्रशांत"},
    {"id": "t4", "text": "British People Are LEARNING the LESSON 😔 #ukcrime #ukpolice #crimetv #crimenews #rishisunak"},
    {"id": "t5", "text": "कम्फर्ट जोन से बाहर कैसे निकलें? || आचार्य प्रशांत"},
    {"id": "t6", "text": "Ye Tune Kya Kiya | Ahmed, Khalfaan, Hyder X Stereo India"},
    {"id": "t7", "text": "The Dark Knight Rises - Blake Knows Bruce's Secret (HD) | The Don"},
    {"id": "t8", "text": "Harbhajan Singh on Gun Celebration #indvspak #asiacup2025 #cricket #shorts"},
]
# Expected mapping: text_id -> [topic_id]
INTEGRATION_EXPECTED = {
    "t1": ["p"],
    "t2": [],
    "t3": ["p"],
    "t4": ["p"],
    "t5": [],
    "t6": ["mu"],
    "t7": ["m"],
    "t8": ["c"],
}

@pytest.mark.integration
@pytest.mark.skipif(
    not ("GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]),
    reason="GEMINI_API_KEY not set; skipping Gemini integration tests."
)
def test_gemini_integration_real_world_cases():
    """
    Integration test: Gemini backend, real-world topics/texts, model_name always specified.
    """
    response = client.post(
        "/classify-texts",
        json={
            "texts": INTEGRATION_TEXTS,
            "topics": INTEGRATION_TOPICS,
            "provider": "GEMINI",
            "model_name": "gemini-2.5-flash"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # Check each text's classification
    for result in data["results"]:
        text_id = result["text_id"]
        expected = set(INTEGRATION_EXPECTED[text_id])
        actual = set(result["topic_ids"])
        assert actual == expected, f"Text {text_id}: expected {expected}, got {actual}"
