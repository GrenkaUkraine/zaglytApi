import traceback

from flask import Flask, request, jsonify, send_file
from generator import MarkovGenerator, DemotivatorGenerator, Mode
from config import *
import os


class ZaglytApi:
    def __init__(self):
        self.app = Flask(__name__)

        self.app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
        self.app.config['API_KEY'] = API_KEY
        self.app.config['MAX_FILE_SIZE'] = MAX_FILE_SIZE

        self.generator = None

        self.app.add_url_rule('/api/generate', 'generate', self.generate, methods=['POST'])
        self.app.add_url_rule('/api/generate/demotivator', 'generate_demotivator', self.generate_demotivator,
                              methods=['POST'])

        self.app.add_url_rule('/api/text/change_mode', 'change_mode', self.change_mode, methods=['POST'])

        self.app.add_url_rule('/api/config/max_file_size', 'config', self.get_max_file_size, methods=['GET'])

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.app.config['ALLOWED_EXTENSIONS']

    def get_max_file_size(self):
        return jsonify({'max_file_size_mb': self.app.config['MAX_FILE_SIZE']}), 200

    def change_mode(self):
        text = request.args.get('text')
        if not text:
            return jsonify({'error': 'Missing required argument "text"'}), 400
        mode = request.args.get('mode')
        if not mode:
            return jsonify({'error': 'Missing required argument "mode"'}), 400

        try:
            result = Mode.parse_mode(int(mode), text)
            return jsonify({'text': result}), 200
        except Exception as e:
            error_info = {
                'error': f'An error occurred: {str(e)}',
                'traceback': traceback.format_tb(e.__traceback__)
            }
            return jsonify(error_info), 500

    def generate(self):
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if 'x-api-key' in request.headers and request.headers['x-api-key'] == self.app.config['API_KEY']:
            pass
        else:
            if file.content_length > self.app.config['MAX_FILE_SIZE'] * 1024 * 1024:
                return jsonify({'error': 'File size exceeds the limit (10 MB)'}), 400

        maximum_length = request.args.get('maximum_length')
        if not maximum_length:
            return jsonify({'error': 'Missing required argument "maximum_length"'}), 400

        mode = request.args.get('mode', default=0)

        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, "temp")

        try:
            file.save(file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            self.generator = MarkovGenerator(text_content, int(maximum_length))
            self.generator.generate()
            self.generator.change_mode(int(mode))
            generated_text = self.generator.generated_text

            return jsonify({'text': generated_text}), 200
        except Exception as e:
            error_info = {
                'error': f'An error occurred: {str(e)}',
                'traceback': traceback.format_tb(e.__traceback__)
            }
            return jsonify(error_info), 500
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def generate_demotivator(self):
        title = request.args.get('title')
        image_file = request.files.get('image')
        image_url = request.args.get('image_url')
        description = request.args.get('description', '')

        if not title:
            return jsonify({'error': 'Missing required field title'}), 400
        if not image_file and not image_url:
            return jsonify({'error': 'Missing required field image or image_url'}), 400

        max_file_size_mb = self.app.config['MAX_FILE_SIZE']
        if image_file:
            if image_file.content_length > max_file_size_mb * 1024 * 1024:
                return jsonify({'error': f'File size exceeds the limit ({max_file_size_mb} MB)'}), 400

        if image_file:
            image_path = ZaglytApi.save_uploaded_image(image_file)
        else:
            image_path = ZaglytApi.download_image_from_url(image_url)

        output_dir = 'generated'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join('generated', 'demotivator.jpg')
        if os.path.exists(output_path):
            os.remove(output_path)
        try:
            demotivator_generator = DemotivatorGenerator(title, image_path, description)
            demotivator_generator.generate()
            demotivator_generator.save_image(output_path)
            os.remove(image_path)

            return send_file(output_path, download_name="demotivator.jpg"), 200
        except Exception as e:
            error_info = {
                'error': f'An error occurred during demotivator generation: {str(e)}',
                'traceback': traceback.format_tb(e.__traceback__)
            }
            return jsonify(error_info), 500
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    def run(self, debug: bool = False):
        self.app.run(debug=debug)

    @staticmethod
    def save_uploaded_image(file):
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, "temp")
        file.save(file_path)
        return file_path

    @staticmethod
    def download_image_from_url(url):
        import requests
        response = requests.get(url)
        if response.status_code == 200:
            image_path = 'temp_image.jpg'
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return image_path
        else:
            raise Exception(f"Failed to download image from URL: {url}")


if __name__ == '__main__':
    api = ZaglytApi()
    api.run(True)
