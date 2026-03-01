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

@bot.tree.command(name="avatar", description="Da la fotite de perfil de un usuario, o la tuya si no dices ningún usuario")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    await interaction.response.defer()
    # Si no se dice la foto de quien, se coge la de quien manda el comando
    user = user or interaction.user
    avatar_url = user.display_avatar.url
    embed = discord.Embed(title=f"Fotite de: {user.display_name}", color=discord.Color.pink())
    embed.set_image(url=avatar_url)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="template", description="Pone o texto o una imagen en otra.")
async def template(interaction: discord.Interaction, image_template_name:str, caption: str=None, image:discord.Attachment = None, font:str = "roboto", colour:str = None ):
    # Edita una imagen con una caption
    await interaction.response.defer()
    
    try:
        if caption:
            file, file_path = await template_generic(interaction=interaction, template_command_name=image_template_name, caption=caption, font=font.lower(), colour=colour)
        elif image:
            if not image.content_type.startswith('image/'):
                await interaction.followup.send("Eso no es una imagen, espabila.", ephemeral=True, type='png')
                return
            elif image.content_type.startswith('image/gif'):
                image_data = await image.read()
                file, file_path = await template_generic(interaction=interaction, template_command_name=image_template_name, image_data=image_data, type='gif')
            else:
                image_data = await image.read()
                file, file_path = await template_generic(interaction=interaction, template_command_name=image_template_name, image_data=image_data, type='png')

        if file:
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send("Owie :(")
        template_cleanup(file_path=file_path)
    except Exception as e:
        await interaction.followup.send(f"Big owie owowowow :'((:\n{e}")

# Atajo para /sonic
@bot.tree.command(name="sonic", description="Es un atajo para la plantilla de sonic, solo para texto, como en otros bots")
async def sonic(interaction: discord.Interaction, caption: str, font:str = "Roboto", colour:str = None ):
    await interaction.response.defer()
    try:
        file, file_path = await template_generic(interaction=interaction, template_command_name="sonic", caption=caption, font=font.lower(), colour=colour)
        if file:
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send("Owie :(")
        template_cleanup(file_path=file_path)
    except Exception as e:
        await interaction.followup.send(f"Big owie owowowow :'((: \n{e}")

@bot.tree.command(name="links", description="La nueva forma epica de poner links, en lugar del trigger url")
async def links(interaction: discord.Interaction):
    await interaction.response.send_message(f"# URLs:\nChange my settings at:\n{misc.URL}\nBugs? Improvements?:\n{misc.ISSUES}")

@bot.tree.command(name="triggers", description="La nueva forma epica de ver los triggers, en lugar del trigger debug triggers")
async def triggers(interaction: discord.Interaction):
    combos = get_combos()
    triggers = [combo["trigger"] for combo in combos]
    triggerList:str = ""
    for trigger in triggers:
        triggerList=triggerList + f"- {trigger}\n"
    await interaction.response.send_message(f"TelekApp version:{misc.VERSION}\nMy triggers are:\n```{triggerList}```")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip().lower()

    # Debug: list all triggers
    # DEPRECATED
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

async def template_generic (interaction: discord.Interaction, template_command_name:str, caption: str = None, font:str = "roboto", colour:str = None, image_data:discord.Attachment = None, type:str = 'png'):
    file = None
    try:
        template_dict = get_template(template_command_name)
        imageworker = TemplateWorker(
            image_command_name=template_command_name,
            image_template_name=template_dict["templateImageFile"],
            rect_top_left=[template_dict["templateTextBoxTLX"], template_dict["templateTextBoxTLY"]],
            rect_bottom_right=[template_dict["templateTextBoxBRX"], template_dict["templateTextBoxBRY"]],
            font_colour=colour if colour else template_dict["defaultTextColour"],
            font_name=font.lower() if font else "roboto"
        )
        if caption:
            imagehash = imageworker.image_and_text(caption=caption)
        else:
            if type=='gif':
                imagehash = imageworker.image_and_animated_gif(image_data=image_data)
            else:
                imagehash = imageworker.image_and_image(image_data=image_data)
        file_path = f'image-templates/tmp/{template_command_name}-{imagehash}.{type}'
        file = discord.File(file_path, filename=f"{template_command_name}-{imagehash}.{type}")
    except Exception as e:
        print("Oh cock @ template")
        print(e)
    
    return file, file_path

def template_cleanup(file_path: str):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")