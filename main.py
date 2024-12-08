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
        message_id = update.message.message_id
        user = json_data["message"]["from"]["first_name"] + " " + json_data["message"]["from"]["last_name"]
        text = update.message.text

        if text.startswith("/summarize_"):
            limit = None
            try:
                limit = int(text.split("_")[1])
                print("limit", limit)
                if limit <= 0:
                    limit = None
            except:
                print("ooops")
                pass
            history = app.bot.get_chat_history(chat_id, limit)
            response = app.qwen_helper.get_response(
                f"Summarize the following text in Russian: {history}"
            )
        elif text.startswith("/summarize"):
            history = app.bot.get_chat_history(chat_id)
            app.bot.set_last_summarized_id(chat_id, message_id)
            response = app.qwen_helper.get_response(
                f"Summarize the following text in Russian: {history}"
            )
        elif text.startswith("/chat"):
            text = text.replace('/chat', '')
            history = app.bot.get_chat_history(chat_id, 10)
            response = app.qwen_helper.get_response(
                f"{text} (reply in Russian)", history
            )
            app.bot.register_message(chat_id, message_id, user, text)
        else:
            app.bot.register_message(chat_id, message_id, user, text)
            return "OK", 200

        app.bot.send_message(chat_id, message_id, response)

        return "OK", 200
    except Exception as e:
        logger.error(f"Something went wrong while handling a request: {e}")
        return "OK", 200 # код успеха, чтобы не было проблем со стороны телеграмма (просто игнорируем)


@app.before_serving
async def startup():
    bot_builder = (
        TelegramBotBuilder(Config.TELEGRAM_TOKEN)
        .with_webhook(Config.HOST)
    )

    app.bot = bot_builder.get_bot()
    app.qwen_helper = QwenHelper()


async def main():
    quart_cfg = hypercorn.Config()
    quart_cfg.bind = [f"127.0.0.1:{Config.PORT}"]
    logger.info("Starting the application")
    await hypercorn.asyncio.serve(app, quart_cfg)


if __name__ == "__main__":
    asyncio.run(main())
