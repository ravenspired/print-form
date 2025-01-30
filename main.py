from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a strong secret key

UPLOAD_FOLDER = 'uploads'
ARCHIVE_FOLDER = 'archives'
PASSWORD = 'userpassword'  # Change this to the shared password
ADMIN_PASSWORD = 'adminpassword'  # Change this to the admin password
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('upload'))
        elif password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('index.html', error="That password is incorrect")
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        location_confirmed = request.form.get('location_confirmed')
        location_details = request.form.get('location_details')
        emergency = request.form.get('emergency')
        file = request.files.get('file')
        
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            return "File uploaded successfully!"
    return render_template('upload.html')

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('index'))
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('admin.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    if not session.get('admin'):
        return redirect(url_for('index'))
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<filename>')
def delete(filename):
    if not session.get('admin'):
        return redirect(url_for('index'))
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for('admin'))

@app.route('/complete/<filename>')
def complete(filename):
    if not session.get('admin'):
        return redirect(url_for('index'))
    os.rename(os.path.join(UPLOAD_FOLDER, filename), os.path.join(ARCHIVE_FOLDER, filename))
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # app.run(host='192.168.1.112', port=5000, debug=True)
    app.run(debug=True)

