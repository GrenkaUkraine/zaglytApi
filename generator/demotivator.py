from PIL import Image, ImageDraw, ImageFont, ImageOps


class DemotivatorGenerator:
    def __init__(self, title_text: str, image_file: str, description: str = ''):
        self.drawer = None
        self.img = None
        self.title_text = title_text
        self.image_file = image_file
        self.description = description

    def generate(self):
        self.create_main()
        self.add_text()
        return self.img

    def create_main(self):
        self.img = Image.new('RGB', (1280, 1024), color='black')
        border = ImageOps.expand(Image.new('RGB', (1060, 720), color='black'), border=2, fill='white')
        user_img = Image.open(self.image_file).convert("RGBA").resize((1050, 710))
        self.img.paste(border, (111, 96))
        self.img.paste(user_img, (118, 103))
        self.drawer = ImageDraw.Draw(self.img)

    def add_text(self):
        font_path = 'times.ttf'
        title_font = DemotivatorGenerator.get_optimal_font(font_path, self.title_text, self.img.width - 20, 80)
        desc_font = DemotivatorGenerator.get_optimal_font(font_path, self.description, self.img.width - 20, 60)

        self.add_text_centered(self.title_text, title_font, 840, 'white')
        self.add_text_centered(self.description, desc_font, 930, 'white')

    @staticmethod
    def get_optimal_font(font_path: str, text: str, max_width: int, initial_size: int) -> ImageFont.FreeTypeFont:
        font_size = initial_size
        font = ImageFont.truetype(font=font_path, size=font_size, encoding='UTF-8')
        text_width = font.getlength(text)

        while text_width >= max_width:
            font = ImageFont.truetype(font=font_path, size=font_size, encoding='UTF-8')
            text_width = font.getlength(text)
            font_size -= 1

        return font

    def add_text_centered(self, text: str, font: ImageFont.FreeTypeFont, y_position: int, fill_color: str):
        text_width = self.drawer.textlength(text, font=font)
        x_position = (self.img.width - text_width) / 2
        self.drawer.text((x_position, y_position), text, fill=fill_color, font=font)

    def save_image(self, output_path: str):
        if self.img:
            self.img.save(output_path)
            return True
        else:
            return False
