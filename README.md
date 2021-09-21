# Mute user telegram bot

This is a bot that allows you to mute an user when he joins in a Telegram group for an amount of time.

## Configuration

The configuration is really simple: just copy the content of `configuration.env.example` in a new file `configuration.env` and change the parameters with your values.

| Parameter      | Description |
| ----------- | ----------- |
| * TELEGRAM_BOT_API_TOKEN * | This is the API token that BotFather will provide to you. It is secret.       |
| * SQLITE_DATABASE_PATH *  | This is the path to the database that will be created.        |
| * MUTE_TIME_OPTIONS * | This is the list of time options that you can setup with the bot. It is just a string of numbers separated by commas. |