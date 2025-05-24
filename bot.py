import discord
from discord.ext import commands
from ollama_client import list_models, start_model, generate_response
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

user_model_choice = {}

class ModelSelectView(discord.ui.View):
    def __init__(self, models: list[str], user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        for model in models:
            self.add_item(ModelButton(label=model, user_id=user_id))

class ModelButton(discord.ui.Button):
    def __init__(self, label: str, user_id: int):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.model = label
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(f"Checking if `{self.model}` is available...", ephemeral=True)
        status = await start_model(self.model)
        if status == True or status == "success":
            user_model_choice[self.user_id] = self.model
            await interaction.followup.send(f"Model set to `{self.model}` for you!", ephemeral=True)
        else:
            await interaction.followup.send(f"Failed to start model `{self.model}`: `{status}`", ephemeral=True)

@bot.command(name="choose")
async def choose_model(ctx):
    models = await list_models()
    if not models:
        await ctx.send("No models found in Ollama!", ephemeral=True)
        return

    view = ModelSelectView(models=models, user_id=ctx.author.id)
    await ctx.send("Select your model:", view=view)

@bot.command(name="ask")
async def ask(ctx, *, prompt: str):
    model = user_model_choice.get(ctx.author.id)
    if not model:
        await ctx.send("No model set for you! Use `!choose` first.")
        return
    await ctx.send(f"Sending to `{model}`...")
    response = await generate_response(model, prompt)
    await ctx.send(f"**{model} says:**
{response}")

bot.run(TOKEN)
