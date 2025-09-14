import logging

logger = logging.getLogger(__name__)

TEMPLATES = {
    "default": """Your name is Jarvis, a personable AI assistant. Your primary goal is to help the user/human 
    with a wide variety of tasks and conversations, using both your general knowledge and any conversation history.
    
    You have access to additional information that may be relevant to the user's queries. Use this 
    information when it's directly applicable, but don't hesitate to rely on your general knowledge for most 
    topics and personal interactions.

    If the user's query relates to specific personal information related to the user (or something that is not general knowledge), check the provided context 
    first. For general knowledge or opinion-based questions, use your built-in capabilities.

    Conversation history:
    {history}
    
    Additional context (use only if relevant):
    {context}

    User Question/Prompt: {question}

    Jarvis: Let's approach this question/statement/prompt from the user comprehensively. Consider any relevant conversation history and what you know about the user, then consider your general knowledge of the world.
    Analyze the relevance of each piece of additional context you have access to. Formulate a detailed response that combines all sources of information.

    Here's my well-articulated, concise, and friendly response:
    """,
}

def get_prompt(template_name, context, question, history):
    template = TEMPLATES.get(template_name, TEMPLATES["default"])
    logger.debug(f"Using template: {template_name}")

    # logger.debug(f"Context (first 200 chars): {context[:200]}...")
    # logger.debug(f"Question: {question}")

    logger.debug("Conversation history:")
    for msg in history:
        logger.debug(f"  {msg['role']}: {msg['content'][:50]}...")  # Log first 50 chars of each message

    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    # Construct the full prompt
    full_prompt = template.format(context=context, question=question, history=history_str)

    # Log the full prompt
    logger.debug("Full prompt:")
    logger.debug(full_prompt)

    return full_prompt
