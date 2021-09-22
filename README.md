# Mute user telegram bot

This is a bot that allows you to mute, and then to automatically unmute, for an amount of time an user when he joins in a Telegram (super)group. This bot **must be an administrator** of the group in order to mute users.

## Configuration

The configuration is really simple: just copy the content of `configuration.env.example` in a new file `configuration.env` and change the parameters with your values.

| Parameter      | Description |
| ----------- | ----------- |
| **TELEGRAM_BOT_API_TOKEN** | This is the API token that BotFather will provide to you. It is secret.       |
| **SQLITE_DATABASE_PATH**  | This is the path to the database that will be created.        |
| **MUTE_TIME_OPTIONS** | This is the list of time options that you can setup with the bot. It is just a string of numbers separated by commas. |


## How can I run it?

You can run it just by launching the command: **`python main.py`**. It will create a new database with the `bot_settings` table that contains two fields: `enabled` (a boolean to save the bot status) and `mute_time` that represents the time that the user will be muted when join into the group.

Feel free to contribute to the repository :)!
