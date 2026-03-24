from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name='ping')


@router.message(Command('ping'))
async def cmd_ping(message: Message):
    await message.answer('pong')
