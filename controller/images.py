from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import hashlib
from typing import List
import math

class TemplateWorker:
    def __init__(
        self,
        image_template_name: str,
        rect_top_left: List[int] = [10, 10],
        rect_bottom_right: List[int] = [500, 300],
        font_name: str = 'Roboto',
        font_size: int = 200,
        font_colour: str = 'FFFFFF'
    ):
        self.rect_top_left = rect_top_left
        self.image_template_name = str(image_template_name)
        self.rect_bottom_right = rect_bottom_right
        self.font_path = f"image-templates/fonts/{font_name}.ttf"
        self.font_size = font_size

        # Convert HEX color string to RGB tuple
        self.font_color = tuple(int(font_colour[i:i+2], 16) for i in (0, 2, 4))

        self.I1 = None
        self.image = None

    def imageWork(self, caption: str):
        # Open an Image
        print(self.image_template_name)
        self.image = Image.open(f'image-templates/{self.image_template_name}.png')

        # Call draw Method to add 2D graphics in an image
        self.I1 = ImageDraw.Draw(self.image)

        # Calculate rectangle dimensions
        rect_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        rect_height = self.rect_bottom_right[1] - self.rect_top_left[1]
        
        # Small padding to prevent touching edges
        padding = 8
        max_text_width = rect_width - (2 * padding)
        max_text_height = rect_height - (2 * padding)

        # Load font
        try:
            myFont = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            myFont = ImageFont.load_default()
            print("Using default font")

        # Vamos a encontrar el tamaño del texto a base de coger un tamaño enorme y bajarlo hasta que quepa
        min_font_size = 8
        current_font_size = self.font_size
        best_font = myFont
        best_lines = []
        best_line_height = 0
        
        while current_font_size >= min_font_size:
            try:
                test_font = ImageFont.truetype(self.font_path, current_font_size)
            except IOError:
                test_font = ImageFont.load_default()
            
            # A ver que tal se separa en lineas
            lines = self.get_optimal_wrapping(caption, test_font, max_text_width)
            
            # A ver que tal cabe en vertical
            if self.text_fits(test_font, lines, max_text_height):
                best_font = test_font
                best_lines = lines
                best_line_height = self.get_line_height(test_font)
                break
            else:
                current_font_size -= 2
        
        # Si nada funciona, caso extremo con letra mas pequeña posible
        if not best_lines:
            current_font_size = min_font_size
            best_font = ImageFont.truetype(self.font_path, current_font_size)
            best_line_height = self.get_line_height(best_font)
            
            words = caption.split()
            best_lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.get_text_width(test_line, best_font) <= max_text_width:
                    current_line.append(word)
                else:
                    if current_line:
                        best_lines.append(' '.join(current_line))
                    # Separar palabras es una medida desesperada para casos desesperados
                    if self.get_text_width(word, best_font) > max_text_width:
                        split_words = self.split_long_word(word, best_font, max_text_width)
                        best_lines.extend(split_words)
                        current_line = []
                    else:
                        current_line = [word]
            
            if current_line:
                best_lines.append(' '.join(current_line))

        # Revisar en vertical de nuevo
        total_text_height = len(best_lines) * best_line_height
        y_text = self.rect_top_left[1] + padding + (max_text_height - total_text_height) // 2

        # Dibujar las lineas
        for i, line in enumerate(best_lines):
            raw_width = self.I1.textbbox((0, 0), line, font=best_font)[2] - self.I1.textbbox((0, 0), line, font=best_font)[0]
            x_text = self.rect_top_left[0] + padding + (max_text_width - raw_width) // 2
            self.I1.text((x_text, y_text), line, font=best_font, fill=self.font_color)
            y_text += best_line_height

        # Guardamos archivo temporal
        os.makedirs("image-templates/tmp", exist_ok=True)
        unique_id = hashlib.md5(caption.encode()).hexdigest()[:10]
        self.image.save(f"image-templates/tmp/{self.image_template_name}-{unique_id}.png")

        return unique_id
    
    # PAra dividir palabros
    def split_long_word(self, word, font, max_width):
        result = []
        current_segment = ""
        
        for char in word:
            test_segment = current_segment + char
            if self.get_text_width(test_segment, font) <= max_width:
                current_segment = test_segment
            else:
                if current_segment:
                    result.append(current_segment)
                current_segment = char
        
        if current_segment:
            result.append(current_segment)
        
        return result

    # Para medidas en vertical
    def text_fits(self, font, lines, max_height):
        if not lines:
            return True
        line_height = self.get_line_height(font)
        total_height = len(lines) * line_height
        return total_height <= max_height
    
        # Function to get actual text width with a small safety margin
    def get_text_width(self, text, font):
        bbox = self.I1.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        # Add a small safety margin (2% or 2 pixels, whichever is larger)
        safety_margin = max(2, width * 0.02)
        return width + safety_margin

    # Para sacar cuanto mide una linea de texto, en vertical, en el peor de los casos
    def get_line_height(self, font):
        bbox = self.I1.textbbox((0, 0), "Ag", font=font)
        return bbox[3] - bbox[1]

    # Para separar las lineas del texto acorde al espacio disponible
    def get_optimal_wrapping(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = self.get_text_width(test_line, font)
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    # Si hay algo, eso nos sirve como linea
                    lines.append(' '.join(current_line))

                # Palabros muy largos:
                word_width = self.get_text_width(word, font)
                if word_width > max_width:
                    split_word_lines = self.split_long_word(word, font, max_width)
                    lines.extend(split_word_lines)
                    current_line = []
                else:
                    current_line = [word]
        
        #El final, que debería quedar algo siempre
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines