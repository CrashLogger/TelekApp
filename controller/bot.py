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
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    await interaction.response.defer()
    # Si no se dice la foto de quien, se coge la de quien manda el comando
    user = user or interaction.user
    avatar_url = user.display_avatar.url
    embed = discord.Embed(title=f"Fotite de: {user.display_name}", color=discord.Color.pink())
    embed.set_image(url=avatar_url)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="template", description="Pone o texto o una imagen en otra.")
async def template(interaction: discord.Interaction, image_template_name:str, caption: str=None, image:discord.Attachment = None, font:str = "Roboto", colour:str = None ):
    # Edita una imagen con una caption
    # TODO: rect_top_left=[10, 10] y rect_bottom_right=[320, 240] deberían de salir de la base de datos!
    # Hay que hacer un schema que considere imagenes, el rectángulo donde se puede poner el texto y el color que el texto debería ser!
    await interaction.response.defer()
    
    try:
        if caption:
            file, file_path = await template_generic(interaction=interaction, image_template_name=image_template_name, caption=caption, font=font, colour=colour)
        elif image:
            print(image.content_type)
            if not image.content_type.startswith('image/'):
                await interaction.followup.send("Eso no es una imagen, espabila.", ephemeral=True)
                return
            elif image.content_type.startswith('image/gif'):
                image_data = await image.read()
                file, file_path = await template_picture_in_picture(interaction=interaction, image_template_name=image_template_name, image_data=image_data, type='gif')
            else:
                image_data = await image.read()
                file, file_path = await template_picture_in_picture(interaction=interaction, image_template_name=image_template_name, image_data=image_data, type='png')

        if file:
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send("Owie :(")
        template_cleanup(file_path=file_path)
    except Exception as e:
        await interaction.followup.send(f"Big owie owowowow :'((:\n{e}")

# Atajo para /sonic
@bot.tree.command()
async def sonic(interaction: discord.Interaction, caption: str, font:str = "Roboto", colour:str = None ):
    await interaction.response.defer()
    try:
        file, file_path = template_generic(interaction=interaction, image_template_name="sonic", caption=caption, font=font, colour=colour)
        if file:
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send("Owie :(")
        template_cleanup(file_path=file_path)
    except Exception:
        await interaction.followup.send("Big owie owowowow :'((")


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

async def template_generic (interaction: discord.Interaction, image_template_name:str, caption: str, font:str = "Roboto", colour:str = None):
    
    # Edita una imagen con una caption
    # TODO: rect_top_left=[10, 10] y rect_bottom_right=[320, 240] deberían de salir de la base de datos!
    # Hay que hacer un schema que considere imagenes, el rectángulo donde se puede poner el texto y el color que el texto debería ser!
    file = None
    try:
        template_dict = get_template(image_template_name)
        imageworker = TemplateWorker(
            image_template_name=image_template_name,
            rect_top_left=[template_dict["templateTextBoxTLX"], template_dict["templateTextBoxTLY"]],
            rect_bottom_right=[template_dict["templateTextBoxBRX"], template_dict["templateTextBoxBRY"]],
            font_colour=colour if colour else template_dict["defaultTextColour"],
            font_name=font if font else "Roboto"
        )
        #imageworker = TemplateWorker(rect_top_left=[10,10], rect_bottom_right=[320, 240], font_path=font)
        imagehash = imageworker.image_and_text(caption=caption)
        file_path = f'image-templates/tmp/{image_template_name}-{imagehash}.png'
        file = discord.File(file_path, filename=f"{image_template_name}-{imagehash}.png")
    except Exception as e:
        print("Oh cock @ template")
        print(e)
    
    return file, file_path

async def template_picture_in_picture (interaction: discord.Interaction, image_template_name:str, image_data:discord.Attachment, font:str = "Roboto", colour:str = None, type:str = 'png'):
    
    # Edita una imagen poniendo otra imagen donde normalmente iría el texto
    # TODO: rect_top_left=[10, 10] y rect_bottom_right=[320, 240] deberían de salir de la base de datos!
    # Hay que hacer un schema que considere imagenes, el rectángulo donde se puede poner el texto y el color que el texto debería ser!
    file = None
    try:
        template_dict = get_template(image_template_name)
        imageworker = TemplateWorker(
            image_template_name=image_template_name,
            rect_top_left=[template_dict["templateTextBoxTLX"], template_dict["templateTextBoxTLY"]],
            rect_bottom_right=[template_dict["templateTextBoxBRX"], template_dict["templateTextBoxBRY"]],
            font_colour=colour if colour else template_dict["defaultTextColour"],
            font_name=font if font else "Roboto"
        )
        #imageworker = TemplateWorker(rect_top_left=[10,10], rect_bottom_right=[320, 240], font_path=font)
        
        if type=='gif':
            print("bing bong")
            imagehash = imageworker.image_and_animated_gif(image_data=image_data)
        else:
            print("boooooong")
            imagehash = imageworker.image_and_image(image_data=image_data)
        file_path = f'image-templates/tmp/{image_template_name}-{imagehash}.{type}'
        file = discord.File(file_path, filename=f"{image_template_name}-{imagehash}.{type}")
    except Exception as e:
        print("Oh cock @ template")
        print(e)
    
    return file, file_path

def template_cleanup(file_path: str):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")