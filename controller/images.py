from PIL import Image, ImageDraw, ImageFont
import io
import os
import hashlib
from typing import List
import discord

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

    def image_and_image(self, image_data:discord.Attachment):
        # Abrir ambas imagenes
        print(f"Opening template: {self.image_template_name}")
        self.image = Image.open(f'image-templates/{self.image_template_name}.png').convert("RGBA")
        image_pip = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # Tamaño de la imagen
        target_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        target_height = self.rect_bottom_right[1] - self.rect_top_left[1]
        image_pip.thumbnail((target_width, target_height))

        # Para centrar la imagen como un pro
        paste_x = self.rect_top_left[0] + (target_width - image_pip.width) // 2
        paste_y = self.rect_top_left[1] + (target_height - image_pip.height) // 2

        # Juntar y guardar
        self.image.paste(image_pip, (paste_x, paste_y), image_pip)
        os.makedirs("image-templates/tmp", exist_ok=True)
        unique_id = hashlib.md5(image_data).hexdigest()[:10]
        self.image.save(f"image-templates/tmp/{self.image_template_name}-{unique_id}.png")

        return unique_id

    def image_and_animated_gif(self, image_data:discord.Attachment):
        """
        Combine an animated GIF with a template image, creating a new animated GIF
        where the GIF maintains its animation on top of the template.

        Args:
            image_data: The bytes of the GIF to paste onto the template.
        """
        # Open the template image
        template = Image.open(f'image-templates/{self.image_template_name}.png').convert("RGBA")

        # Open the GIF
        with Image.open(io.BytesIO(image_data)) as gif:
            if not getattr(gif, 'is_animated', False):
                # If it's not a GIF, use the regular method
                return self.image_and_image(image_data)

            # Create a list to store the frames
            frames = []
            durations = []

            # Process each frame of the GIF
            try:
                while True:
                    # Create a copy of the template for each frame
                    frame = template.copy()

                    # Get the current frame of the GIF
                    gif.seek(gif.tell())
                    current_frame = gif.convert("RGBA")

                    # Resize the frame to fit the rectangle while maintaining aspect ratio
                    target_width = self.rect_bottom_right[0] - self.rect_top_left[0]
                    target_height = self.rect_bottom_right[1] - self.rect_top_left[1]

                    # Resize the frame
                    current_frame = current_frame.resize((target_width, target_height))

                    paste_x = self.rect_top_left[0] + (target_width - current_frame.width) // 2
                    paste_y = self.rect_top_left[1] + (target_height - current_frame.height) // 2

                    # Paste the frame
                    frame.paste(current_frame, (paste_x, paste_y), current_frame)

                    # Add the frame to our list
                    frames.append(frame.copy())

                    # Get the duration of the frame
                    durations.append(gif.info.get('duration', 100))

                    # Move to the next frame
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass  # End of sequence

            if not frames:
                # If we couldn't process any frames, use the regular method
                return self.image_and_image(image_data)

            # Save the animated GIF
            os.makedirs("image-templates/tmp", exist_ok=True)
            unique_id = hashlib.md5(image_data).hexdigest()[:10]
            output_path = f"image-templates/tmp/{self.image_template_name}-{unique_id}.gif"

            # Save the first frame to get the dimensions
            frames[0].save(
                output_path,
                format="GIF",
                append_images=frames[1:],
                save_all=True,
                duration=durations,
                loop=0,  # Loop forever
                disposal=2  # Use disposal method 2 for better transparency handling
            )

            # Store the first frame as self.image for consistency
            self.image = frames[0]

            return unique_id


    def image_and_text(self, caption: str):
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

        # Como se nota cuando cambio de sitio del que copio :3
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