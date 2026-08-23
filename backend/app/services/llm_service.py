"""Deterministic mock AI responses for demo and testing."""

import hashlib
import json
import time
from abc import ABC, abstractmethod

from app.core.config import settings
from app.schemas.answer import StructuredAnswer


class AIResponse:
    def __init__(
        self,
        raw_answer: str,
        structured: StructuredAnswer,
        provider: str,
        model: str,
        latency_ms: float,
    ):
        self.raw_answer = raw_answer
        self.structured = structured
        self.provider = provider
        self.model = model
        self.latency_ms = latency_ms


class LLMProvider(ABC):
    @abstractmethod
    def run_query(self, query_text: str) -> AIResponse:
        pass


MOCK_SCENARIOS: list[dict] = [
    {
        "answer_summary": "Top Middle East beauty retailers include Sephora, Amazon, Boutiqaat, and Noon.",
        "recommendations": [
            {"company": "Sephora", "position": 1, "recommended": True, "reason": "Global beauty leader with GCC stores"},
            {"company": "Amazon", "position": 2, "recommended": True, "reason": "Wide selection and fast delivery"},
            {"company": "Boutiqaat", "position": 3, "recommended": True, "reason": "Regional specialist with celebrity brands"},
            {"company": "Noon", "position": 4, "recommended": True, "reason": "Popular GCC marketplace"},
        ],
        "boutiqaat": {"mentioned": True, "recommended": True, "position": 3, "reason": "Strong regional presence"},
        "sources": [
            {"url": "https://www.sephora.ae", "domain": "sephora.ae", "title": "Sephora UAE"},
            {"url": "https://www.boutiqaat.com", "domain": "boutiqaat.com", "title": "Boutiqaat Official"},
            {"url": "https://www.arabianbusiness.com/beauty-retail-gcc", "domain": "arabianbusiness.com", "title": "GCC Beauty Retail Report"},
        ],
    },
    {
        "answer_summary": "For Korean skincare in GCC, Boutiqaat and YesStyle are top choices.",
        "recommendations": [
            {"company": "Boutiqaat", "position": 1, "recommended": True, "reason": "Strong K-beauty catalog in Kuwait/Saudi"},
            {"company": "YesStyle", "position": 2, "recommended": True, "reason": "Extensive Korean skincare range"},
            {"company": "iHerb", "position": 3, "recommended": True, "reason": "Affordable K-beauty with GCC shipping"},
        ],
        "boutiqaat": {"mentioned": True, "recommended": True, "position": 1, "reason": "Leading regional K-beauty retailer"},
        "sources": [
            {"url": "https://www.boutiqaat.com/korean-skincare", "domain": "boutiqaat.com", "title": "Korean Skincare | Boutiqaat"},
            {"url": "https://www.yesstyle.com", "domain": "yesstyle.com", "title": "YesStyle K-Beauty"},
        ],
    },
    {
        "answer_summary": "Best beauty shopping websites: Sephora, Amazon, Namshi, and iHerb dominate recommendations.",
        "recommendations": [
            {"company": "Sephora", "position": 1, "recommended": True, "reason": "Premium beauty destination"},
            {"company": "Amazon", "position": 2, "recommended": True, "reason": "Convenience and variety"},
            {"company": "Namshi", "position": 3, "recommended": True, "reason": "Fashion and beauty in GCC"},
            {"company": "iHerb", "position": 4, "recommended": True, "reason": "Natural and skincare products"},
        ],
        "boutiqaat": {"mentioned": False, "recommended": False, "position": None, "reason": ""},
        "sources": [
            {"url": "https://www.sephora.com", "domain": "sephora.com", "title": "Sephora"},
            {"url": "https://www.namshi.com", "domain": "namshi.com", "title": "Namshi"},
        ],
    },
    {
        "answer_summary": "Companies such as Sephora and Boutiqaat are popular, but I recommend Sephora and Noon for skincare.",
        "recommendations": [
            {"company": "Sephora", "position": 1, "recommended": True, "reason": "Best curated skincare"},
            {"company": "Noon", "position": 2, "recommended": True, "reason": "Local marketplace with deals"},
        ],
        "boutiqaat": {"mentioned": True, "recommended": False, "position": None, "reason": "Mentioned as popular but not recommended"},
        "sources": [
            {"url": "https://www.sephora.ae/skincare", "domain": "sephora.ae", "title": "Skincare at Sephora"},
        ],
    },
    {
        "answer_summary": "For COSRX in Saudi Arabia, try Amazon.sa, Nice One, and iHerb.",
        "recommendations": [
            {"company": "Amazon", "position": 1, "recommended": True, "reason": "Fast Saudi delivery"},
            {"company": "Nice One", "position": 2, "recommended": True, "reason": "Local Saudi beauty retailer"},
            {"company": "iHerb", "position": 3, "recommended": True, "reason": "Authentic COSRX products"},
        ],
        "boutiqaat": {"mentioned": False, "recommended": False, "position": None, "reason": ""},
        "sources": [
            {"url": "https://www.amazon.sa", "domain": "amazon.sa", "title": "Amazon Saudi"},
            {"url": "https://niceonesa.com", "domain": "niceonesa.com", "title": "Nice One SA"},
        ],
    },
    {
        "answer_summary": "GCC online beauty: Boutiqaat ranks highly alongside Sephora for makeup and skincare.",
        "recommendations": [
            {"company": "Boutiqaat", "position": 1, "recommended": True, "reason": "Celebrity-backed GCC beauty platform"},
            {"company": "Sephora", "position": 2, "recommended": True, "reason": "International brand trust"},
            {"company": "Faces", "position": 3, "recommended": True, "reason": "Regional beauty chain"},
        ],
        "boutiqaat": {"mentioned": True, "recommended": True, "position": 1, "reason": "Top GCC beauty destination"},
        "sources": [
            {"url": "https://www.boutiqaat.com", "domain": "boutiqaat.com", "title": "Boutiqaat"},
            {"url": "https://www.voguearabia.com/beauty-shopping", "domain": "voguearabia.com", "title": "Best Beauty Shopping GCC"},
            {"url": "https://www.boutiqaat.com/en/about", "domain": "boutiqaat.com", "title": "About Boutiqaat"},
        ],
    },
    {
        "answer_summary": "Laneige products available at Sephora, Amazon, and Boutiqaat in UAE.",
        "recommendations": [
            {"company": "Sephora", "position": 1, "recommended": True, "reason": "Official Laneige partner"},
            {"company": "Amazon", "position": 2, "recommended": True, "reason": "Competitive pricing"},
            {"company": "Boutiqaat", "position": 3, "recommended": True, "reason": "Available in UAE with local support"},
        ],
        "boutiqaat": {"mentioned": True, "recommended": True, "position": 3, "reason": "Carries Laneige in UAE"},
        "sources": [
            {"url": "https://www.sephora.ae/brands/laneige", "domain": "sephora.ae", "title": "Laneige at Sephora"},
        ],
    },
]


def _scenario_index(query_text: str) -> int:
    digest = hashlib.md5(query_text.encode()).hexdigest()
    return int(digest, 16) % len(MOCK_SCENARIOS)


def _format_raw_answer(structured: dict) -> str:
    lines = [structured["answer_summary"], "", "Recommendations:"]
    for rec in structured.get("recommendations", []):
        pos = rec.get("position", "?")
        lines.append(f"{pos}. {rec['company']} — {rec.get('reason', '')}")
    b = structured.get("boutiqaat", {})
    if b.get("mentioned"):
        status = "recommended" if b.get("recommended") else "mentioned only"
        lines.append(f"\nBoutiqaat: {status}")
    if structured.get("sources"):
        lines.append("\nSources:")
        for s in structured["sources"]:
            lines.append(f"- {s.get('title', s.get('domain', ''))}: {s.get('url', '')}")
    return "\n".join(lines)


class MockLLMProvider(LLMProvider):
    def run_query(self, query_text: str) -> AIResponse:
        time.sleep(0.05)
        scenario = MOCK_SCENARIOS[_scenario_index(query_text)].copy()
        structured = StructuredAnswer(**scenario)
        raw = _format_raw_answer(scenario)
        return AIResponse(
            raw_answer=raw,
            structured=structured,
            provider="mock",
            model="mock-deterministic-v1",
            latency_ms=50.0,
        )


class OpenAIProvider(LLMProvider):
    SYSTEM_PROMPT = """You are simulating an AI shopping assistant answering beauty/skincare retail questions for GCC/Middle East customers.
Return JSON with this exact schema:
{
  "answer_summary": "string",
  "recommendations": [{"company": "name", "position": 1, "recommended": true, "reason": "why"}],
  "boutiqaat": {"mentioned": bool, "recommended": bool, "position": int|null, "reason": "string"},
  "sources": [{"url": "string", "domain": "string", "title": "string"}]
}
Only include real or plausible retailers. Mention Boutiqaat only when genuinely relevant."""

    def run_query(self, query_text: str) -> AIResponse:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY required when MOCK_MODE=false")

        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        start = time.time()
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": query_text},
            ],
            response_format={"type": "json_object"},
        )
        latency = (time.time() - start) * 1000
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        structured = StructuredAnswer(**data)
        raw = _format_raw_answer(data)
        return AIResponse(
            raw_answer=raw,
            structured=structured,
            provider="openai",
            model=settings.openai_model,
            latency_ms=latency,
        )


def get_llm_provider(provider_name: str = "mock") -> LLMProvider:
    if settings.mock_mode or provider_name == "mock":
        return MockLLMProvider()
    return OpenAIProvider()
