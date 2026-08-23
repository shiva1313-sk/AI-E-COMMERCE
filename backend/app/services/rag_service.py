import re
from typing import List, Optional, Tuple
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.chat import SourceDocument
from backend.app.services.vector_store_service import vector_store_service
from backend.app.services.ollama_service import ollama_service
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
        4. Synthesize short (1-3 sentences) answer with Ollama using retrieved chunks.
        5. If Ollama is unavailable -> generate direct grounded summary from top snippet.
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
        # (prevents false matches when generic terms like 'delivery' match but specific modifiers like 'international delivery' are absent)
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

        # 4. Prompt Construction
        prompt = build_support_prompt(
            query=query,
            policy_context=combined_context,
            conversation_history=conversation_history
        )

        # 5. LLM Generation via Ollama
        try:
            raw_answer = await ollama_service.generate(
                prompt=prompt,
                system=SYSTEM_PROMPT,
                temperature=0.1
            )
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_answer.strip()) if s.strip()]
            if len(sentences) > 3:
                answer = " ".join(sentences[:3])
            else:
                answer = raw_answer.strip()
            return answer, sources, True
        except Exception as e:
            logger.warning(f"Ollama generation unavailable ({e}). Generating direct grounded answer from knowledge base snippets.")
            # Deterministic fallback: extract relevant lines containing query keywords from top chunk
            top_doc = search_results[0][0]
            top_content = top_doc.get("content", "").strip()
            lines = [l.strip().lstrip("-*# ") for l in top_content.split("\n") if l.strip() and not l.startswith("#")]
            
            query_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', query)]
            # Find lines that match query words
            matching_lines = []
            for line in lines:
                if any(qw in line.lower() for qw in query_words if qw not in {"delivery", "return", "warranty", "refund", "order", "what", "how", "can", "the"}):
                    matching_lines.append(line)
            
            if not matching_lines:
                matching_lines = lines[:2]

            snippet_summary = " ".join(matching_lines[:2])
            fallback_answer = f"According to our {top_doc.get('document', 'policy')}, {snippet_summary}"
            return fallback_answer, sources, True


rag_service = RAGService()
