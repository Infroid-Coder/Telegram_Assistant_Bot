import re
import os
from asyncio import gather, get_event_loop, sleep

from aiohttp import ClientSession
from pyrogram import Client, filters, idle
from Python_ARQ import ARQ

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

Telegram_Assistant_Bot = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)

bot_id = int(bot_token.split(":")[0])
arq = None


async def Telegram_Assistant_BotQuery(query: str, user_id: int):
    query = (
        query
        if LANGUAGE == "en"
        else (await arq.translate(query, "en")).result.translatedText
    )
    resp = (await arq.Telegram_Assistant_Bot(query, user_id)).result
    return (
        resp
        if LANGUAGE == "en"
        else (
            await arq.translate(resp, LANGUAGE)
        ).result.translatedText
    )


async def type_and_send(message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    query = message.text.strip()
    await message._client.send_chat_action(chat_id, "typing")
    response, _ = await gather(Telegram_Assistant_BotQuery(query, user_id), sleep(2))
    await message.reply_text(response)
    await message._client.send_chat_action(chat_id, "cancel")


@Telegram_Assistant_Bot.on_message(filters.command("repo") & ~filters.edited)
async def repo(_, message):
    await message.reply_text(
        "[GitHub](https://github.com/SenuGamerBoy/Telegram_Assistant_Bot)"
        + " | [Group](t.me/senuinfinity)",
        disable_web_page_preview=True,
    )


@Telegram_Assistant_Bot.on_message(filters.command("help") & ~filters.edited)
async def start(_, message):
    await Telegram_Assistant_Bot.send_chat_action(message.chat.id, "typing")
    await sleep(2)
    await message.reply_text("/repo - Get Repo Link")


@Telegram_Assistant_Bot.on_message(
    ~filters.private
    & filters.text
    & ~filters.command("help")
    & ~filters.edited,
    group=69,
)
async def chat(_, message):
    if message.reply_to_message:
        if not message.reply_to_message.from_user:
            return
        from_user_id = message.reply_to_message.from_user.id
        if from_user_id != bot_id:
            return
    else:
        match = re.search(
            "[.|\n]{0,}Telegram_Assistant_Bot[.|\n]{0,}",
            message.text.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            return
    await type_and_send(message)


@Telegram_Assistant_Bot.on_message(
    filters.private & ~filters.command("help") & ~filters.edited
)
async def chatpm(_, message):
    if not message.text:
        return
    await type_and_send(message)


async def main():
    global arq
    session = ClientSession()
    arq = ARQ(ARQ_API_BASE_URL, ARQ_API_KEY, session)

    await Telegram_Assistant_Bot.start()
    print(
        """
-----------------------------------
| Telegram_Assistant_Bot Started! |
-----------------------------------
"""
    )
    await idle()


loop = get_event_loop()
loop.run_until_complete(main())
