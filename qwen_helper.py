import logging
import requests
import json

logger = logging.getLogger("bot")
logger.setLevel("DEBUG")


class QwenHelper:
    def __init__(self):
        logging.info(f"Initializing Qwen helper.")

    def get_response(self, text, context=None):
        url = "http://localhost:11434/api/chat"
        data = {
            "model": "qwen2.5:1.5b", 
            "messages": [
                {
                "role": "assistant",
                "content": context if context is not None else ""
                },
                {
                "role": "system",
                "content": "Next message message is the main one"
                },
                {
                "role": "user",
                "content": text
                },
            ],
            "stream" : True
        }

        response = requests.post(url, json=data , stream=True)
        if (response.status_code == 200):

            message_text = ''
            error_count = 0

            for line in response.iter_lines():
                try:
                    obj = json.loads(line)
                    if 'message' in obj and 'content' in obj['message']:
                        message_text += obj['message']['content']
                    else:
                        print("Skipping line: missing 'message' or 'content' key")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    error_count += 1
                except KeyError as e:
                    print(f"Missing key: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    error_count += 1

            if (error_count > 0) :
                print(f"Check. Too many errors ({error_count}) recorded.")
            
        return message_text
