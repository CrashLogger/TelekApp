import os
import asyncio

class ioHelpers:

    def __init__(self, autoresponse_path):
        self.autoresponse_path = autoresponse_path
        self.file_list = []
        self.file_types_list = []
        self.file_name_list = []
        self.TEXT_FORMATS = [".txt", ".md"]

    async def load_responses(self):

        # Si alguien tiene una forma mas elegante de hacer esto que me mande PR
        # Lo he hecho para minimizar el tiempo de cambio de listas
        
        tmp_file_list = []
        tmp_file_types_list = []
        tmp_file_name_list = []

        tmp_file_list = os.listdir(self.autoresponse_path)
        for file in tmp_file_list:
            file, filetype = os.path.splitext(file)
            tmp_file_name_list.append(file)
            tmp_file_types_list.append(filetype)

        self.file_list = tmp_file_list
        self.file_types_list = tmp_file_types_list
        self.file_name_list = tmp_file_name_list

    # Si queréis podemos hacer que mande multiples mensajes de mas de 2kB
    # No sé por que querríais que hiciera eso, pero en fin.
    def read_text_file(self, path:str):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read(2000)
            return(text)
    
    def write_file(self, path, file):
        try:
            print("Path:")
            print(path)
            file.save(path)
            return(0)
        except Exception as e:
            print(e)
            return(-1)
        
    async def start_periodic_reload(self, interval: int = 60):
        while True:
            await self.load_responses()
            await asyncio.sleep(interval)