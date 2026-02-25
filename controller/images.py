from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import hashlib
from typing import List, Tuple

class TemplateWorker:
    def __init__(
        self,
        image_template_name: str,
        rect_top_left: List[int] = [10, 10],
        rect_bottom_right: List[int] = [500, 300],
        font_path: str = 'Roboto',
        font_size: int = 65,
        font_color: Tuple[int, int, int] = (255, 0, 0)
    ):
        self.rect_top_left = rect_top_left
        self.image_template_name = str(image_template_name),
        self.image_template_name = self.image_template_name[0]
        self.rect_bottom_right = rect_bottom_right
        self.font_path = f"image-templates/fonts/{font_path}.ttf"
        print(f"font path {self.font_path}")
        self.font_size = font_size
        self.font_color = font_color
        self.I1 = None

    def imageWork(self, caption: str):
        # Open an Image
        print("Vamos no me jodas")
        print(self.image_template_name)
        img = Image.open(f'image-templates/{self.image_template_name}.png')

        # Call draw Method to add 2D graphics in an image
        self.I1 = ImageDraw.Draw(img)

        # Calculate rectangle dimensions
        rect_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        rect_height = self.rect_bottom_right[1] - self.rect_top_left[1]
        print(f"Rectangle dimensions: {rect_width}x{rect_height}")

        # Load font
        print(f"LOOKING FOR: {self.font_path}")
        try:
            myFont = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            myFont = ImageFont.load_default()
            print("Using default font")

        # Measure actual font height
        _, font_height = self.get_text_dimensions("Ag", myFont)
        print(f"Font size: {self.font_size}, Actual font height: {font_height} pixels")

        # Wrapping text horizontally
        lines, total_text_height, line_height = self.wrap_text_to_fit(caption, myFont, rect_width, rect_height)
        print(f"Initial total text height: {total_text_height}")

        # Adjust font size until text fits vertically
        while total_text_height > rect_height and self.font_size > 10:
            self.font_size -= 1
            myFont = ImageFont.truetype(self.font_path, self.font_size)
            _, font_height = self.get_text_dimensions("Ag", myFont)
            print(f"Trying font size: {self.font_size}, Actual font height: {font_height} pixels")
            lines, total_text_height, line_height = self.wrap_text_to_fit(caption, myFont, rect_width, rect_height)

        print(f"Final font size: {self.font_size}, Actual font height: {font_height} pixels, Total text height: {total_text_height}")

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
        img.save(f"image-templates/tmp/{self.image_template_name}-{unique_id}.png")

        return unique_id

    def get_text_dimensions(self, text, font):
        # Use textbbox for more accurate measurements
        bbox = self.I1.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def wrap_text_to_fit(self, text, font, max_width, max_height):
        # Measure the width of a typical character to estimate max characters per line
        avg_char_width, _ = self.get_text_dimensions("W", font)
        max_chars_per_line = max(1, int(max_width / avg_char_width))

        # Use TextWrapper to avoid splitting words
        wrapper = textwrap.TextWrapper(width=max_chars_per_line, break_long_words=False, break_on_hyphens=False)
        wrapped_text = wrapper.fill(text)
        lines = wrapped_text.split('\n')

        # Measure the height of a line of text
        _, line_height = self.get_text_dimensions("Ag", font)

        # Calculate total height of the wrapped text
        total_text_height = len(lines) * line_height

        return lines, total_text_height, line_height

