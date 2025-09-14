import logging
from logging_config import setup_logging
from RAG_pipeline import RAGPipeline
from prompt_templates import TEMPLATES
import asyncio

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


# This is the entry point of the application, handling user interactions and orchestrating the RAG process.
async def main():
    logger.info("Starting Jarvis AI assistant...")
    rag_pipeline = RAGPipeline()  # Initialize the RAG pipeline
    try:
        rag_pipeline.initialize()
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize the RAG pipeline. Error: {e}", exc_info=True)
        return

    # Print welcome message and available templates
    logger.info("Welcome to Jarvis, the personal AI assistant.")
    logger.info("This system can handle up to 32,000 tokens of context, allowing for detailed, contextual responses, "
                "in addition to its substantial general knowledge of the world.")
    logger.info("Type 'quit' to exit.")

    current_template = "default"  # not built out yet

    while True:
        user_input = input("\nEnter your question (or 'change template' or 'clear history'): ").strip()
        logger.debug(f"User input: {user_input}")

        if user_input.lower() == 'quit':
            logger.info("Exiting Jarvis AI assistant.")
            break
        elif user_input.lower() == 'change template':
            logger.info("Template change requested. This feature is not implemented yet.")
            continue
        elif user_input.lower() == 'clear history':
            try:
                rag_pipeline.conversation_manager.clear_history()
                logger.info("Conversation history cleared.")
            except Exception as e:
                logger.error(f"Failed to clear conversation history. Error: {e}", exc_info=True)
            continue

        logger.info(f"Processing query: {user_input}")
        try:
            answer = await rag_pipeline.process_query(user_input, current_template)
            print("\nAnswer:", answer)
            logger.info("Query processed successfully.")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            print("\nAn error occurred while processing your query. Please try again.")

    rag_pipeline.conversation_manager.summarize_old_conversations()
    rag_pipeline.conversation_manager.prune_old_conversations()

if __name__ == '__main__':
    asyncio.run(main())