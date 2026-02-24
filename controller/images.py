from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import hashlib
from typing import List, Tuple

class TemplateWorker:
    def __init__(
        self,
        rect_top_left: List[int] = [10, 10],
        rect_bottom_right: List[int] = [500, 300],
        font_path: str = 'FreeMono.ttf',
        font_size: int = 65,
        font_color: Tuple[int, int, int] = (255, 0, 0)
    ):
        self.rect_top_left = rect_top_left
        self.rect_bottom_right = rect_bottom_right
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.I1 = None

    def imageWork(self, image_template_name: str, caption: str):
        print(f"Image template name: {image_template_name}")

        # Open an Image
        img = Image.open(f'image-templates/{image_template_name}.png')

        # Call draw Method to add 2D graphics in an image
        self.I1 = ImageDraw.Draw(img)

        # Calculate rectangle dimensions
        rect_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        rect_height = self.rect_bottom_right[1] - self.rect_top_left[1]

        # Load font
        try:
            myFont = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            myFont = ImageFont.load_default()

        # Wrapping text horizontally
        lines, total_text_height, line_height = self.wrap_text_to_fit(caption, myFont, rect_width, rect_height)

        # Adjust font size until text fits vertically
        while total_text_height > rect_height and self.font_size > 10:
            self.font_size -= 1
            myFont = ImageFont.truetype(self.font_path, self.font_size)
            lines, total_text_height, line_height = self.wrap_text_to_fit(caption, myFont, rect_width, rect_height)

        # Center the text in the rectangle
        y_text = self.rect_top_left[1] + (rect_height - total_text_height) // 2

        # Draw each line of text
        for line in lines:
            text_width, _ = self.get_text_dimensions(line, myFont)
            x_text = self.rect_top_left[0] + (rect_width - text_width) // 2
            self.I1.text((x_text, y_text), line, font=myFont, fill=self.font_color)
            y_text += line_height

        # Ensure the tmp directory exists
        os.makedirs("image-templates/tmp", exist_ok=True)

        # Generate a unique filename using a hash
        unique_id = hashlib.md5(caption.encode()).hexdigest()[:10]

        # Save the edited image with a unique filename
        img.save(f"image-templates/tmp/{image_template_name}-{unique_id}.png")

        return unique_id

    def get_text_dimensions(self, text, font):
        # Use textbbox for more accurate measurements
        bbox = self.I1.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def wrap_text_to_fit(self, text, font, max_width, max_height):
        # Wrap the text to fit within max_width
        avg_char_width = self.get_text_dimensions("W", font)[0]  # Approximate average character width
        max_chars_per_line = max(1, int(max_width / avg_char_width))
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)
        lines = wrapped_text.split('\n')

        # Calculate total height of the wrapped text
        line_height = self.get_text_dimensions("Ag", font)[1]  # Approximate line height
        total_text_height = len(lines) * line_height

        return lines, total_text_height, line_height
