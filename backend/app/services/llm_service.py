import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
import httpx

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.models.product import Product
from backend.app.prompts.system_prompt import SYSTEM_PROMPT
from backend.app.services.ollama_service import ollama_service


class LLMService:
    """
    Unified High-Performance AI Synthesis & LLM Service.
    Supports:
    - Tier 1: Instant Intelligent Grounded Synthesis (< 5ms response time)
    - Tier 2: Ultra-Fast Cloud API (Gemini / Groq / OpenAI) with short timeout
    - Tier 3: Local Ollama with fast circuit breaking (2.5s timeout)
    """

    def __init__(self):
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._cache_ttl = 300.0  # 5 minutes cache

    def get_cached(self, key: str) -> Optional[str]:
        if key in self._cache:
            val, expire = self._cache[key]
            if time.time() < expire:
                return val
            else:
                del self._cache[key]
        return None

    def set_cached(self, key: str, val: str):
        if len(self._cache) > 500:
            self._cache.clear()
        self._cache[key] = (val, time.time() + self._cache_ttl)

    async def generate_response(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT,
        temperature: float = 0.2,
        max_tokens: int = 150
    ) -> Optional[str]:
        """
        Attempt generation using Cloud LLM (Gemini / Groq) or Ollama with strict timeouts.
        Returns None if external LLM generation is unavailable or times out.
        """
        cache_key = f"{prompt[:100]}_{hash(prompt)}"
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        # 1. Try Gemini API if key is present
        gemini_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        if gemini_key:
            try:
                text = await self._generate_gemini(gemini_key, prompt, system)
                if text:
                    self.set_cached(cache_key, text)
                    return text
            except Exception as e:
                logger.warning(f"Gemini API generation failed/timed out: {e}")

        # 2. Try Groq API if key is present
        groq_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
        if groq_key:
            try:
                text = await self._generate_groq(groq_key, prompt, system)
                if text:
                    self.set_cached(cache_key, text)
                    return text
            except Exception as e:
                logger.warning(f"Groq API generation failed/timed out: {e}")

        # 3. Try Local Ollama if available
        try:
            if await ollama_service.is_available():
                text = await ollama_service.generate(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                if text:
                    self.set_cached(cache_key, text)
                    return text
        except Exception as e:
            logger.debug(f"Ollama fast generation bypassed: {e}")

        return None

    async def _generate_gemini(self, api_key: str, prompt: str, system: str) -> Optional[str]:
        """Call Google Gemini 2.0 Flash / 1.5 Flash API with 2.0s timeout."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"System: {system}\n\nUser: {prompt}"}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 150
            }
        }
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return text
        return None

    async def _generate_groq(self, api_key: str, prompt: str, system: str) -> Optional[str]:
        """Call Groq API (Llama 3 8B) with 2.0s timeout."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 150
        }
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"].strip()
                return text
        return None

    def synthesize_fast_recommendation(
        self,
        query: str,
        products: List[Product],
        parsed_query=None
    ) -> str:
        """
        Instantaneous (<1ms) grounded synthesis for product recommendations.
        Produces fluent, human-like, accurate 1-2 sentence summaries.
        """
        if not products:
            return "No products found matching your requirements."

        top = products[0]
        max_p = getattr(parsed_query, "max_price", None) if parsed_query else None
        category = getattr(parsed_query, "category", None) if parsed_query else None

        if len(products) == 1:
            budget_str = f" under your ₹{max_p:,} budget" if max_p and top.price <= max_p else ""
            feat_str = f" featuring {top.features[0]}" if top.features else ""
            return f"I recommend the {top.name} priced at ₹{top.price:,}{budget_str},{feat_str}."

        second = products[1]
        top_names = f"{top.name} (₹{top.price:,}) and {second.name} (₹{second.price:,})"

        if max_p:
            return f"Here are our top recommendations under ₹{max_p:,}: {top_names}."
        elif category:
            return f"Here are the top-rated {category} matching your search: {top_names}."
        else:
            return f"Based on your requirements, here are our top recommendations: {top_names}."

    def synthesize_fast_support_answer(
        self,
        query: str,
        top_doc: Dict[str, Any],
        search_results: List[Tuple[Dict[str, Any], float]]
    ) -> str:
        """
        Instantaneous (<1ms) grounded policy answer extraction from knowledge chunks.
        """
        content = top_doc.get("content", "").strip()
        lines = [l.strip().lstrip("-*# ") for l in content.split("\n") if l.strip() and not l.startswith("#")]

        # Query word matching
        query_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', query)]
        matched_lines = []
        for line in lines:
            if any(qw in line.lower() for qw in query_words if qw not in {"what", "when", "where", "how", "can", "the", "and", "for", "with", "does"}):
                matched_lines.append(line)

        if not matched_lines:
            matched_lines = lines[:2]

        snippet_summary = " ".join(matched_lines[:2])
        doc_name = top_doc.get("title", top_doc.get("document", "our store policy"))
        return f"According to our {doc_name}, {snippet_summary}"


llm_service = LLMService()
