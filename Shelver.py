import shelve

from channel_parser.ChannelAnalyzer import Analyzer


class Shelver:
    def __init__(self, path):
        self._path = path
        self._PATH_TEMPLATE = 'channel_parser/channels_data/df_{}.csv'

    def set_language(self, chat_id, language: str):
        with shelve.open(self._path) as database:
            analyzer = Analyzer()
            is_set = False
            if str(chat_id) in database:
                analyzer = database[str(chat_id)]['analyzer']
                is_set = database[str(chat_id)]['is_set']
            database[str(chat_id)] = {
                'language': language,
                'analyzer': analyzer,
                'is_set': is_set,
                'path': self._PATH_TEMPLATE.format(chat_id)  # path to csv,
                # that contains the data of the latest requested channel by this user
            }

    def set_analyzer(self, chat_id):
        analyzer = Analyzer()
        analyzer.read_data(self.get_path(chat_id), chat_id)
        language = None
        with shelve.open(self._path) as database:
            if str(chat_id) in database:
                language = database[str(chat_id)]['language']
            database[str(chat_id)] = {
                'language': language,
                'analyzer': analyzer,
                'is_set': True,
                'path': 'channels_data/df_' + str(chat_id) + '.csv'  # path to csv,
                # that contains the data of the latest requested channel
            }

    def get_language(self, chat_id):
        language = None
        with shelve.open(self._path) as database:
            if str(chat_id) in database:
                language = database[str(chat_id)]['language']
        return language

    def get_path(self, chat_id):
        return self._PATH_TEMPLATE.format(chat_id)

    def is_analyzer_set(self, chat_id):
        is_set = False
        with shelve.open(self._path) as database:
            if str(chat_id) in database:
                is_set = database[str(chat_id)]['is_set']
        return is_set

    def get_analyzer(self, chat_id):
        analyzer = Analyzer()
        with shelve.open(self._path) as database:
            if str(chat_id) in database:
                analyzer = database[str(chat_id)]['analyzer']
        return analyzer
