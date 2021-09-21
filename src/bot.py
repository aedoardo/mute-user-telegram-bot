import sqlite3
from telegram import Update, ForceReply, ChatMemberUpdated, ChatMember
from telegram.callbackquery import CallbackQuery
from telegram.chat import Chat
from telegram.chatpermissions import ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ChatMemberHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from .database import Database
from datetime import datetime, timedelta, tzinfo
from typing import Tuple, Optional
import json

class Bot:

    def __init__(self, telegram_token: str, database_path: str) -> None:
        self.token = telegram_token
        self.database = Database(database_path)
        self.connection = self.database.connection
        self.setup_bot()
    

    def setup_bot(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bot_settings'") # check if table 'bot_settings' exists
        data = cursor.fetchall() # fetch the query
        if len(data) == 0:
            # we do not have a bot_settings table, just create it.
            cursor = self.connection.cursor()
            cursor.execute("CREATE TABLE bot_settings (enabled INT NOT NULL, mute_time INT NOT NULL);")
            self.connection.commit()
            cursor.execute("INSERT INTO bot_settings (enabled, mute_time) VALUES (0, 5);")
            self.connection.commit()
            print("[BOT] => Settings table created successfully")
            self.enabled = 0 # initially, setup enabled to 0 
            self.mute_time = 300 # default mute time is 5 minutes.
        else:
            cursor.execute("SELECT * FROM bot_settings")
            data = cursor.fetchall()[0] # we will have only one row.
            self.enabled = data[0]
            self.mute_time = data[1]
            print("[BOT] => Bot settings loaded successfully")


    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text("Hi, *thank you* for adding me to this group! Don't forget to make me administrator. \nYou can enable the bot by clicking \"*Enable bot*\" and you can change the settings by clicking \"*Bot settings*\".", reply_markup=self.build_main_keyboard(self.enabled), parse_mode="Markdown")


    def extract_status_change(self, chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
        status_change = chat_member_update.difference().get("status")
        old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

        if status_change is None:
            return None
        
        old_status, new_status = status_change

        was_member = (old_status in [ChatMember.MEMBER, ChatMember.CREATOR, ChatMember.ADMINISTRATOR] or (old_status == ChatMember.RESTRICTED and old_is_member is True))
        is_member = (new_status in [ChatMember.MEMBER, ChatMember.CREATOR, ChatMember.ADMINISTRATOR] or (new_status == ChatMember.RESTRICTED and new_is_member is True))

        return was_member, is_member


    def user_event(self, update: Update, context: CallbackContext) -> None:

        if not self.enabled: # if the bot isn't enabled
            return None

        result = self.extract_status_change(update.chat_member)
        if result is None:
            return None

        was_member, is_member = result

        if not was_member and is_member:
            # added user!
            user = update.chat_member.new_chat_member.user
            chat = update.chat_member.chat
            if not user.is_bot:
                context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(
                    can_send_media_messages=False,
                    can_send_messages=False,
                    can__send_other_messages=False,
                    can_add_web_page_previews=False
                ), until_date=datetime.utcnow() + timedelta(seconds=self.mute_time))
                
      
    def button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        data = json.loads(query.data)
        if data["callback"] == "update_enabled":
            self.update_enabled(query)
        elif data["callback"]  == "bot_settings":
            self.bot_settings(query)
        elif data["callback"] == "set_time":
            self.set_time(query, int(data["seconds"]))
        
        query.answer()


    def set_time(self, query: CallbackQuery, seconds: int) -> None:
        if self.mute_time != seconds: # do not spam queries.
            self.mute_time = seconds
            cursor = self.connection.cursor()
            cursor.execute("UPDATE bot_settings SET mute_time = ?", (seconds, ))
            self.connection.commit()

        query.edit_message_reply_markup(reply_markup=self.build_main_keyboard(self.enabled))


    def bot_settings(self, query: CallbackQuery) -> None:
        # if mute time < 30 seconds or > 366 days -> it will be a permanent mute.
        keyboard = []
        options = [30, 60, 120, 300, 600] # add here some seconds if u want :D

        for option in options:
            text_appended = ""
            icon = " ✔️" if option == self.mute_time else " ❌"
            if option < 60:
                text_appended = "{} seconds".format(str(option))
            elif option == 60:
                text_appended = "one minute"
            else:
                text_appended = "{} minutes".format(str(round(option / 60)))
            
            keyboard.append(
                [
                    InlineKeyboardButton("Mute user for " + text_appended + icon, callback_data=json.dumps({"callback": "set_time", "seconds": option}))
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    
    def update_enabled(self, query: CallbackQuery) -> None:
        cursor = self.connection.cursor()
        cursor.execute("UPDATE bot_settings SET enabled = NOT enabled")
        self.connection.commit()
        query.answer()

        self.enabled = not self.enabled
        query.edit_message_reply_markup(reply_markup=self.build_main_keyboard(self.enabled))


    def build_main_keyboard(self, enabled) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton("Bot enabled ✔️" if enabled else "Bot enabled ❌", callback_data=json.dumps({"callback": "update_enabled"})),
                InlineKeyboardButton("Bot settings ⚙️", callback_data=json.dumps({"callback": "bot_settings"}))
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup


    def main(self) -> None:

        updater = Updater(self.token) # create the Updater and pass it the bot's token.
        dispatcher = updater.dispatcher 

        dispatcher.add_handler(ChatMemberHandler(self.user_event, ChatMemberHandler.CHAT_MEMBER))
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CallbackQueryHandler(self.button))

        updater.start_polling(allowed_updates=Update.ALL_TYPES)

        updater.idle()