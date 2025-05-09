

from typing import Union

import disnake
from db.playlist import PlaylistDB
from service.music.player import Player

class Music_UI:
    @staticmethod
    async def play_music_interaction(player: Player, ctx: Union[disnake.Interaction, any]): # type: ignore
            if player.is_paused:
                player.is_paused = False
                player.is_audio_buffered = True
                if player.voice_client is not None:
                    player.voice_client.resume()
                return
            if not player.is_audio_buffered:
                await player.play_music()

    @staticmethod
    def init_View() -> disnake.ui.View:
            view = disnake.ui.View()
            button = disnake.ui.Button()
            button.label = "Start VC"
            button.custom_id = "jvc"
            # button.callback = self.join_music_interaction
            view.add_item(button)
            return view

    @staticmethod
    def main_View() -> disnake.ui.View:
            view = disnake.ui.View()
            play_button = disnake.ui.Button()
            play_button.label = "Play"
            play_button.custom_id = "play"
            # play_button.callback = self.play_music_interaction

            skip_button = disnake.ui.Button()
            skip_button.label = "Skip"
            # skip_button.callback = self.skip_callback

            add_button = disnake.ui.Button()
            add_button.label = "Add to Playlist"
            add_button.custom_id = "add"
            # add_button.callback = self.add_callback

            leave_button = disnake.ui.Button()
            leave_button.label = "Leave VC"
            leave_button.custom_id = "leave"
            # leave_button.callback = self.leave_music_interaction

            list_button = disnake.ui.Button()
            list_button.label = "Leave VC"
            list_button.custom_id = "leave"

            view.add_item(play_button)
            view.add_item(skip_button)
            view.add_item(add_button)
            view.add_item(leave_button)
            
            return view



    # # Instead of subclassing `disnake.ui.StringSelect`, this example shows how to use the
    # # `@disnake.ui.string_select` decorator directly inside the View to create the dropdown
    # # component.
    # class AnimalView(disnake.ui.View):
    #     def __init__(self):
    #         super().__init__()

    #         # If you wish to pass a previously defined sequence of values to this `View` so that
    #         # you may have dynamic options, you can do so by defining them within this __init__ method.
    #         # `self.animal_callback.options = [...]`

    #     @disnake.ui.string_select(
    #         placeholder="Choose an animal",
    #         options=[
    #             disnake.SelectOption(label="Dog", description="Dogs are your favorite type of animal"),
    #             disnake.SelectOption(label="Cat", description="Cats are your favorite type of animal"),
    #             disnake.SelectOption(
    #                 label="Snake", description="Snakes are your favorite type of animal"
    #             ),
    #             disnake.SelectOption(
    #                 label="Gerbil", description="Gerbils are your favorite type of animal"
    #             ),
    #         ],
    #         min_values=1,
    #         max_values=1,
    #     )
    #     async def animal_callback(
    #         self, select: disnake.ui.StringSelect, inter: disnake.MessageInteraction
    #     ):
    #         # The main difference in this callback is that we access the `StringSelect` through the
    #         # parameter passed to the callback, vs the subclass example where we access it via `self`
    #         await inter.response.send_message(f"You favorite type of animal is: {select.values[0]}")

    @staticmethod
    def playlist_view() -> disnake.ui.View:
        view = disnake.ui.View()
        view.add_item(PlaylistDropdown())
        return view
    
    @staticmethod
    def create_playlist_view() -> disnake.ui.View:
        view = disnake.ui.View()
        view.add_item(PlaylistDropdown())
        return view

class PlaylistDropdown(disnake.ui.StringSelect):
    def __init__(self):

        # Define the options that will be displayed inside the dropdown.
        # You may not have more than 25 options.
        # There is a `value` keyword that is being omitted, which is useful if
        # you wish to display a label to the user, but handle a different value
        # here within the code, like an index number or database id.

        playlists = PlaylistDB.get_all()
        # playlists = [{"playlist_name": "Hello", "id": 1}]
        options = []
        options.append(disnake.SelectOption(
                        label="New PLaylist",
                        value="0", 
                        description=f"Playlist ID: 0" 
                    ))
        if playlists is not None:
            options.extend(
                disnake.SelectOption(
                        label=playlist.playlist_name,
                        value=str(playlist.id), 
                        description=f"Playlist ID: {playlist.id}" 
                    ) for playlist in playlists
            )

        # We will include a placeholder that will be shown until an option has been selected.
        # The min and max values indicate the minimum and maximum number of options to be selected -
        # in this example we will only allow one option to be selected.
        super().__init__(
            placeholder="Choose a Playlist",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    # This callback is called each time a user has selected an option
    async def callback(self, inter: disnake.MessageInteraction):
        # Use the interaction object to respond to the interaction.
        # `self` refers to this StringSelect object, and the `values`
        # attribute contains a list of the user's selected options.
        # We only want the first (and in this case, only) one.
        if(self.values[0] == "0"):
             await inter.response.send_modal(CreatePlaylistModal())
             return

        await inter.response.send_message(f"You choose playlist: {self.values[0]}", delete_after=10)
        await inter.send(f"You choose playlist: {self.values[0]}", delete_after=10)

class CreatePlaylistModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Playlist Name",
                placeholder="Name",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=50,
        )]

        super().__init__(
            title= "Create Playlist",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction):
        PlaylistDB.create(inter.author.id, inter.text_values['name']) 
        await inter.response.send_message(f"Playlist: {inter.text_values['name']} now created", delete_after=10)