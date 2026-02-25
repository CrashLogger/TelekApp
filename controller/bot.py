import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from model.bot_db import get_random_response, get_combos, get_template
from model import misc
from controller.images import TemplateWorker

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
    print(f"Eyyyyy ey ey aaaaaqui {bot.user} v{misc.VERSION} eeeeeeen Discord")

@bot.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@bot.tree.command()
async def template(interaction: discord.Interaction, image_template_name:str, caption: str, font:str = "Roboto", colour:str = None ):
    # Edita una imagen con una caption
    # TODO: rect_top_left=[10, 10] y rect_bottom_right=[320, 240] deberían de salir de la base de datos!
    # Hay que hacer un schema que considere imagenes, el rectángulo donde se puede poner el texto y el color que el texto debería ser!
    file = None
    try:
        template_dict = get_template(image_template_name)
        print(f"Picked up template: {template_dict["templateCommand"]}")
        imageworker = TemplateWorker(
            image_template_name=image_template_name,
            rect_top_left=[template_dict["templateTextBoxTLX"], template_dict["templateTextBoxTLY"]],
            rect_bottom_right=[template_dict["templateTextBoxBRX"], template_dict["templateTextBoxBRY"]],
            font_colour=colour if colour else template_dict["defaultTextColour"],
            font_name=font if font else "Roboto"
        )
        #imageworker = TemplateWorker(rect_top_left=[10,10], rect_bottom_right=[320, 240], font_path=font)
        imagehash = imageworker.imageWork(caption=caption)
        file_path = f'image-templates/tmp/{image_template_name}-{imagehash}.png'
        file = discord.File(file_path, filename=f"{image_template_name}-{imagehash}.png")
    except Exception as e:
        print("Oh cock")
        print(e)

    
    await interaction.response.send_message(file=file)
    
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

@bot.tree.command()
async def links(interaction: discord.Interaction):
    combos = get_combos()
    triggers = [combo["trigger"] for combo in combos]
    await interaction.response.send_message(f"# URLs:\nChange my settings at:\n{misc.URL}\nBugs? Improvements?:\n{misc.ISSUES}")

@bot.tree.command()
async def triggers(interaction: discord.Interaction):
    combos = get_combos()
    triggers = [combo["trigger"] for combo in combos]
    await interaction.response.send_message(f"TelekApp version:{misc.VERSION}\nMy triggers are:\n```{triggers}```")

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