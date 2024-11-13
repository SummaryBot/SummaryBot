import asyncio
import logging

import hypercorn.asyncio
from quart import Quart, request

from config import Config
from data_models import Update
from qwen_helper import QwenHelper
from telegram_bot import TelegramBotBuilder

logger = logging.getLogger("bot")
logger.setLevel("DEBUG")

app = Quart(__name__)


@app.route("/", methods=["GET", "POST"])
async def handle_webhook():
    try:
        json_data = await request.json
        logger.info(f"Handling a webhook: {json_data}")
        update = Update(**json_data)
        chat_id = update.message.chat.id

        if update.message.text.startswith("/summarize"):
            history = await app.bot.get_chat_history(chat_id)
            response = app.qwen_helper.get_response(
                f"Summarize the following text in Russian: {history}"
            )
        elif update.message.text.startswith("/chat"):
            response = app.qwen_helper.get_response(
                f"{update.message.text.replace('/chat', '')} (reply in Russian)"
            )
        else:
            return "OK", 200

        app.bot.send_message(chat_id, response)

        return "OK", 200
    except Exception as e:
        logger.error(f"Something went wrong while handling a request: {e}")
        return "Something went wrong", 500


@app.before_serving
async def startup():
    bot_builder = (
        TelegramBotBuilder(Config.TELEGRAM_TOKEN)
        .with_webhook(Config.HOST)
        .with_core_api(Config.TELEGRAM_CORE_API_ID, Config.TELEGRAM_CORE_API_HASH)
    )

    app.bot = bot_builder.get_bot()
    app.qwen_helper = QwenHelper()

    if app.bot.core_api_client:
        await app.bot.core_api_client.connect()
        await app.bot.core_api_client.start()


async def main():
    quart_cfg = hypercorn.Config()
    quart_cfg.bind = [f"127.0.0.1:{Config.PORT}"]
    logger.info("Starting the application")
    await hypercorn.asyncio.serve(app, quart_cfg)


if __name__ == "__main__":
    asyncio.run(main())
