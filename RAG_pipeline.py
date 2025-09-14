import logging
import weaviate
from config import Config
from document_retriever import WeaviateRetriever
from jan_ai_service import JanAIPromptNode
from prompt_templates import get_prompt
from tokenizer import Tokenizer
import asyncio
from conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

# This file contains the RAGPipeline class, which orchestrates the retrieval-augmented generation process.
class RAGPipeline:
    def __init__(self, max_history=20, max_tokens=32000):
        self.retriever = None
        self.prompt_node = None
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.tokenizer = Tokenizer()
        self.conversation_manager = ConversationManager()
        logger.info(f"RAGPipeline initialized with max_history={max_history}, max_tokens={max_tokens}")

    def initialize(self):
        """
        Initialize the RAG pipeline by setting up the retriever and prompt node. When the system starts, it connects
        to two important things: (1) a "retriever" (in this case, Weaviate); and (2) a "prompt node" (using Jan.AI
        API) that runs the LLM server.
        """
        try:
            client = weaviate.Client(Config.WEAVIATE_URL)
            self.retriever = WeaviateRetriever(client)
            self.prompt_node = JanAIPromptNode(
                api_url=Config.JANAI_API_URL,
                model_name=Config.JANAI_MODEL_NAME,
                max_retries=Config.MAX_RETRIES,
                base_delay=Config.BASE_DELAY,
                api_key=Config.JANAI_API_KEY
            )
            logger.info("RAGPipeline components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing the RAG pipeline: {e}", exc_info=True)
            raise

    def count_tokens(self, text):
        return self.tokenizer.estimate_tokens(text)

    async def summarize_conversation_chunk(self, chunk):
        summary_prompt = f"Summarize the following conversation chunk concisely, preserving key points:\n\n{chunk}"
        summary = await self.prompt_node.prompt(summary_prompt)
        return summary

    async def truncate_context(self, context, query, history):
        try:
            context_tokens = self.count_tokens(context)
            query_tokens = self.count_tokens(query)
            history_tokens = [self.count_tokens(msg['content']) for msg in history]

            total_tokens = context_tokens + query_tokens + sum(history_tokens)
            logger.info(f"Initial total tokens: {total_tokens}")

            # First, truncate context if necessary
            while total_tokens > self.max_tokens and context_tokens > 0:
                try:
                    context_words = context.split()
                    if len(context_words) <= 2:
                        logger.warning("Context too short to truncate further")
                        break
                    context = ' '.join(
                        context_words[len(context_words) // 8:-len(context_words) // 8])  # Remove first and last eighth
                    context_tokens = self.count_tokens(context)
                    total_tokens = context_tokens + query_tokens + sum(history_tokens)
                    logger.info(f"Truncated context. New context tokens: {context_tokens}")
                except Exception as e:
                    logger.error(f"Error during context truncation: {e}")
                    break

            # Now, apply sliding window summarization to history
            if total_tokens > self.max_tokens:
                try:
                    summarized_history = []
                    current_chunk = []
                    current_chunk_tokens = 0
                    chunk_token_limit = max(self.max_tokens // 4, 1)  # Ensure chunk_token_limit is at least 1

                    for msg in reversed(history):
                        try:
                            msg_tokens = self.count_tokens(msg['content'])
                            if current_chunk_tokens + msg_tokens <= chunk_token_limit:
                                current_chunk.insert(0, msg)
                                current_chunk_tokens += msg_tokens
                            else:
                                if current_chunk:
                                    chunk_text = "\n".join([f"{m['role']}: {m['content']}" for m in current_chunk])
                                    summary = await self.summarize_conversation_chunk(chunk_text)
                                    summarized_history.insert(0, {"role": "system", "content": f"Summary: {summary}"})
                                current_chunk = [msg]
                                current_chunk_tokens = msg_tokens
                        except Exception as e:
                            logger.error(f"Error processing message in history: {e}")
                            continue

                    if current_chunk:
                        summarized_history = current_chunk + summarized_history

                    history = summarized_history
                    history_tokens = [self.count_tokens(msg['content']) for msg in history]
                    total_tokens = context_tokens + query_tokens + sum(history_tokens)
                except Exception as e:
                    logger.error(f"Error during history summarization: {e}")
                    # If summarization fails, we'll return the original history
                    logger.warning("Returning original history due to summarization failure")

            logger.info(f"Final total tokens after truncation and summarization: {total_tokens}")
            return context, history

        except Exception as e:
            logger.critical(f"Unhandled error in truncate_context: {e}")
            # In case of a critical error, return the original context and history
            return context, history

    async def process_query(self, query: str, template: str) -> str:
        try:
            logger.info(f"Processing query: {query}")
            docs = self.retriever.retrieve(query, top_k=20)
            logger.debug(f"Retrieved {len(docs)} documents matching user query: {query}")
            context = "\n".join([f"Document {i + 1}: {doc['content']}" for i, doc in enumerate(docs)])

            self.conversation_manager.add_message("user", query)

            recent_history = self.conversation_manager.get_recent_messages(self.max_history)

            logger.debug("Recent persisted conversation history:")
            for msg in recent_history:
                logger.debug(f"  {msg['role']}: {msg['content'][:50]}...")

            truncated_context, truncated_history = await self.truncate_context(context, query, recent_history)

            logger.debug(f"Truncated context length: {len(truncated_context)}")
            logger.debug(f"Truncated history length: {len(truncated_history)}")

            logger.debug(f"Truncated conversation history:")
            for msg in truncated_history:
                logger.debug(f"  {msg['role']}: {msg['content'][:50]}...")  # Log first 50 chars of each message

            prompt = get_prompt(template, truncated_context, query, truncated_history)

            final_token_count = self.count_tokens(prompt)
            logger.debug(f"Final prompt token count: {final_token_count}")

            if final_token_count > self.max_tokens:
                logger.warning(f"Final prompt exceeds max tokens: {final_token_count} > {self.max_tokens}")
                return "I apologize, but the current query with context is too long for me to process. Could you please try a shorter query or provide less context?"

            response = await self.prompt_node.prompt(prompt)
            self.conversation_manager.add_message("assistant", response)
            logger.info("Query processed successfully")
            return response

        except Exception as e:
            logger.critical(f"Unhandled error in process_query: {e}", exc_info=True)
            return "I'm sorry, but I encountered an unexpected error. Please try again or contact support if the issue persists."
