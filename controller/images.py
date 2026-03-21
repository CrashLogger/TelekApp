from PIL import Image, ImageDraw, ImageFont
from controller.textworker import TextWorker
import io
import os
import hashlib
from typing import List
import discord

def tmp_image_cleanup(file_path: str):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
class TemplateWorker:
    def __init__(
        self,
        image_template_name: str,
        image_command_name: str,
        rect_top_left: List[int] = [10, 10],
        rect_bottom_right: List[int] = [500, 300],
        font_name: str = 'Roboto',
        font_colour: str = 'FFFFFF'
    ):
        self.rect_top_left = rect_top_left
        self.image_template_name = str(image_template_name)
        self.rect_bottom_right = rect_bottom_right
        self.font_path = f"media/fonts/{font_name}.ttf"
        self.image_command_name = image_command_name

        # Convertir la string #ABCDEF00 en un tuple de colores
        self.font_colour = tuple(int(font_colour[i:i+2], 16) for i in (0, 2, 4))

        self.I1 = None
        self.image = None

    # ============================================================================================================================================== #
    # Junta dos frames. Lo usan image_and_image y image_and_animated_gif
    # ============================================================================================================================================== #

    def image_into_image(self, template:Image, image_pip:Image):
        # Tamaño de la imagen
        target_width = self.rect_bottom_right[0] - self.rect_top_left[0]
        target_height = self.rect_bottom_right[1] - self.rect_top_left[1]
        image_pip = image_pip.resize((target_width, target_height))

        # Para centrar la imagen como un pro
        paste_x = self.rect_top_left[0] + (target_width - image_pip.width) // 2
        paste_y = self.rect_top_left[1] + (target_height - image_pip.height) // 2

        template.paste(image_pip, (paste_x, paste_y), image_pip)
        return(template)

    # ============================================================================================================================================== #
    # Alinea una imagen en otra imagen
    # ============================================================================================================================================== #

    def image_and_image(self, image_data:discord.Attachment):
        # Abrir ambas imagenes
        image_data = bytes(image_data)
        self.image = Image.open(f'media/templates/{self.image_template_name}').convert("RGBA")
        image_pip = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # Juntar y guardar
        result_image:Image = self.image_into_image(template=self.image, image_pip=image_pip)
        os.makedirs("media/tmp", exist_ok=True)
        unique_id = hashlib.md5(image_data).hexdigest()[:10]
        result_image.save(f"media/tmp/{self.image_command_name}-{unique_id}.png")
        return unique_id

    # ============================================================================================================================================== #
    # Alinea un gif en una imagen
    # ============================================================================================================================================== #

    def image_and_animated_gif(self, image_data:discord.Attachment):
        # Juntamos una template con todos los frames de un gif y sacamos un gif de vuelta con mucho swag
        # Open the template image
        template:Image = Image.open(f'media/templates/{self.image_template_name}').convert("RGBA")
        original_width, original_height = template.size
        max_gif_width = 800
        max_gif_height = 600
        if original_width > 800 or original_height > 600:
            template.thumbnail((max_gif_width, max_gif_height), Image.Resampling.LANCZOS)
            self.rect_top_left = (int((self.rect_top_left[0]/original_width)*template.size[0]), int((self.rect_top_left[1]/original_height)*template.size[1]))
            self.rect_bottom_right = (int((self.rect_bottom_right[0]/original_width)*template.size[0]), int((self.rect_bottom_right[1]/original_height)*template.size[1]))

        image_data = bytes(image_data)
        # Abrimos el gif
        with Image.open(io.BytesIO(image_data)) as gif:
            if not getattr(gif, 'is_animated', False):
                # Si es un gif raro de esos en plan logo, nos da igual que sea un gif, lo podemos tratar como png
                return self.image_and_image(image_data)

            frames = []
            durations = []

            # Procesamos todos los frames hasta que se acaben. No sé como sacar cuantos frames hay de un gif sin hacer esto primero.
            try:
                while True:
                    # Create a copy of the template for each frame
                    frame = template.copy()

                    # Sacamos cada imagen del gif y la guardamos como un PNG en el espacio RGBA
                    # Si no haces RGBA, al ser un gif, a veces la lia y lo hace todo opaco
                    gif.seek(gif.tell())
                    current_frame = gif.convert("RGBA")

                    # Funcioncita pro que junta imagenes, guardamos todos los frames en una lista
                    frame = self.image_into_image(template=frame, image_pip=current_frame)
                    frames.append(frame.copy())

                    # Sacar la duración del frame del gif original
                    # Si no dice nada, ponemos a 100 porque si
                    durations.append(gif.info.get('duration', 100))

                    # Move to the next frame
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass  # End of sequence

            if not frames:
                # Si falla a detectar frames asumimos que es uno solo, y que esa función nos diga si algo va mal
                return self.image_and_image(image_data)

            # Guardar
            os.makedirs("media/tmp", exist_ok=True)
            unique_id = hashlib.md5(image_data).hexdigest()[:10]
            output_path = f"media/tmp/{self.image_command_name}-{unique_id}.gif"

            # Save the first frame to get the dimensions
            frames[0].save(
                output_path,
                format="GIF",
                append_images=frames[1:],
                save_all=True,
                duration=durations,
                loop=0,  # Loop forever - Otra cosa mas que he robado sin saber muy bien por qué
                disposal=2  # Tira el frame anterior del gif. No nos va a hacer falta hasta que tengamos templates transparentes
            )

            # Esto estaba en el ejemplo y el gatito quiere que lo mantenga. Ahí se queda.
            # Store the first frame as self.image for consistency
            self.image = frames[0]

            return unique_id

    # ============================================================================================================================================== #
    # Alinea una string en una imagen
    # ============================================================================================================================================== #

    def image_and_text(self, caption: str):
        # Open an Image
        print(self.image_template_name)
        self.image = Image.open(f"media/templates/{self.image_template_name}")

        # Call draw Method to add 2D graphics in an image
        self.I1 = ImageDraw.Draw(self.image)

        textWorker = TextWorker(self.I1, font_path=self.font_path, textbox_topleft=self.rect_top_left, textbox_bottomright=self.rect_bottom_right, font_colour=self.font_colour)
        self.I1 = textWorker.text_auto_fit(caption=caption)

        # Guardamos archivo temporal
        os.makedirs("media/tmp", exist_ok=True)
        unique_id = hashlib.md5(caption.encode()).hexdigest()[:10]
        self.image.save(f"media/tmp/{self.image_command_name}-{unique_id}.png")

        return unique_id
    
class OverlayWorker:
    def __init__(
            self,
            image_overlay_name: str,
            overlay_file_name: str,
            overlay_offset_leftright: int,
            overlay_offset_updown: int
        ):
        self.image_overlay_name = image_overlay_name
        self.overlay_file_name = overlay_file_name
        self.overlay_overhang_leftright = overlay_offset_leftright
        self.overlay_overhang_updown = overlay_offset_updown
        self.overlay_image = Image.open(f"media/overlays/{self.overlay_file_name}").convert("RGBA")

    # ============================================================================================================================================== #
    # Ingesta de imágenes y tamaños, bare minimum
    # ============================================================================================================================================== #

    def rectangle_overlay(self, image_data:discord.Attachment):

        self.image_data = bytes(image_data)
        original_image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # Tamaño de la imagen
        self.orig_width = original_image.size[0]
        self.orig_height = original_image.size[1]
        self.over_width = self.overlay_image.size[0]
        self.over_height = self.overlay_image.size[1]

        msg = self.overlay_place(self.overlay_image, original_image)
        return(msg)

    # ============================================================================================================================================== #
    # Junta la imagen de overlay encima de la imagen del usuario
    # ============================================================================================================================================== #

    def overlay_place(self, overlay:Image, userImage:Image):
        try:
            # Las overlays probablemente requieran cambiar de tamaño y que sigan el tamaño de la imagen del usuario
            # A diferencia de las imagenes de usuario, estas no las queremos distorsionar
            # El best effort se nota: Vamos a hacer que la overlay esté en la misma escala que la imagen que nos han dado

            resizedOverlay = overlay.copy()
            resizedOverlay = overlay.resize(userImage.size, Image.Resampling.LANCZOS)
            sizeRatio = max(resizedOverlay.size[0]/self.over_width, resizedOverlay.size[1]/self.over_height)

            adjusted_overhang_leftright = int(sizeRatio*self.overlay_overhang_leftright)
            adjusted_overhang_updown = int(sizeRatio*self.overlay_overhang_updown)

            # Posiciones
            user_x = max(0, adjusted_overhang_leftright)
            user_y = max(0, adjusted_overhang_updown)
            overlay_x = max(0, -adjusted_overhang_leftright)
            overlay_y = max(0, -adjusted_overhang_updown)

            # Hacemos una imagen nueva y pegamos todo encima de mala manera, pero eso es sorprendentemente la mejor manera.
            canvas_width = (max(self.orig_width, resizedOverlay.size[0])+abs(adjusted_overhang_leftright))
            canvas_height = (max(self.orig_height, resizedOverlay.size[1])+abs(adjusted_overhang_updown))
            canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            canvas.paste(userImage, (user_x, user_y), userImage)
            canvas.paste(resizedOverlay, (overlay_x, overlay_y), resizedOverlay)

            # Guardar el fitxategi
            unique_id = hashlib.md5(self.image_data).hexdigest()[:10]
            output_path = f"media/tmp/{self.image_overlay_name}-{unique_id}.png"
            canvas.save(output_path)
            return (unique_id)
        except Exception as e:
            print(e)
            return(-1)