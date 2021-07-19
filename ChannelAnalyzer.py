from telebot import TeleBot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud


class Analyzer:
    def __init__(self):
        self._df = pd.DataFrame()
        self._chat_id = ''
        self._text_df = pd.DataFrame()
        self._PLOTS_PATH = '/home/aidar/PycharmProjects/tg-bot/channel_parser/channels_plots/{}.png'

    def read_data(self, path: str, chat_id):
        self._chat_id = chat_id
        self._df = pd.read_csv(path)
        self.__preprocess_data()

    def is_data_read(self) -> bool:
        return not self._df.empty

    @staticmethod
    def __tokenize(text):
        # you should uncomment code below, if you're running it for the first time
        # nltk.download('punkt')
        # nltk.download('stopwords')
        tokens = nltk.word_tokenize(text)
        stop_words = stopwords.words('english')
        stop_words.extend(stopwords.words('russian'))
        stop_words.extend([
            'это', '.', ',', 'то', 'например', 'которые', 'который', '*', '`',
            'которые', '/', '\\', '(', ')', ':', ';', '!', '?', '-', '#', '%', '$',
            '``', ']', '[', '{', '}', '~', '|', ' ', 'http', '├', '--', '<', '>', 'хочу', 'очень',
            'либо', 'или', 'что', 'кто', 'то', 'поэтому', '+', '«', '»', '__что', '_', '__',
            '=', '\'', '\'\'', '&', '−', '—', '^', '"', '`'
        ])
        tokens = [token.replace('"', '') for token in tokens if token not in stop_words]
        return ' '.join(tokens)

    @staticmethod
    def __remove_links_and_ats(text):
        try:
            return ' '.join(
                [word for word in text.split() if 'http' not in word and '@' not in word]
            )
        except AttributeError:
            pass

    @staticmethod
    def __set_plotting_config(title, xlabel, ylabel):
        plt.title(label=title, fontsize=26)
        plt.xlabel(xlabel=xlabel, fontsize=16)
        plt.ylabel(ylabel=ylabel, fontsize=16)

    def __preprocess_data(self):
        self._df['date'] = pd.to_datetime(self._df['date'])
        self._df.sort_values(by='date', inplace=True, ascending=True)
        self._df['text'].fillna('', inplace=True)

    def __get_total_views(self):
        total_views = pd.pivot_table(
            self._df, columns=['date'], values='views', aggfunc=np.sum
        ).T
        total_views.reset_index(inplace=True)
        return total_views

    def __get_corpus(self):
        corpus = self._df[['text']]
        corpus['text'] = corpus['text'].str.lower()
        corpus['text'] = corpus['text'].apply(lambda x: self.__remove_links_and_ats(x))
        corpus['text'] = corpus['text'].apply(lambda x: self.__tokenize(x))
        return corpus

    # post plots
    def __plot_post_dynamic_overall(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        total_history = self._df['date'].dt.date.sort_values()
        if language == 'en':
            title = 'Post Dynamic'
            xlabel = 'Date'
            ylabel = 'Posts count'
            label = 'Overall posts'
        else:
            title = 'Динамика постов'
            xlabel = 'Дата'
            ylabel = 'Количество постов'
            label = 'Посты за все время'
        total_history.value_counts().sort_index().cumsum().plot(figsize=(22, 8), label=label)
        self.__set_plotting_config(title, xlabel, ylabel)
        plt.legend(fontsize=16)
        all_posts = self._PLOTS_PATH.format('all_posts_' + str(self._chat_id))

        plt.savefig(all_posts)
        plt.close()
        return all_posts

    def __plot_post_dynamic_by_days(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        if language == 'en':
            title = 'Number of posts by days'
            xlabel = 'Date'
            ylabel = 'Posts count'
        else:
            title = 'Количество постов по дням'
            xlabel = 'Дата'
            ylabel = 'Количество постов'
        self._df.groupby(self._df['date'].dt.date).count()['date'].plot(figsize=(24, 5))
        by_days_posts = self._PLOTS_PATH.format('by_days_posts_' + str(self._chat_id))
        self.__set_plotting_config(title, xlabel, ylabel)
        plt.savefig(by_days_posts)
        plt.close()
        return by_days_posts

    def __plot_post_dynamic_by_hours(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        if language == 'en':
            title = 'Number of posts by hours'
            xlabel = 'Hour'
            ylabel = 'Posts count'
        else:
            title = 'Количество постов по часам'
            xlabel = 'Час дня'
            ylabel = 'Количество постов'
        self._df.groupby(
            self._df['date'].dt.tz_convert('Europe/Moscow').dt.hour
        ).count()['date'].plot(figsize=(24, 5))
        plt.xticks(range(24))
        self.__set_plotting_config(title, xlabel, ylabel)
        by_hours_posts = self._PLOTS_PATH.format('by_hours_posts_' + str(self._chat_id))
        plt.savefig(by_hours_posts)
        plt.close()
        return by_hours_posts

    # views plots
    def __plot_views_dynamic_overall(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        if language == 'en':
            title = 'Views dynamic'
            xlabel = 'Date'
            ylabel = 'Views count'
            label = 'Overall views'
        else:
            title = 'Динамика просмотров'
            xlabel = 'Дата'
            ylabel = 'Количество просмотров'
            label = 'Все просмотры'
        self.__set_plotting_config(title, xlabel, ylabel)
        self.__get_total_views()['views'].cumsum().plot(figsize=(22, 8), label=label)
        plt.legend(fontsize=16)
        all_views = self._PLOTS_PATH.format('all_views_' + str(self._chat_id))
        plt.savefig(all_views)
        plt.close()
        return all_views

    def __plot_views_dynamic_by_days(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        if language == 'en':
            title = 'Views number by days'
            xlabel = 'Day'
            ylabel = 'Views count'
        else:
            title = 'Количество просмотров по дням'
            xlabel = 'День'
            ylabel = 'Количество просмотров'
        self.__set_plotting_config(title, xlabel, ylabel)
        total_views = self.__get_total_views()
        total_views.groupby(total_views['date'].dt.date)['views'].sum().plot(figsize=(24, 5))
        by_days_views = self._PLOTS_PATH.format('by_days_views_' + str(self._chat_id))
        plt.savefig(by_days_views)
        plt.close()
        return by_days_views

    def __plot_views_dynamic_by_hours(self, language: str) -> str:
        """
        :param language: user-selected language
        :return: path to the plot
        """
        if language == 'en':
            title = 'Views number by hours'
            xlabel = 'Hour'
            ylabel = 'Views count'
        else:
            title = 'Количество просмотров по часам'
            xlabel = 'Час'
            ylabel = 'Количество просмотров'
        self.__set_plotting_config(title, xlabel, ylabel)
        total_views = self.__get_total_views()
        total_views.groupby(
            total_views['date'].dt.tz_convert('Europe/Moscow').dt.hour
        )['views'].sum().plot(figsize=(24, 5))
        by_hours_views = self._PLOTS_PATH.format('by_hours_views_' + str(self._chat_id))
        plt.savefig(by_hours_views)
        plt.close()
        return by_hours_views

    # text plots
    def __plot_word_cloud(self, corpus: pd.DataFrame):
        """
        :param corpus: processed dataFrame to work with text
        :return: path to the word_cloud
        """
        text = ' '.join(corpus['text'])
        cloud = WordCloud(
            max_font_size=None, background_color='black', width=1200, height=1000
        ).generate(text)
        plt.figure(figsize=(30, 30))
        plt.imshow(cloud)
        plt.axis("off")
        cloud_path = self._PLOTS_PATH.format('cloud_' + str(self._chat_id))
        cloud.to_file(cloud_path)
        plt.close()
        return cloud_path

    def __plot_top_ngrams(self, n: int, corpus: pd.DataFrame, language: str, word: str, top: int = 10) -> str:
        """
        :param corpus: processed dataFrame to work with text
        :return: path to the ngram
        """
        if language == 'en':
            title = f'{top} Most Frequently Occurring {word}'
            xlabel = 'Number of occurrences'
            ylabel = f'{word}'
        else:
            title = f'{top} Самых Часто Встречаемых {word}'
            xlabel = 'Частота появлений'
            ylabel = f'{word}ы'
        words = ' '.join(corpus['text']).split()
        ngram = (pd.Series(nltk.ngrams(words, n)).value_counts())[:top]
        ngram.sort_values().plot.barh(color='blue', figsize=(18, 15))
        self.__set_plotting_config(title, xlabel, ylabel)
        ngram_path = self._PLOTS_PATH.format(f'{n}-gram_' + str(self._chat_id))
        plt.tick_params(axis='y', labelrotation=50)
        plt.savefig(ngram_path)
        plt.close()
        return ngram_path

    # post stats
    def send_post_stats(self, bot: TeleBot, language: str):
        all_posts = self.__plot_post_dynamic_overall(language)
        by_days_posts = self.__plot_post_dynamic_by_days(language)
        by_hours_posts = self.__plot_post_dynamic_by_hours(language)
        if language == 'en':
            bot.send_message(self._chat_id, 'Poss dynamic plots:')
        else:
            bot.send_message(self._chat_id, 'Графики динамики постов:')
        bot.send_photo(self._chat_id, photo=open(all_posts, 'rb'))
        bot.send_photo(self._chat_id, photo=open(by_days_posts, 'rb'))
        bot.send_photo(self._chat_id, photo=open(by_hours_posts, 'rb'))

    # views stats
    def __get_top_1_by_views(self):
        return self._df.sort_values(by='views', ascending=False).head(1)['text'], \
               int(self._df.sort_values(by='views', ascending=False).head(1)['views'])

    def __send_top_1(self, bot: TeleBot, language: str):
        if language == 'en':
            bot.send_message(self._chat_id, 'That is the text of the most popular post on this channel!')
            word = 'views'
        else:
            bot.send_message(self._chat_id, 'Держи текст самого популярного поста на этом канале!')
            word = 'просмотров'
        text, views = self.__get_top_1_by_views()
        bot.send_message(self._chat_id, f'*Top 1. {views} {word}*', parse_mode='markdown')
        bot.send_message(self._chat_id, text)

    def __send_average_views(self, bot: TeleBot, language: str):
        mean = int(self._df['views'].mean())
        if language == 'en':
            bot.send_message(self._chat_id, f'Mean number of views per post = {mean}')
        else:
            bot.send_message(self._chat_id, f'Среднее количество просмотров на одном посте = {mean}')

    def __send_median_views(self, bot: TeleBot, language: str):
        median = int(self._df['views'].median())
        if language == 'en':
            bot.send_message(self._chat_id, f'Median number of views per post = {median}')
        else:
            bot.send_message(self._chat_id, f'Медианное количество просмотров на одном посте = {median}')

    def send_views_stats(self, bot: TeleBot, language: str):
        if language == 'en':
            bot.send_message(self._chat_id, 'Views dynamic plots:')
        else:
            bot.send_message(self._chat_id, 'Графики динамики просмотров:')
        all_views = self.__plot_views_dynamic_overall(language)
        by_days_views = self.__plot_views_dynamic_by_days(language)
        by_hours_views = self.__plot_views_dynamic_by_hours(language)
        bot.send_photo(self._chat_id, photo=open(all_views, 'rb'))
        bot.send_photo(self._chat_id, photo=open(by_days_views, 'rb'))
        bot.send_photo(self._chat_id, photo=open(by_hours_views, 'rb'))
        self.__send_top_1(bot, language)
        self.__send_average_views(bot, language)
        self.__send_median_views(bot, language)

    # text stats
    def send_text_stats(self, bot: TeleBot, language: str):
        corpus = self.__get_corpus()
        cloud = self.__plot_word_cloud(corpus)
        if language == 'en':
            cloud_text = 'Word cloud:'
            freq_text = 'Word frequency plots:'
            word1 = 'Unigram'
            word2 = 'Bigram'
            word3 = 'Trigram'
        else:
            cloud_text = 'Облако слов:'
            freq_text = 'Графики частот слов:'
            word1 = 'Юниграм'
            word2 = 'Биграм'
            word3 = 'Триграм'
        unigrams = self.__plot_top_ngrams(n=1, top=12, corpus=corpus, language=language, word=word1)
        bigrams = self.__plot_top_ngrams(n=2, top=12, corpus=corpus, language=language, word=word2)
        trigrams = self.__plot_top_ngrams(n=3, top=12, corpus=corpus, language=language, word=word3)
        bot.send_message(self._chat_id, cloud_text)
        bot.send_photo(self._chat_id, photo=open(cloud, 'rb'))
        bot.send_message(self._chat_id, freq_text)
        bot.send_photo(self._chat_id, photo=open(unigrams, 'rb'))
        bot.send_photo(self._chat_id, photo=open(bigrams, 'rb'))
        bot.send_photo(self._chat_id, photo=open(trigrams, 'rb'))
