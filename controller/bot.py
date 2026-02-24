import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from model.bot_db import get_random_response, get_combos
from controller import images

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))

class TelekApp(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
intents.message_content = True
bot = TelekApp(intents=intents)

@bot.event
async def on_ready():
    print(f"Que pasa crack, {bot.user}")

@bot.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@bot.tree.command()
async def template(interaction: discord.Interaction, message: str):
    # Edita una imagen con una caption
    images.imageWork()
    await interaction.response.send_message(f'Hola tonto ({interaction.user.mention}), me has dicho: {message}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip().lower()

    # Debug: list all triggers
    if content == "debug triggers":
        combos = get_combos()
        triggers = [combo["trigger"] for combo in combos]
        await message.channel.send(f"My triggers are:\n```{triggers}```")
        return

    # Bot response
    response = get_random_response(content)
    if response:
        await message.channel.send(response)


def run_bot():
    bot.run(DISCORD_TOKEN)