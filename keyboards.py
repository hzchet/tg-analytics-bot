from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from UI import ui_messages


def send_language_markup(bot, chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('English', callback_data='en'),
        InlineKeyboardButton('Русский', callback_data='ru')
    )
    bot.send_message(
        chat_id,
        ui_messages.SELECT_LANGUAGE,
        reply_markup=markup
    )


def send_stats_markup_en(bot, chat_id):
    markup = InlineKeyboardMarkup()
    item_post = InlineKeyboardButton('Stats by posts', callback_data='post_en')
    item_views = InlineKeyboardButton('Stats by views', callback_data='views_en')
    item_text = InlineKeyboardButton('Stats by texts', callback_data='text_en')
    markup.add(item_post)
    markup.add(item_views)
    markup.add(item_text)
    bot.send_message(chat_id, 'Select the type of stats', reply_markup=markup)


def send_stats_markup_ru(bot, chat_id):
    markup = InlineKeyboardMarkup()
    item_post = InlineKeyboardButton('Статистика по постам', callback_data='post_ru')
    item_views = InlineKeyboardButton('Статистика по просмотрам', callback_data='views_ru')
    item_text = InlineKeyboardButton('Статистика по текстам', callback_data='text_ru')
    markup.add(item_post)
    markup.add(item_views)
    markup.add(item_text)
    bot.send_message(chat_id, 'Выбери тип статистики', reply_markup=markup)
