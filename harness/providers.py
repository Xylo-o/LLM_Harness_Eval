import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from .cache import get, put

load_dotenv()

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

@dataclass
class ModelResponse:
    text: str
    latency_ms: int
    tokens_in: int
    tokens_out: int

@dataclass
class OpenAIProvider:
    model: str

    def complete(self, prompt: str):
        cached = get(self.model, prompt)
        if cached is not None:
            return ModelResponse(text=cached.get("text"), latency_ms=cached.get("latency"), tokens_in=cached.get("tokens_in"), tokens_out=cached.get("tokens_out"))

        client = get_client()
        start = time.perf_counter()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        stop = time.perf_counter()
        text = response.choices[0].message.content
        latency = (stop - start) * 1000
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        payload = {
            "text": response.choices[0].message.content,
            "latency_ms": int((stop - start) * 1000),
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
        }
        put(self.model, prompt, payload)
        return ModelResponse(**payload)

