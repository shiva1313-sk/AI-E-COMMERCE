def build_support_prompt(query: str, policy_context: str, conversation_history: str = "") -> str:
    """
    Construct a strictly grounded prompt for customer support policy queries.
    Enforces maximum 1-3 short sentences (50-80 words maximum).
    """
    return f"""You are answering a customer support question for ShopEase using only the verified policy documentation below.

### VERIFIED POLICY KNOWLEDGE BASE CONTEXT:
{policy_context}

### PREVIOUS CONVERSATION CONTEXT:
{conversation_history if conversation_history else "No previous conversation."}

### CUSTOMER QUESTION:
"{query}"

### INSTRUCTIONS:
1. Answer the customer's question directly and concisely in 1 to 3 short sentences (maximum 50-80 words).
2. Answer ONLY using the facts present in the policy context above. Include specific numbers or timelines (e.g. 7-day return window, 24-48 hour refund, 1-year warranty) if stated.
3. Do NOT provide long explanations, bulleted guides, or reproduce entire policy documents.
4. If the question cannot be answered from the provided context, you MUST respond:
   "I don't have enough information in the available knowledge base to answer that question."
5. Never invent or assume facts, policies, or international shipping options not explicitly present in the text.
"""
