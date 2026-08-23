import re
from typing import List, Optional, Tuple
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.chat import SourceDocument
from backend.app.services.vector_store_service import vector_store_service
from backend.app.services.llm_service import llm_service
from backend.app.prompts.support_prompt import build_support_prompt
from backend.app.prompts.system_prompt import SYSTEM_PROMPT


class RAGService:
    """Retrieval-Augmented Generation service for customer support and policy queries."""

    FALLBACK_MESSAGE = "I don't have enough information in the available knowledge base to answer that question."

    async def query_knowledge_base(
        self,
        query: str,
        conversation_history: str = "",
        top_k: int = 3
    ) -> Tuple[str, List[SourceDocument], bool]:
        """
        Execute RAG flow for support inquiries:
        1. Embed user query & search FAISS knowledge index.
        2. Apply strict similarity threshold filter.
        3. Check topic relevance to ensure no hallucination on missing policies.
        4. Synthesize short (1-3 sentences) grounded answer with sub-millisecond fast synthesis or LLM.
        """
        logger.info(f"Executing support RAG search for query: '{query}'")

        # 1. FAISS similarity search with threshold
        search_results = vector_store_service.search(
            collection="knowledge",
            query=query,
            top_k=top_k,
            min_score=settings.SIMILARITY_THRESHOLD
        )

        if not search_results:
            logger.warning(f"No knowledge base documents exceeded similarity threshold ({settings.SIMILARITY_THRESHOLD}) for query: '{query}'")
            return self.FALLBACK_MESSAGE, [], False

        # 2. Extract context and construct source documents
        context_chunks = []
        sources: List[SourceDocument] = []
        combined_texts = []

        for meta, score in search_results:
            doc_title = meta.get("title", meta.get("source_file", "Policy Document"))
            content = meta.get("content", "")
            context_chunks.append(f"--- Document: {doc_title} ---\n{content}")
            combined_texts.append(content)
            sources.append(
                SourceDocument(
                    source_type="policy",
                    title=doc_title,
                    score=round(score, 3),
                    snippet=content[:200] + ("..." if len(content) > 200 else "")
                )
            )

        combined_context = "\n\n".join(context_chunks)
        all_text_lower = " ".join(combined_texts).lower()

        # 3. Guardrail: verify that specific substantive query concepts actually exist in the retrieved text
        unsupported_policy_patterns = [
            r'\binternational(?:\s+delivery|\s+shipping|\s+order|\s+courier)?\b',
            r'\boutside\s+india\b',
            r'\bship\s+(?:to\s+)?(?:usa|uk|canada|dubai|abroad)\b',
            r'\b(?:crypto|bitcoin|ethereum|paypal)\b',
            r'\b(?:submarine|moon|mars)\b'
        ]
        for pattern in unsupported_policy_patterns:
            if re.search(pattern, query.lower()):
                # Check if this concept is actually present in the retrieved context
                if not re.search(pattern, all_text_lower):
                    logger.info(f"Query matches unsupported concept not in KB: {pattern}")
                    return self.FALLBACK_MESSAGE, [], False
                elif "international" in pattern and "international delivery" not in all_text_lower and "international shipping" not in all_text_lower:
                    logger.info("International delivery/shipping is not supported in KB documents.")
                    return self.FALLBACK_MESSAGE, [], False

        # 4. Instant Fast Synthesis & LLM Fallback Pipeline
        top_doc = search_results[0][0]

        # Check if fast synthesis mode is active
        if settings.FAST_SYNTHESIS_MODE and not (settings.GEMINI_API_KEY or settings.GROQ_API_KEY):
            fast_answer = llm_service.synthesize_fast_support_answer(
                query=query,
                top_doc=top_doc,
                search_results=search_results
            )
            return fast_answer, sources, True

        # Otherwise attempt prompt generation with fast non-blocking fallback
        prompt = build_support_prompt(
            query=query,
            policy_context=combined_context,
            conversation_history=conversation_history
        )

        try:
            llm_text = await llm_service.generate_response(
                prompt=prompt,
                system=SYSTEM_PROMPT,
                temperature=0.1,
                max_tokens=150
            )
            if llm_text:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', llm_text.strip()) if s.strip()]
                answer = " ".join(sentences[:3]) if len(sentences) > 3 else llm_text.strip()
                return answer, sources, True
        except Exception as e:
            logger.warning(f"External LLM generation bypassed: {e}")

        # Deterministic grounded fallback in <1ms
        fast_answer = llm_service.synthesize_fast_support_answer(
            query=query,
            top_doc=top_doc,
            search_results=search_results
        )
        return fast_answer, sources, True


rag_service = RAGService()
