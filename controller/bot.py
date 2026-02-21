# Dependencias
import os, discord
from dotenv import load_dotenv
from discord.ext import commands

from model import iohelpers, defaults

from controller import api

# Creo que es obvio que solo sacamos el fakin token del .env pero vaya
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Intents, los usos que puede hacer un bot
# Los que ponemos en true aquí son los que usa. Los demás se desactivan. Security is my motto.
intents = discord.Intents.default()
intents.message_content = True

# Loggeamos el bot con el token del .env
bot =  discord.Client(intents=intents)

# Cargamos las autoresponses posibles de este archivo
autoresponse_path = defaults.AUTORESPONSE_PATH
working_dir = os.getcwd()

io_helper = iohelpers.ioHelpers(autoresponse_path)
io_helper.load_responses()

###################################################
# Eventos a los que el bot responde               #
###################################################
# Cosas que hace al arranque
@bot.event
async def on_ready():
    bot.loop.create_task(io_helper.start_periodic_reload(interval=30))

# Cosas que hace al buscar mensajes
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "debug replies":
        print("Woah mr hacker over here")
        print(io_helper.file_name_list)
        print(io_helper.file_types_list)
        await message.channel.send(f"My replies are:```{io_helper.file_name_list}```And their formats are:\n```{io_helper.file_types_list}```")

    elif message.content in io_helper.file_name_list:
        file_path = os.path.join(working_dir, autoresponse_path, io_helper.file_list[io_helper.file_name_list.index(message.content)])
        if io_helper.file_types_list[io_helper.file_name_list.index(message.content)] in io_helper.TEXT_FORMATS:
            message_to_send = io_helper.read_text_file(file_path)
            await message.channel.send(message_to_send)
        else:
            if os.path.exists(file_path):
                file_to_send = discord.File(file_path, filename=file_path)
                await message.channel.send(file=file_to_send)

# Por algún motivo que aun no entiendo esto tiene que ir al final
def run_bot():
    bot.run(DISCORD_TOKEN)