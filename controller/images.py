from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from typing import List 
import textwrap

def imageWork(image_template_name: str, caption: str, startcorner: List[int], endcorner: List[int], font: str = "FreeMono"):
    # Open an Image
    img = Image.open(f'image-templates/{image_template_name}.png')

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)

    # Custom font style and font size
    font_size = 24
    myFont = ImageFont.truetype(f'image-templates/fonts/{font}.ttf', font_size)

    rect_width = endcorner[0] - startcorner[0]

# Calculate max characters per line based on rectangle width
    # This is a rough estimate; you may need to adjust it
    avg_char_width = font_size * 0.2  # Approximate average character width
    max_chars_per_line = int(rect_width / avg_char_width)

    # Wrap the text to fit within the rectangle's width
    wrapped_text = textwrap.fill(caption, width=max_chars_per_line)

    # Split the wrapped text into lines
    lines = wrapped_text.split('\n')

    # Calculate the total height required for the text
    line_height = font_size * 0.6  # Approximate line height
    total_text_height = len(lines) * line_height

    y_text = 10
    font_color = "#00FFFF"
    max_lines = 10

    for line in lines[:max_lines]:  # Limit the number of lines to prevent overflow
        I1.text((10, y_text), line, font=myFont, fill=font_color)
        y_text += font_size  # Move down for the next line

    # Save the edited image
    img.save(f"image-templates/tmp/{image_template_name}CAP{caption}.png")