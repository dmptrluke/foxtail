import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class ActionListener:
    """Listens for actions from the web app via Redis BLPOP."""

    def __init__(self, bot, handlers, redis_url):
        self.bot = bot
        self.handlers = handlers
        self.redis = aioredis.from_url(redis_url)

    async def run(self):
        logger.info('Action listener started')
        while True:
            _, data = await self.redis.blpop('bot:actions')
            payload = json.loads(data)
            action = payload.pop('action', None)
            handler = self.handlers.get(action)
            if not handler:
                logger.warning('Unknown action type: %s', action)
                continue
            try:
                await handler(self.bot, payload)
                logger.info('Action %s completed', action)
            except Exception:
                logger.exception('Action %s failed', action)

    async def close(self):
        await self.redis.aclose()
