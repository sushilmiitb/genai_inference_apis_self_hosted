import os
from typing import Dict, Any, List
from google import genai
from google.genai import types, errors
from pydantic import BaseModel
from .config import GEMINI_MODEL_NAME

# Pydantic models for Gemini structured output
class GeminiClassificationResult(BaseModel):
    text_id: str
    topic_ids: List[str]

class GeminiClassificationResponse(BaseModel):
    results: List[GeminiClassificationResult]

class GeminiClient:
    """
    Client for interacting with the Gemini 2.5 Flash API for batch text classification using google-genai library.
    """
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or GEMINI_MODEL_NAME
        if not self.api_key:
            raise ValueError("Gemini API key not set. Set GEMINI_API_KEY environment variable.")
        self.client = genai.Client(api_key=self.api_key)

    def classify_texts(self, texts: List[Dict[str, str]], topics: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Sends a single structured prompt to Gemini for all texts and topics, returns mapping from text_id to topic_ids.
        """
        prompt = self._build_batch_prompt(texts, topics)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": GeminiClassificationResponse,
                },
            )
            # Use the parsed property for structured output
            parsed: GeminiClassificationResponse = response.parsed
            if not parsed or not parsed.results:
                return {}
            return {r.text_id: r.topic_ids for r in parsed.results}
        except errors.APIError as e:
            # Log or handle API errors as needed
            return {}

    def _build_batch_prompt(self, texts: List[Dict[str, str]], topics: List[Dict[str, str]]) -> str:
        """
        Build a structured prompt for Gemini to classify all texts into topic IDs.
        """
        import json
        prompt = (
            "I have a list of youtube video titles along with channel names. I want to determine if that youtube title belongs to any of the topics."
            "Given the following texts (with IDs) and topics (with IDs), return a JSON object with a 'results' field, which is an array of objects, each with a text_id and a topic_ids array (from the provided list) that the text clearly belongs to. "
            "If a text does not belong to any, use an empty array.\n"
            f"Texts: {json.dumps(texts)}\n"
            f"Topics: {json.dumps(topics)}\n"
            "Respond with only a JSON object like: {\"results\": [{\"text_id\": \"t1\", \"topic_ids\": [\"p\"]}, {\"text_id\": \"t2\", \"topic_ids\": []}]}"
        )
        return prompt
