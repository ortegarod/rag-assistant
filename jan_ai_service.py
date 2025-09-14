import logging
import random
import asyncio
import aiohttp
from aiohttp import ClientError

logger = logging.getLogger(__name__)

class JanAIPromptNode:
    def __init__(self, api_url: str, model_name: str, max_tokens=32000, max_retries: int = 3, base_delay: float = 1):
        self.api_url = api_url
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def prompt(self, prompt_text: str) -> str:
        messages = [{"role": "user", "content": prompt_text}]

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "max_tokens": self.max_tokens
        }

        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(self.api_url, json=payload) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                except aiohttp.ClientError as e:
                    logger.warning(f"Client error on attempt {attempt + 1}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    raise

                if attempt < self.max_retries - 1:
                    delay = (2 ** attempt + random.random()) * self.base_delay
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)

            logger.error(f"Failed to connect to Jan.ai API after {self.max_retries} attempts")
            raise Exception("Failed to connect to Jan.ai API")