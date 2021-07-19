import json
import pandas as pd

from telethon.sync import TelegramClient


class DataCollector:
    def __init__(self, client, limit: int = None):
        self._client = client
        self._limit = limit

    async def __collect_data(self, channel_username):
        post_id, post_text, post_date, post_views = [], [], [], []
        async for mess in self._client.iter_messages(channel_username, limit=self._limit):
            if mess.text is not None:
                post_id.append(mess.id)
                post_text.append(mess.text)
                post_date.append(mess.date)
                post_views.append(mess.views)

        return pd.DataFrame(
            data={
                'id': post_id,
                'text': post_text,
                'date': post_date,
                'views': post_views
            }
        )

    def load_data(self, channel_username, path: str):
        df = self._client.loop.run_until_complete(self.__collect_data(channel_username))
        df.to_csv(path, index=False)

    @staticmethod
    def from_config(json_path: str, limit: int = None):
        with open(json_path, 'r') as json_file:
            client_credentials = json.load(json_file)

        client = TelegramClient(
            'session_name',
            client_credentials['api_id'],
            client_credentials['api_hash']
        )
        client.start()
        return DataCollector(client, limit=limit)
