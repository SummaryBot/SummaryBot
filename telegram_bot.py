import logging
import os
from json import load, dump

import requests

from config import Config

logger = logging.getLogger("bot")
logger.setLevel("DEBUG")


class TelegramBotBuilder:
    def __init__(self, token):
        logger.info("Building a new bot.")
        self.bot = TelegramBot(token)

    def with_webhook(self, host):
        self.bot.set_webhook(host)
        return self

    def get_bot(self):
        return self.bot


class TelegramBot:
    dump_file = "messages.json"


    def __init__(self, token):
        self.token = token
        self.bot_api_url = f"{Config.TELEGRAM_API}/bot{self.token}"
        self.messages = {
            "chats": {}
        }
        if os.path.exists(TelegramBot.dump_file):
            with open(TelegramBot.dump_file, "r") as f:
                self.messages = load(f)

    def set_webhook(self, host):
        try:
            logger.info(f"Setting webhook for url: {host}")
            set_webhook_url = f"{self.bot_api_url}/setWebhook?url={host}"

            response = requests.get(set_webhook_url)
            response.raise_for_status()
            logger.info(f"Got response: {response.json()}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")

    def register_message(self, chat_id, message_id, user, message):
        if str(chat_id) not in self.messages["chats"]:
            self.messages["chats"][str(chat_id)] = {
                "messages": {},
                "last_summirized_id": None,
                "messages_order": []
            }
        self.messages["chats"][str(chat_id)]["messages"][str(message_id)] = {
            "id": message_id,
            "user": user,
            "message": message,
            "response": None
        }
        self.messages["chats"][str(chat_id)]["messages_order"].append(message_id)
        with open(TelegramBot.dump_file, "w") as f:
            dump(self.messages, f)

    def send_message(self, chat_id, message_id, text):
        try:
            logger.info(f"Sending message to chat #{chat_id}")
            send_message_url = f"{self.bot_api_url}/sendMessage"
            response = requests.post(
                send_message_url, json={"chat_id": chat_id, "text": text}
            )
            response.raise_for_status()
            if str(chat_id) not in self.messages["chats"]:
                self.messages["chats"][str(chat_id)] = {
                    "messages": {},
                    "last_summirized_id": None,
                    "messages_order": []
                }
            if str(message_id) not in self.messages["chats"][str(chat_id)]["messages"]:
                self.messages["chats"][str(chat_id)]["messages"][str(message_id)] = {
                    "id": message_id,
                    "user": None,
                    "message": None,
                    "response": text
                }
                self.messages["chats"][str(chat_id)]["messages_order"].append(message_id)
            else:
                self.messages["chats"][str(chat_id)]["messages"][str(message_id)]["response"] = text
            with open(TelegramBot.dump_file, "w") as f:
                dump(self.messages, f)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def set_last_summarized_id(self, chat_id, message_id):
        self.messages["chats"][str(chat_id)]["last_summirized_id"] = message_id

    def get_chat_history(self, chat_id, limit=None):
        try:
            print("history limit", limit)
            logger.info(f"Getting conversation history for chat #{chat_id}")
            ids: list = self.messages["chats"][str(chat_id)]["messages_order"].copy()
            history = []
            if limit is None:
                last_id = self.messages["chats"][str(chat_id)]["last_summirized_id"]
                if not last_id:
                    start_pos = 0
                else:
                    start_pos = 0
                    for i in ids:
                        if i > last_id:
                            break
                        start_pos += 1
                for i in range(start_pos, len(ids)):
                    cur_id = str(ids[i])
                    if self.messages["chats"][str(chat_id)]["messages"][cur_id]["message"] is not None:
                        history.append(self.messages["chats"][str(chat_id)]["messages"][cur_id]["user"] + ": " + self.messages["chats"][str(chat_id)]["messages"][cur_id]["message"])
                    if self.messages["chats"][str(chat_id)]["messages"][cur_id]["response"] is not None:
                        history.append("ChatSummarizerBot: " + self.messages["chats"][str(chat_id)]["messages"][cur_id]["response"])
            else:
                ids.reverse()
                for cur_id in ids:
                    if len(history) >= limit:
                        break
                    cur_id = str(cur_id)
                    if self.messages["chats"][str(chat_id)]["messages"][cur_id]["response"] is not None:
                        history.append("ChatSummarizerBot: " + self.messages["chats"][str(chat_id)]["messages"][cur_id]["response"])
                        if len(history) >= limit:
                            break
                    if self.messages["chats"][str(chat_id)]["messages"][cur_id]["message"] is not None:
                        history.append(self.messages["chats"][str(chat_id)]["messages"][cur_id]["user"] + ": " + self.messages["chats"][str(chat_id)]["messages"][cur_id]["message"])
                history.reverse()
            print("history len", len(history))
            print(history)
            if len(history) == 0:
                result = ""
            else:
                result = "\n".join(history)
            return result
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return ""
