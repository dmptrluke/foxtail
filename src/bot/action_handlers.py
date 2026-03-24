"""Action handlers for the Redis message queue.
Each handler receives (bot, payload_dict) and runs async."""


async def handle_send_message(bot, payload):
    await bot.send_message(
        chat_id=payload['telegram_id'],
        text=payload['text'],
    )


# registry: action type string -> async handler
ACTION_HANDLERS = {
    'send_message': handle_send_message,
}
