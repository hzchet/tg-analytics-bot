import json
import random

import telebot
from telethon.errors.rpcbaseerrors import FloodError, InvalidDCError

from UI import ui_messages, keyboards
from data_managing.Shelver import Shelver
from channel_parser.ChannelDataCollector import DataCollector

JSON_PATH = 'data_managing/secret_data.json'
POST_LIMIT = 10_000

with open(JSON_PATH, 'r') as json_file:
    API_TOKEN = json.load(json_file)['token']

bot = telebot.TeleBot(API_TOKEN, threaded=False)
collector = DataCollector.from_config(JSON_PATH, limit=POST_LIMIT)
database = Shelver('data_managing/user_info.db')
print('Initializing finished')


# Interaction with a user
@bot.message_handler(commands=['start'])
def handle_start(message):
    lang = database.get_language(message.chat.id)
    if lang == 'en':
        bot.send_message(message.chat.id, ui_messages.WELCOME_EN)
    elif lang == 'ru':
        bot.send_message(message.chat.id, ui_messages.WELCOME_RU)
    else:
        keyboards.send_language_markup(bot, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'en')
def set_english(call):
    lang = database.get_language(call.from_user.id)
    if lang is None:
        bot.send_message(call.from_user.id, ui_messages.WELCOME_EN)
    else:
        bot.send_message(call.from_user.id, ui_messages.LANGUAGE_SET_EN)
    database.set_language(call.from_user.id, 'en')


@bot.callback_query_handler(func=lambda call: call.data == 'ru')
def set_russian(call):
    lang = database.get_language(call.from_user.id)
    if lang is None:
        bot.send_message(call.from_user.id, ui_messages.WELCOME_RU)
    else:
        bot.send_message(call.from_user.id, ui_messages.LANGUAGE_SET_RU)
    database.set_language(call.from_user.id, 'ru')


@bot.message_handler(commands=['help'])
def send_help(message):
    lang = database.get_language(message.chat.id)
    if lang == 'en':
        bot.send_message(message.chat.id, ui_messages.HELP_EN, parse_mode='markdown')
    elif lang == 'ru':
        bot.send_message(message.chat.id, ui_messages.HELP_RU, parse_mode='markdown')
    else:
        keyboards.send_language_markup(bot, message.chat.id)


@bot.message_handler(commands=['setlanguage'])
def handle_setlanguage(message):
    keyboards.send_language_markup(bot, message.chat.id)


@bot.message_handler(regexp='^https://t.me/')
def handle_wrong_query(message):
    language = database.get_language(message.chat.id)
    if language is None:
        keyboards.send_language_markup(bot, message.chat.id)
    elif language == 'en':
        bot.send_message(message.chat.id, ui_messages.FORGOT_ANALYZE_EN, parse_mode='markdown')
    else:
        bot.send_message(message.chat.id, ui_messages.FORGOT_ANALYZE_RU, parse_mode='markdown')


# Queries handling
@bot.message_handler(regexp='^/analyze')
def handle_analyze_query(message):
    lang = database.get_language(message.chat.id)
    if lang is None:
        keyboards.send_language_markup(bot, message.chat.id)
    elif message.text.strip() == '/analyze':  # if user just typed /analyze without the link
        if lang == 'en':
            bot.send_message(message.chat.id, ui_messages.FORGOT_LINK_EN, parse_mode='markdown')
        elif lang == 'ru':
            bot.send_message(message.chat.id, ui_messages.FORGOT_LINK_RU, parse_mode='markdown')
    else:
        channel_username = message.text.strip().split(' ')[-1]
        try:
            path = database.get_path(message.chat.id)
            collector.load_data(channel_username, path=path)
            database.set_analyzer(message.chat.id)
            if lang == 'en':
                bot.reply_to(message, ui_messages.CHANNEL_ANALYZED_EN)
            elif lang == 'ru':
                bot.reply_to(message, ui_messages.CHANNEL_ANALYZED_RU)
        except ValueError:
            if lang == 'en':
                bot.reply_to(message, ui_messages.CHANNEL_NOT_FOUND_EN)
            elif lang == 'ru':
                bot.reply_to(message, ui_messages.CHANNEL_NOT_FOUND_RU)
        except (ConnectionError, FloodError, InvalidDCError):
            if lang == 'en':
                bot.reply_to(message, ui_messages.SOMETHING_WENT_WRONG_EN)
            elif lang == 'ru':
                bot.reply_to(message, ui_messages.SOMETHING_WENT_WRONG_RU)


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    print('handle_stats entered')
    language = database.get_language(message.chat.id)
    if language == 'ru':
        keyboards.send_stats_markup_ru(bot, message.chat.id)
    elif language == 'en':
        keyboards.send_stats_markup_en(bot, message.chat.id)
    else:
        keyboards.send_language_markup(bot, message.chat.id)


def is_ready_to_get_stats(chat_id) -> bool:
    language = database.get_language(chat_id)
    if language is None:
        keyboards.send_language_markup(bot, chat_id)
        return False
    if not database.is_analyzer_set(chat_id):
        if language == 'en':
            bot.send_message(chat_id, ui_messages.SEND_QUERY_EN, parse_mode='markdown')
        elif language == 'ru':
            bot.send_message(chat_id, ui_messages.SEND_QUERY_RU, parse_mode='markdown')
        return False
    return True


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'post')
def send_post_stats(call):
    print('send_post_stats entered')
    if is_ready_to_get_stats(call.from_user.id):
        analyzer = database.get_analyzer(call.from_user.id)
        language = database.get_language(call.from_user.id)
        analyzer.send_post_stats(bot, language)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'views')
def send_views_stats(call):
    print('send_views_stats entered')
    if is_ready_to_get_stats(call.from_user.id):
        analyzer = database.get_analyzer(call.from_user.id)
        language = database.get_language(call.from_user.id)
        analyzer.send_views_stats(bot, language)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'text')
def send_text_stats(call):
    print('send_text_stats entered')
    if is_ready_to_get_stats(call.from_user.id):
        language = database.get_language(call.from_user.id)
        if language == 'en':
            bot.send_message(call.from_user.id, ui_messages.WAIT_EN)
        else:
            bot.send_message(call.from_user.id, ui_messages.WAIT_RU)
        analyzer = database.get_analyzer(call.from_user.id)
        analyzer.send_text_stats(bot, language)


# Unknown commands handling
@bot.message_handler(func=lambda message: True)
def handle_unknown_commands(message):
    lang = database.get_language(message.chat.id)
    if lang == 'en':
        bot.send_message(
            message.chat.id,
            *random.sample(ui_messages.UNKNOWN_COMMAND_EN, 1)
        )
    elif lang == 'ru':
        bot.send_message(
            message.chat.id,
            *random.sample(ui_messages.UNKNOWN_COMMAND_RU, 1)
        )
    else:
        keyboards.send_language_markup(bot, message.chat.id)


if __name__ == '__main__':
    bot.polling()
