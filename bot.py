import discord
from discord.ext import commands
from ollama_client import list_models, start_model, generate_response
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Optional unless you want legacy messages

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
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This button isn't for you!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"Checking if `{self.model}` is available...", ephemeral=True)

        status = await start_model(self.model)
        if status is True or status == "success":
            user_model_choice[self.user_id] = self.model
            await interaction.followup.send(f"Model set to `{self.model}` for you!", ephemeral=True)
        else:
            await interaction.followup.send(f"Failed to start model `{self.model}`: `{status}`", ephemeral=True)

@bot.event
async def on_ready():
    synced = await bot.sync_commands()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Synced {len(synced)} slash command(s)")

@bot.slash_command(name="choose", description="Choose your Ollama model")
async def choose_model(ctx: discord.ApplicationContext):
    models = await list_models()
    if not models:
        await ctx.respond("No models found in Ollama!", ephemeral=True)
        return

    view = ModelSelectView(models=models, user_id=ctx.author.id)
    await ctx.respond("Select your model:", view=view, ephemeral=True)

@bot.slash_command(name="ask", description="Ask your selected Ollama model something")
async def ask(ctx: discord.ApplicationContext, prompt: discord.Option(str, "Your question")):
    model = user_model_choice.get(ctx.author.id)
    if not model:
        await ctx.respond("No model set for you! Use `/choose` first.", ephemeral=True)
        return

    await ctx.defer()
    response = await generate_response(model, prompt)
    await ctx.respond(f"**{model} says:**\n{response}")

bot.run(TOKEN)