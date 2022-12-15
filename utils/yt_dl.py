# # # #
# https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
# https://medium.com/pythonland/build-a-discord-bot-in-python-that-plays-music-and-send-gifs-856385e605a1
# # # #

import youtube_dl
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from asyncio import get_event_loop, AbstractEventLoop

from typing import Optional, cast

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDHandler(PCMVolumeTransformer):

    def __init__(self, ctx, source: FFmpegPCMAudio, data: dict, volume: float=0.5):
        super().__init__(source, volume)

        self._data = data
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        # self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    @classmethod
    async def from_url(cls, ctx, url: str, loop: Optional[AbstractEventLoop] = None, stream=False) -> 'YTDHandler':
        loop = loop or get_event_loop()

        
        data: dict = cast(dict, await loop.run_in_executor(
            None, 
            lambda: ytdl.extract_info(url, download=False)))

        if data is None:
            return ''

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry

        if process_info == None:
            return ''

        webpage_url = process_info["webpage_url"]
        url = process_info["url"]

        print("RESULTS:", webpage_url, url)

        
        # if 'entries' in data:
        #     # take first item from a playlist
        #     data = data['entries'][0]
        # filename = data['title'] if stream else ytdl.prepare_filename(data)
        # return filename
        return cls(ctx, FFmpegPCMAudio(url, **FFMPEG_OPTIONS), data=process_info)