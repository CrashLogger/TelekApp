import os

class ioHelpers:

    def __init__(self, autoresponse_path):
        self.autoresponse_path = autoresponse_path
        self.file_list = []
        self.file_types_list = []
        self.file_name_list = []
        self.TEXT_FORMATS = [".txt", ".md"]

    def load_responses(self):
        self.file_list = os.listdir(self.autoresponse_path)
        for file in self.file_list:
            file, filetype = os.path.splitext(file)
            self.file_name_list.append(file)
            self.file_types_list.append(filetype)
        print(self.file_name_list)

    def read_text_file(self, path:str):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read(2000)
            return(text)