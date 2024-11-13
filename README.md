### Предполагается, что указанное ниже будет дополнено информацией о развертывании и настройке модели Qwen2.5

### Getting started
* install requirements
```
$ pip install -r requirements.txt
```

### 
Регистрация для получения API ID и API HASH для доступа к tg API: https://core.telegram.org/api/obtaining_api_id.
Модель загруженная через ollama в запущенном виде для работы бота не требуется.
WEB_HOOK_HOST - адрес выданный в результате вызова ssh -R 80:127.0.0.1:<port> nokey@localhost.run (порт если не меняете в боте ставьте 5000).

* export environment variables
```
$ ollama run qwen2.5:1.5b
$ ssh -R 80:127.0.0.1:<port> nokey@localhost.run
$ export WEB_HOOK_HOST=...
$ export TELEGRAM_TOKEN=...
$ export TELEGRAM_CORE_API_ID=...
$ export TELEGRAM_CORE_API_HASH=...
```
optional: set application port (as `TELEGRAM_BOT_PORT` mast be same as port in ssh command)

* run main.py
```
python main.py
```
