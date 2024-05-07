import traceback

from flask import Flask, request, jsonify
from generator import MarkovGenerator
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

        self.app.add_url_rule('/api/config/max_file_size', 'config', self.get_max_file_size, methods=['GET'])

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.app.config['ALLOWED_EXTENSIONS']

    def get_max_file_size(self):
        return jsonify({'max_file_size_mb': self.app.config['MAX_FILE_SIZE']}), 200

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

    def run(self, debug: bool = False):
        self.app.run(debug=debug)


if __name__ == '__main__':
    api = ZaglytApi()
    api.run(True)
