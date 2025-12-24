import disnake
from service.jellyfin import JellySeerApi, MovieResult, TvResult, Result
from disnake import ButtonStyle, Embed
from disnake.ui import View, StringSelect


class Dropdown(StringSelect):
    def __init__(self, jellyseerApi: JellySeerApi, results: list[Result]):
        self.results = results
        self.jellyseerApi = jellyseerApi
        options = []
        for res in results:
            if(isinstance(res, MovieResult)):
                options.append(disnake.SelectOption(label=f"{res.mediaType} - {res.title} - {res.releaseDate}", value=str(res.id)))
            if(isinstance(res,TvResult)):
                options.append(disnake.SelectOption(label=f"{res.mediaType} - {res.name} - {res.firstAirDate}", value=str(res.id)))
        super().__init__(
            placeholder="Choose a Movie/Show",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, inter: disnake.MessageInteraction):
        id = int(self.values[0])
        res = [res for res in self.results if res.id == id][0]
        embed = Embed()
        if(isinstance(res, MovieResult)):
            embed.title = res.title
            embed.description = res.overview
            embed.add_field("Release Date", res.releaseDate)
            embed.add_field("Media Type", res.mediaType)
            embed.set_image(res.posterPath)
        if(isinstance(res,TvResult)):
            embed.title = res.name
            embed.description = res.overview
            embed.add_field("First Air Date", res.firstAirDate)
            embed.add_field("Media Type", res.mediaType)
            embed.set_image(res.posterPath)
        await inter.response.send_message(embed=embed, view=RowButtons(self.jellyseerApi, self.results, res))



class RowButtons(disnake.ui.View):
    def __init__(self, jellyseerApi: JellySeerApi, results: list[Result], chosen: Result):
        self.jellyseerApi = jellyseerApi
        self.results = results
        self.chosen = chosen
        super().__init__(timeout=None)

    @disnake.ui.button(label="back", style=ButtonStyle.blurple)
    async def back(self, button: disnake.ui.Button, inter: disnake.MessageInteraction): # pyright: ignore[reportUnknownParameterType]
        embed = ResultsEmbed(self.results)
        view = View()
        view.add_item(Dropdown(self.jellyseerApi, self.results))
        await inter.response.send_message(embed=embed, view=view)

    @disnake.ui.button(label="Request", style=ButtonStyle.green)
    async def request(self, button: disnake.ui.Button, inter: disnake.MessageInteraction): # pyright: ignore[reportUnknownParameterType]
        await inter.response.send_message("Requesting")
        status = self.jellyseerApi.createRequest(self.chosen)
        if (status == 201):
            title = self.chosen.title if isinstance(self.chosen, MovieResult) else self.chosen.name if isinstance(self.chosen, TvResult) else ""
            await inter.edit_original_message(f"Requested {title}")
        else:
            await inter.edit_original_message(f"Error, title could be already in jellyfin")

def ResultsEmbed(results: list[Result]):
    embed = Embed()
    result_str = "Results:\n"
    for res in results:
        if(isinstance(res, MovieResult)):
            result_str += f"{res.mediaType} - {res.title} - {res.releaseDate}\n"
        if(isinstance(res,TvResult)):
            result_str += f"{res.mediaType} - {res.name} - {res.firstAirDate}\n"
    embed.title = "Results:"
    embed.add_field("Media", result_str)
    return embed
