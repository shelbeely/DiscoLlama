import discord
from ollama_client import list_models, start_model, generate_response
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Make sure this is enabled!
print(f"discord.py version: {discord.__version__}")
print(f"discord.Bot exists: {'Bot' in dir(discord)}")
bot = discord.Bot(intents=intents)

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
        if status == True or status == "success":
            user_model_choice[self.user_id] = self.model
            await interaction.followup.send(f"Model set to `{self.model}` for you!", ephemeral=True)
        else:
            await interaction.followup.send(f"Failed to start model `{self.model}`: `{status}`", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) - Slash commands synced!")

@bot.tree.command(name="choose", description="Choose your Ollama model")
async def choose_model(interaction: discord.Interaction):
    models = await list_models()
    if not models:
        await interaction.response.send_message("No models found in Ollama!", ephemeral=True)
        return
    view = ModelSelectView(models=models, user_id=interaction.user.id)
    await interaction.response.send_message("Select your model:", view=view, ephemeral=True)

@bot.tree.command(name="ask", description="Ask your selected Ollama model something")
async def ask(interaction: discord.Interaction, prompt: str):
    model = user_model_choice.get(interaction.user.id)
    if not model:
        await interaction.response.send_message("No model set for you! Use `/choose` first.", ephemeral=True)
        return
    await interaction.response.defer()
    response = await generate_response(model, prompt)
    await interaction.followup.send(f"**{model} says:**\n{response}")

bot.run(TOKEN)