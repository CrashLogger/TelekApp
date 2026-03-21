from PIL import ImageDraw, ImageFont
from typing import List

class TextWorker:
    def __init__(
        self,
        draw_canvas: ImageDraw.Draw,
        font_path: str = None,
        textbox_topleft: List[int] = None,
        textbox_bottomright: List[int] = None,
        font_colour: tuple = (255, 255, 255, 255)
    ):
        self.draw_canvas = draw_canvas
        self.font_path = font_path
        self.font_colour = font_colour
        print(self.font_colour)
        self.rect_top_left = textbox_topleft
        self.rect_bottom_right = textbox_bottomright

        # Cuadrícula donde irá el texto
        self.rect_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        self.rect_height = self.rect_bottom_right[1] - self.rect_top_left[1]

        # Un poco de margen en el tamaño maximo del textio
        self.padding = 5
        self.max_text_width = self.rect_width - (2 * self.padding)
        self.max_text_height = self.rect_height - (2 * self.padding)

        # Font size maximos y minimos, arbitrarios
        self.min_font_size = 8
        self.font_size = 200

        # Intentamos cargar la fuente pedida. Si falla, va a roboto. Si roboto falla, usamos la default (pixel art)
        try:
            self.imageFont = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            try:
                self.font_path = "media/fonts/roboto.ttf"
                self.imageFont = ImageFont.truetype(self.font_path, self.font_size)
            except IOError:
                self.imageFont = ImageFont.load_default()
                print("Using default font")

    # Dividimos palabros, en principio esto es para casos extremos solo
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

    # Comprobar si el texto cabe en el eje Y
    def text_fits(self, lines, font, max_height):
        if not lines:
            return True
        line_height = self.get_line_height(font)
        total_height = len(lines) * line_height
        return total_height <= max_height

    # Calculamos la anchura del texto pedido, normalmente tras ser dividido
    def get_text_width(self, text, font):
        bbox = self.draw_canvas.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        safety_margin = max(2, width * 0.02)
        return width + safety_margin

    # Calculamos la altura de cada linea de texto con la fuente y tamaño pedidos
    def get_line_height(self, font):
        bbox = self.draw_canvas.textbbox((0, 0), "Ag", font=font)
        return bbox[3] - bbox[1]

    # La brujería que copié que consigue (mas o menos) dividir el texto de forma bonica
    def get_optimal_wrapping(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.get_text_width(test_line, font) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                word_width = self.get_text_width(word, font)
                if word_width > max_width:
                    split_word_lines = self.split_long_word(word, font, max_width)
                    lines.extend(split_word_lines)
                    current_line = []
                else:
                    current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    # El "algoritmo" que busca el mejor tamaño de todo para la cantidad de texto y caja entregadas
    def text_auto_fit(self, caption: str):
        current_font_size = self.font_size
        best_font = None
        best_lines = []
        best_line_height = 0

        # Repite hasta llegar al tamaño minimo
        while current_font_size >= self.min_font_size:
            try:
                test_font = ImageFont.truetype(self.font_path, current_font_size)
            except IOError:
                test_font = ImageFont.load_default()

            lines = self.get_optimal_wrapping(caption, test_font, self.max_text_width)
            if self.text_fits(lines, test_font, self.max_text_height):
                best_font = test_font
                best_lines = lines
                best_line_height = self.get_line_height(test_font)
                break
            else:
                current_font_size -= 2

        # Última comprobación del eje Y
        total_text_height = len(best_lines) * best_line_height
        y_text = self.rect_top_left[1] + self.padding + (self.max_text_height - total_text_height) // 2

        for line in best_lines:
            raw_width = self.get_text_width(line, best_font)
            x_text = self.rect_top_left[0] + self.padding + (self.max_text_width - raw_width) // 2
            self.draw_canvas.text((x_text, y_text), line, font=best_font, fill=self.font_colour)
            y_text += best_line_height
