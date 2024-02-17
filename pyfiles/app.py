from flask import Flask, render_template, request, jsonify
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        text = ''
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

        # print(text)
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
