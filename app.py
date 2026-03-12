from flask import Flask, render_template, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    file_path = 'dist/ЭлектроКвест.exe'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name='ЭлектроКвест.exe')
    return "Файл пока не доступен. Соберите exe на Windows и поместите в папку dist/", 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
