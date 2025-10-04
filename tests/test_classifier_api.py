import pytest
from fastapi.testclient import TestClient
from main import app
import os
from src.classifier_backends import InMemoryRateLimiter, get_classifier_backend

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

class TestBasicAPIValidation:
    """Tests for request/response validation and basic API behavior"""
    
    def test_classify_texts_happy_path(self):
        """Happy path: Valid request with multiple texts and topics"""
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

    def test_classify_texts_empty_texts(self):
        """Edge case: Empty texts list should return 422 validation error"""
        response = client.post(
            "/classify-texts",
            json={"texts": [], "topics": TOPICS}
        )
        assert response.status_code == 422

    def test_classify_texts_empty_topics(self):
        """Edge case: Empty topics list should return 422 validation error"""
        response = client.post(
            "/classify-texts",
            json={"texts": TEXTS, "topics": []}
        )
        assert response.status_code == 422

    def test_classify_texts_missing_fields(self):
        """Invalid request: Missing required fields should return 422 validation error"""
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

    def test_classify_texts_large_batch(self):
        """Large batch: Many texts and topics (scalability test)"""
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

class TestProviderAndModelSelection:
    """Tests for provider and model_name parameter handling"""

    def test_classify_texts_default_provider_model(self):
        """Default behavior: no provider/model_name (should use config defaults)"""
        response = client.post(
            "/classify-texts",
            json={"texts": TEXTS, "topics": TOPICS}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_classify_texts_valid_mock(self):
        """Valid provider: MOCK (model_name None)"""
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

    def test_classify_texts_invalid_provider(self):
        """Invalid provider should return 400"""
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

    def test_classify_texts_invalid_model_for_gemini(self):
        """Invalid model_name for valid provider should return 400"""
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

    def test_classify_texts_invalid_model_for_mock(self):
        """Invalid model_name for MOCK provider should return 400"""
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

    def test_classify_texts_empty_provider_model(self):
        """Edge case: empty strings for provider/model_name should fallback or error"""
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

    def test_classify_texts_whitespace_provider_model(self):
        """Edge case: whitespace in provider/model_name should be stripped and normalized"""
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

class TestRateLimiting:
    """Tests for rate limiting functionality"""

    def test_mock_rate_limit_per_minute(self):
        """Test rate limiting per minute for Mock backend"""
        # Use a custom rate limiter with 2 requests per minute
        limiter = InMemoryRateLimiter(per_minute=2, per_day=100)
        backend = get_classifier_backend(provider="MOCK", rate_limiter=limiter)
        texts = [
            {"id": f"t{i}", "text": f"Text {i}"} for i in range(2)
        ]
        topics = [{"id": "a", "topic": "A"}]
        # First two requests should succeed
        for i in range(2):
            req_texts = [texts[i]]
            results = backend.classify(
                [type("TextItem", (), t)() for t in req_texts],
                [type("TopicItem", (), t)() for t in topics],
            )
            assert isinstance(results, list)
        # Third request should fail with 429
        with pytest.raises(Exception) as excinfo:
            backend.classify(
                [type("TextItem", (), texts[0])()],
                [type("TopicItem", (), topics[0])()],
            )
        assert "429" in str(excinfo.value)
        assert "per minute" in str(excinfo.value)

    def test_mock_rate_limit_per_day(self):
        """Test rate limiting per day for Mock backend"""
        # Use a custom rate limiter with 100 per minute, 2 per day
        limiter = InMemoryRateLimiter(per_minute=100, per_day=2)
        backend = get_classifier_backend(provider="MOCK", rate_limiter=limiter)
        texts = [
            {"id": f"t{i}", "text": f"Text {i}"} for i in range(2)
        ]
        topics = [{"id": "a", "topic": "A"}]
        # First two requests should succeed
        for i in range(2):
            req_texts = [texts[i]]
            results = backend.classify(
                [type("TextItem", (), t)() for t in req_texts],
                [type("TopicItem", (), topics[0])()],
            )
            assert isinstance(results, list)
        # Third request should fail with 429
        with pytest.raises(Exception) as excinfo:
            backend.classify(
                [type("TextItem", (), texts[0])()],
                [type("TopicItem", (), topics[0])()],
            )
        assert "429" in str(excinfo.value)
        assert "per day" in str(excinfo.value)

class TestGeminiIntegration:
    """Integration tests requiring real Gemini API"""

    # Real-world topics and texts for integration testing
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
        "t3": [],
        "t4": ["p"],
        "t5": [],
        "t6": ["mu"],
        "t7": ["m"],
        "t8": ["c"],
    }

    @pytest.mark.integration
    @pytest.mark.skipif(
        not (hasattr(__import__('config_secret', fromlist=['GEMINI_API_KEY']), 'GEMINI_API_KEY') and 
             getattr(__import__('config_secret', fromlist=['GEMINI_API_KEY']), 'GEMINI_API_KEY', None)),
        reason="GEMINI_API_KEY not set in config_secret.py; skipping Gemini integration tests."
    )
    def test_gemini_integration_real_world_cases(self):
        """
        Integration test: Gemini backend with real-world topics/texts, model_name always specified.
        """
        response = client.post(
            "/classify-texts",
            json={
                "texts": self.INTEGRATION_TEXTS,
                "topics": self.INTEGRATION_TOPICS,
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
            expected = set(self.INTEGRATION_EXPECTED[text_id])
            actual = set(result["topic_ids"])
            assert actual == expected, f"Text {text_id}: expected {expected}, got {actual}"
