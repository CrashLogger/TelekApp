from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import hashlib
from typing import List

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

    def imageWork(self, caption: str):
        # Open an Image
        print(self.image_template_name)
        img = Image.open(f'image-templates/{self.image_template_name}.png')

        # Call draw Method to add 2D graphics in an image
        self.I1 = ImageDraw.Draw(img)

        # Calculate rectangle dimensions
        rect_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        rect_height = self.rect_bottom_right[1] - self.rect_top_left[1]
        
        # Small padding (Extra aid just in case the same thing that happened before happens again)
        padding = 5
        max_text_width = rect_width - (2 * padding)
        max_text_height = rect_height - (2 * padding)

        # Load font
        try:
            myFont = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            myFont = ImageFont.load_default()
            print("Using default font")

        # Function to wrap text optimally
        def get_optimal_wrapping(text, font, max_width):
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                # Try adding the next word
                test_line = ' '.join(current_line + [word])
                bbox = self.I1.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:  # Save the current line if it's not empty
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            # Add the last line
            if current_line:
                lines.append(' '.join(current_line))
            
            # If no lines were created (single word too long), force split
            if not lines and words:
                # Split the word character by character as last resort
                word = words[0]
                current_line = ""
                for char in word:
                    test_line = current_line + char
                    bbox = self.I1.textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = char
                if current_line:
                    lines.append(current_line)
            
            return lines

        # Function to check if text fits
        def text_fits(font, lines, max_height):
            if not lines:
                return True
            # Measure total height
            bbox = self.I1.textbbox((0, 0), "Ag", font=font)
            line_height = bbox[3] - bbox[1]
            total_height = len(lines) * line_height
            return total_height <= max_height

        # Try to find the optimal font size
        current_font_size = self.font_size
        best_font = myFont
        best_lines = []
        
        # Don't go below minimum readable size
        while current_font_size >= 10:
            try:
                test_font = ImageFont.truetype(self.font_path, current_font_size)
            except IOError:
                test_font = ImageFont.load_default()
            
            # Wrap text with this font size
            lines = get_optimal_wrapping(caption, test_font, max_text_width)
            
            # Check if it fits vertically
            if text_fits(test_font, lines, max_text_height):
                best_font = test_font
                best_lines = lines
                # Break when we've found a working size
                break
            else:
                current_font_size -= 2  # Reduce font size more aggressively
        
        # If we never found a fitting size, use the smallest we tried
        if not best_lines:
            # Use the smallest font size we tried
            current_font_size = 10
            best_font = ImageFont.truetype(self.font_path, current_font_size)
            best_lines = get_optimal_wrapping(caption, best_font, max_text_width)

        # Calculate line height
        bbox = self.I1.textbbox((0, 0), "Ag", font=best_font)
        line_height = bbox[3] - bbox[1]
        
        # Calculate total text height
        total_text_height = len(best_lines) * line_height
        
        # Center vertically in the rectangle (with padding considered)
        y_text = self.rect_top_left[1] + padding + (max_text_height - total_text_height) // 2

        # Draw each line of text
        for line in best_lines:
            bbox = self.I1.textbbox((0, 0), line, font=best_font)
            text_width = bbox[2] - bbox[0]
            x_text = self.rect_top_left[0] + padding + (max_text_width - text_width) // 2
            self.I1.text((x_text, y_text), line, font=best_font, fill=self.font_color)
            y_text += line_height

        # DEBUG: rectangle outline
        # self.I1.rectangle([self.rect_top_left, self.rect_bottom_right], outline="red", width=2)

        # Ensure the tmp directory exists
        os.makedirs("image-templates/tmp", exist_ok=True)

        # Generate a unique filename using a hash
        unique_id = hashlib.md5(caption.encode()).hexdigest()[:10]

        # Save the edited image with a unique filename
        img.save(f"image-templates/tmp/{self.image_template_name}-{unique_id}.png")

        return unique_id