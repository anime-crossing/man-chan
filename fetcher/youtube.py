from typing import Any
from youtube_dl import YoutubeDL


class YoutubeApi:
     YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

     @classmethod
     def search(cls, query: str, limit = 1) -> Any:
        results = YoutubeDL(cls.YDL_OPTIONS).extract_info("ytsearch%d:%s" % (limit,query), download= False)
        return results['entries']

