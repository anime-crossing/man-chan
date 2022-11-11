import youtube_dl
from discord import PCMVolumeTransformer, AudioSource
from asyncio import get_event_loop, BaseEventLoop, AbstractEventLoop

from typing import Optional

youtube_dl.utils.bug_reports_message = lambda: ''

class YTDHandler(PCMVolumeTransformer):

    def __init__(self, original: AudioSource, data, volume: float=0.5):
        super().__init__(original, volume)

        self._data = data
        self._url = ''

    @classmethod
    async def from_url(cls, url: str, *, loop: Optional[AbstractEventLoop] = None, stream=False) -> str:
        loop = loop or get_event_loop()

        
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename