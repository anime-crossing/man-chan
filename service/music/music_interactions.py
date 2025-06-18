from enum import Enum
from typing import List

import disnake

from db.playlist import PlaylistDB
from db.playlistSong import PlaylistSongDB
from db.radio import RadioDB
from db.song import SongDB
from models import Song
from service.music.master_player import MasterPlayer
from service.music.player import Player


class PlaylistAddType(Enum):
    CURRENT_SONG = 1
    QUEUE = 2
    HISTORY = 3


class Music_Interactions:
    @staticmethod
    async def init_music_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        radio = RadioDB.get(guild_id=str(inter.guild.id))
        if radio is None:
            channel = await inter.guild.create_text_channel(name="manchan radio")
            player_ui = await channel.send(
                embed=Music_UI.init_embed(), view=Music_UI.init_view()
            )
            RadioDB.create(str(inter.guild.id), str(channel.id), str(player_ui.id))
            await inter.followup.send(
                f"Channel has been created: {channel.mention}, Music Player UI: [player]({player_ui.jump_url})",
                delete_after=20,
            )
            return

        music_channel = await inter.guild.fetch_channel(radio.channel_id)
        if not isinstance(music_channel, disnake.TextChannel):
            await inter.followup.send("Run !resetmusic command", delete_after=5)
            return

        player_ui = await music_channel.fetch_message(radio.embed_id)
        await inter.followup.send(
            f"Channel already exist: {music_channel.mention}, Music Player UI already exist: [player]({player_ui.jump_url})",
            delete_after=20,
        )

    @staticmethod
    async def reset_music(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        radio = RadioDB.get(guild_id=str(inter.guild.id))
        if radio is None:
            await inter.followup.send("This command is not needed", delete_after=5)
            return
        music_channel = await inter.guild.fetch_channel(radio.channel_id)
        await music_channel.delete()

        RadioDB.delete(str(inter.guild.id))
        await inter.followup.send(
            "Channel successfully delete and deleted from DB", delete_after=5
        )
        return

    @staticmethod
    async def join_music_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        radio = RadioDB.get(guild_id=str(inter.guild.id))
        if radio is None:
            await inter.followup.send("Run !initmusic command", delete_after=5)
            return
        if int(radio.channel_id) != inter.channel.id:
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return
        if not isinstance(inter.author, disnake.Member) or inter.author.voice is None:
            await inter.followup.send("Connect to a voice channel!", delete_after=5)
            return
        player = MasterPlayer().create_player(inter.guild.id)
        player.set_channel_id(int(radio.channel_id))
        music_channel = await inter.guild.fetch_channel(player.get_channel_id())
        if isinstance(music_channel, disnake.TextChannel):
            player_ui = await music_channel.fetch_message(radio.embed_id)
            player.channel_id = int(radio.channel_id)
            player.player_ui = player_ui
            await player.player_ui.edit(
                embed=Music_UI.main_embed(player), view=Music_UI.main_View()
            )
        if not player.is_connected and inter.author.voice.channel is not None:
            player.voice_client = await inter.author.voice.channel.connect()
            player.is_connected = True
            await inter.followup.send("Connected", delete_after=5)

    @staticmethod
    async def leave_music_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        voice_client = inter.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect(force=False)

        player = MasterPlayer().get_player(inter.guild.id)
        if player is not None:
            music_channel = await inter.guild.fetch_channel(player.get_channel_id())
            MasterPlayer().destroy_player(inter.guild.id)
            if (
                isinstance(music_channel, disnake.TextChannel)
                and player.player_ui is not None
            ):
                await player.player_ui.edit(
                    embed=Music_UI.init_embed(), view=Music_UI.init_view()
                )
        await inter.followup.send(
            "Bot left VC and player instance destroyed", delete_after=5
        )

    @staticmethod
    async def play_interaction(inter: disnake.Interaction, song: str):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            await inter.followup.send("Run !jvc to start", delete_after=5)
            return
        if player.get_channel_id() != inter.channel.id:
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return

        if song != "":
            player.add_song(song)
            player_ui = player.get_player_ui()
            if player_ui is not None:
                await player_ui.edit(embed=Music_UI.main_embed(player))

        if player.is_paused:
            player.is_paused = False
            player.is_audio_buffered = True
            if player.voice_client is not None:
                player.voice_client.resume()
            if player.player_ui is not None:
                await player.player_ui.edit(embed=Music_UI.main_embed(player))
            return await inter.followup.send("Audio is now Resumed", delete_after=5)

        if not player.is_audio_buffered:
            await player.play_music()
            return await inter.followup.send("Started Playing music", delete_after=5)

    @staticmethod
    async def add_interaction(inter: disnake.Interaction, song: str):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        radio = RadioDB.get(guild_id=str(inter.guild.id))
        if radio is None:
            await inter.followup.send("Run !initmusic command", delete_after=5)
            return

        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            player = MasterPlayer().create_player(inter.guild.id)

        music_channel = await inter.guild.fetch_channel(radio.channel_id)
        if not isinstance(music_channel, disnake.TextChannel):
            await inter.followup.send("Run resetMusic command", delete_after=5)
            return

        player_ui = await music_channel.fetch_message(radio.embed_id)
        player.add_song(song)
        await player_ui.edit(embed=Music_UI.main_embed(player))
        await inter.followup.send("Added Song", delete_after=5)

    @staticmethod
    async def history_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == inter.channel.id):
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return
        return await inter.followup.send(
            embed=Music_UI.history_embed(player), delete_after=20
        )

    @staticmethod
    async def clear_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == inter.channel.id):
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return
        if player.is_connected:
            player.clear_queue()
        music_channel = await inter.guild.fetch_channel(player.get_channel_id())
        if not isinstance(music_channel, disnake.TextChannel):
            await inter.followup.send("Run resetMusic command", delete_after=5)
            return
        player_ui = await music_channel.fetch_message(player.get_player_ui().id)  # type: ignore
        await player_ui.edit(embed=Music_UI.main_embed(player))

    @staticmethod
    async def skip_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == inter.channel.id):
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return
        if player.is_connected:
            player.stop_player()

    @staticmethod
    async def pause_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == inter.channel.id):
            await inter.followup.send("Not in Music Channel", delete_after=5)
            return
        if player.is_audio_buffered:
            player.is_paused = True
            player.is_audio_buffered = False
            player.voice_client.pause()  # type: ignore
            await inter.followup.send("Audio is now Paused", delete_after=5)
            if player.player_ui is not None:
                await player.player_ui.edit(embed=Music_UI.main_embed(player))

    @staticmethod
    async def create_playlist_interaction(
        inter: disnake.Interaction, playlist_name: str
    ):
        await inter.response.defer()
        PlaylistDB.create(str(inter.author.id), playlist_name)
        await inter.followup.send(
            f"Playlist: {playlist_name} now created", delete_after=5
        )
        return

    @staticmethod
    async def list_playlist_interaction(inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        playlists = PlaylistDB.get_all()
        embed = disnake.Embed()
        embed.title = "Playlists:"
        playlist_str = ""
        for playlist in playlists:
            playlist_str += str(playlist.id) + ". " + playlist.playlist_name + "\n"
        embed.add_field("", playlist_str)
        await inter.followup.send(embed=embed, delete_after=10)

    @staticmethod
    async def delete_playlist_interaction(inter: disnake.Interaction, playlist_id: int):
        await inter.response.defer()
        playlist = PlaylistDB.get(playlist_id, str(inter.author.id))
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return
        PlaylistDB.delete(playlist_id)
        await inter.followup.send(f"Playlist: {playlist_id} deleted", delete_after=10)

    @staticmethod
    async def add_playlist_interaction(
        inter: disnake.Interaction, playlist_id: int, addType: PlaylistAddType
    ):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        match addType:
            case PlaylistAddType.CURRENT_SONG:
                await Music_Interactions.add_song_playlist_interaction(
                    inter, playlist_id
                )
            case PlaylistAddType.QUEUE:
                await Music_Interactions.add_queue_playlist(inter, playlist_id)
            case PlaylistAddType.HISTORY:
                await Music_Interactions.add_history_queue_playlist(inter, playlist_id)

    @staticmethod
    async def list_playlist_songs_interaction(
        inter: disnake.Interaction, playlist_id: int
    ):
        await inter.response.defer()

        playlist = PlaylistSongDB.get_songs_by_playlist(playlist_id)
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return
        embed = disnake.Embed()
        playlist_name = PlaylistDB.get_by_id(playlist_id)
        if playlist_name is None:
            return
        embed.title = playlist_name.playlist_name
        playlist_str = ""
        index = 1
        for entry in playlist:
            song = SongDB.get_by_id(int(entry.id))
            if song is not None:
                playlist_str += f"{index}. {song.title} ({song.id})\n"
            index += 1
        embed.add_field("", playlist_str)
        await inter.followup.send(embed=embed, delete_after=10)

    @staticmethod
    async def remove_playlist_song(
        inter: disnake.Interaction, playlist_id: int, song_id: int
    ):
        await inter.response.defer()
        playlist = PlaylistSongDB.get_songs_by_playlist(playlist_id)
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return
        song = SongDB.get_by_id(song_id)
        if song is None:
            await inter.followup.send(f"Song does not exist", delete_after=10)
            return
        PlaylistSongDB.delete_playlist_song(playlist_id, song_id)
        await inter.followup.send(
            f"Song {song.title} removed from Playlist: {playlist_id} deleted",
            delete_after=10,
        )

    @staticmethod
    async def load_playlist_interaction(inter: disnake.Interaction, playlist_id: int):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        playlist = PlaylistSongDB.get_songs_by_playlist(playlist_id)
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        for entry in playlist:
            songdb = SongDB.get_by_id(int(entry.id))
            if songdb is not None:
                player.add_song(songdb.webpage_url)
        if player.player_ui is None:
            return
        await player.player_ui.edit(embed=Music_UI.main_embed(player))

    @staticmethod
    async def loop_interaction(inter: disnake.Interaction):
        await inter.response.defer()
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return
        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        player.loop = not player.loop
        player_ui = player.get_player_ui()
        if player_ui is not None:
            await player_ui.edit(embed=Music_UI.main_embed(player))

    @staticmethod
    async def add_song_playlist_interaction(
        inter: disnake.Interaction, playlist_id: int
    ):
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        playlist = PlaylistDB.get_by_id(playlist_id)
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return

        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if player.current_song is None:
            await inter.followup.send("No song is currently playing.", delete_after=10)
            return
        song: Song = player.current_song

        addedSong = SongDB.get_by_url(song.url)
        if addedSong is None:
            addedSong = SongDB.create(song)
        PlaylistSongDB.create(int(playlist.id), int(addedSong.id))
        await inter.followup.send(
            f"Song: {song.title} added to Playlist: {playlist_id}", delete_after=10
        )

    @staticmethod
    async def add_queue_playlist(inter: disnake.Interaction, playlist_id: int):
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        playlist = PlaylistDB.get_by_id(playlist_id)
        print(playlist.__str__())
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return

        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if player.queue is None:
            await inter.followup.send(
                "No songs is currently in queue.", delete_after=10
            )
            return

        for song in player.queue:
            addedSong = SongDB.get_by_url(song.url)
            if addedSong is None:
                addedSong = SongDB.create(song)
            PlaylistSongDB.create(int(playlist.id), int(addedSong.id))
        await inter.followup.send(
            f"Queue added to Playlist: {playlist_id}", delete_after=10
        )

    @staticmethod
    async def add_history_queue_playlist(inter: disnake.Interaction, playlist_id: int):
        if inter.guild is None:
            await inter.followup.send(
                "This command can only be used in a server.", delete_after=5
            )
            return

        playlist = PlaylistDB.get_by_id(playlist_id)
        if playlist is None:
            await inter.followup.send(
                f"Playlist: {playlist_id} does not exist", delete_after=10
            )
            return

        player = MasterPlayer().get_player(inter.guild.id)
        if player is None:
            return
        if player.history is None:
            await inter.followup.send(
                "No songs is currently in history.", delete_after=10
            )
            return

        for song in player.history:
            addedSong = SongDB.get_by_url(song.url)
            if addedSong is None:
                addedSong = SongDB.create(song)
            PlaylistSongDB.create(int(playlist.id), int(addedSong.id))
        await inter.followup.send(
            f"Current history Queue added to Playlist: {playlist_id}", delete_after=10
        )


class Music_UI:
    @staticmethod
    def init_view() -> disnake.ui.View:
        view = disnake.ui.View()
        button = disnake.ui.Button()
        button.label = "Start VC"
        button.custom_id = "jvc"
        view.add_item(button)
        return view

    @staticmethod
    def init_embed() -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "MANCHAN RADIO"
        embed.description = "Please run !jvc to start radio"
        embed.add_field("Paused:", "False")
        embed.add_field("Loop:", "False")
        embed.add_field("Now Playing:", "Empty", inline=False)
        embed.add_field("Queue:", "Empty", inline=False)
        return embed

    @staticmethod
    def main_View() -> disnake.ui.View:
        view = disnake.ui.View()
        view.timeout = None
        view.add_item(ButtonPlay())
        view.add_item(ButtonPause())
        view.add_item(ButtonSkip())
        view.add_item(ButtonLoop())
        view.add_item(ButtonHistory())
        view.add_item(ButtonAddToPlaylist())
        view.add_item(ButtonViewPlaylist())
        view.add_item(ButtonLoadPlaylist())
        view.add_item(ButtonClear())
        view.add_item(ButtonLeaveVc())
        return view

    @staticmethod
    def main_embed(player: Player) -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "MANCHAN RADIO"
        embed.description = "Please run !lvc to stop radio"
        embed.add_field("Paused:", str(player.is_paused))
        embed.add_field("Loop:", str(player.loop))
        embed.add_field(
            "Now Playing:",
            player.current_song.title if player.current_song else "Empty",
            inline=False,
        )
        embed.add_field("Queue:", player.queue_to_string(), inline=False)
        if player.current_song:
            embed.set_image(player.current_song.thumbnail_url)
        return embed

    @staticmethod
    def history_embed(player: Player) -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "History:"
        history_str = player.history_to_string()
        if player.is_history_empty():
            history_str = "No Songs"
        embed.add_field("", history_str)
        return embed


class DropDownAddPlaylist(disnake.ui.StringSelect):
    def __init__(self):
        playlists = PlaylistDB.get_all()
        options = []
        if playlists is not None:
            options.extend(
                disnake.SelectOption(
                    label=playlist.playlist_name,
                    value=str(playlist.id),
                    description=f"Playlist ID: {playlist.id}",
                )
                for playlist in playlists
            )
        super().__init__(
            placeholder="Choose a Playlist",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        value = int(self.values[0])
        view = disnake.ui.View()
        view.add_item(DropDownPlaylistOptions(value))
        await inter.response.send_message(view=view, delete_after=10)


class DropDownViewPlaylist(disnake.ui.StringSelect):
    def __init__(self, playlists: List[PlaylistDB]):
        options = []
        if playlists is not None:
            options.extend(
                disnake.SelectOption(
                    label=playlist.playlist_name,
                    value=str(playlist.id),
                    description=f"Playlist ID: {playlist.id}",
                )
                for playlist in playlists
            )

        super().__init__(
            placeholder="Choose a Playlist",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await Music_Interactions.list_playlist_songs_interaction(
            inter, int(self.values[0])
        )


class DropDownLoadPlaylist(disnake.ui.StringSelect):
    def __init__(self, playlists: List[PlaylistDB]):
        options = []
        if playlists is not None:
            options.extend(
                disnake.SelectOption(
                    label=playlist.playlist_name,
                    value=str(playlist.id),
                    description=f"Playlist ID: {playlist.id}",
                )
                for playlist in playlists
            )

        super().__init__(
            placeholder="Choose a Playlist",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await Music_Interactions.load_playlist_interaction(inter, int(self.values[0]))


class DropDownPlaylistOptions(disnake.ui.StringSelect):
    def __init__(self, playlist_id: int):
        self.playlist_id = playlist_id
        options = [
            disnake.SelectOption(
                label="Current Song",
                value="1",
                description=f"Adds current playing Song to playlist",
            ),
            disnake.SelectOption(
                label="Queue", value="2", description=f"Adds whole queue to playlist"
            ),
            disnake.SelectOption(
                label="History",
                value="3",
                description=f"Adds history session to playlist",
            ),
        ]
        super().__init__(
            placeholder="Add Type", min_values=1, max_values=1, options=options, row=1
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await Music_Interactions.add_playlist_interaction(
            inter, self.playlist_id, PlaylistAddType(int(self.values[0]))
        )


class ButtonAddToPlaylist(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="Add to Playlist", custom_id="addPlaylist", row=1)

    async def callback(self, inter: disnake.Interaction):
        view = disnake.ui.View()
        view.add_item(DropDownAddPlaylist())
        await inter.response.send_message(view=view, delete_after=10)


class ButtonPlay(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label="Play", custom_id="play", style=disnake.ButtonStyle.primary, row=0
        )

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.play_interaction(inter, "")


class ButtonPause(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label="Pause", custom_id="pause", style=disnake.ButtonStyle.blurple, row=0
        )

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.pause_interaction(inter)


class ButtonSkip(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="Skip", custom_id="skip", row=0)

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.skip_interaction(inter)


class ButtonViewPlaylist(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="View Playlist", custom_id="viewPlaylist", row=1)

    async def callback(self, inter: disnake.Interaction):
        playlists = PlaylistDB.get_all()
        view = disnake.ui.View()
        view.add_item(DropDownViewPlaylist(playlists))
        await inter.response.send_message(view=view, delete_after=10)


class ButtonLeaveVc(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label="Leave VC", custom_id="leave", style=disnake.ButtonStyle.danger, row=2
        )

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.leave_music_interaction(inter)


class ButtonLoadPlaylist(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="Load Playlist", custom_id="loadPlaylist", row=1)

    async def callback(self, inter: disnake.Interaction):
        playlists = PlaylistDB.get_all()
        view = disnake.ui.View()
        view.add_item(DropDownLoadPlaylist(playlists))
        await inter.response.send_message(view=view, delete_after=10)


class ButtonClear(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label="Clear", custom_id="clear", style=disnake.ButtonStyle.danger, row=2
        )

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.clear_interaction(inter)


class ButtonHistory(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="History", custom_id="history", row=0)

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.history_interaction(inter)


class ButtonLoop(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="Loop", custom_id="loop", row=0)

    async def callback(self, inter: disnake.Interaction):
        await Music_Interactions.loop_interaction(inter)
