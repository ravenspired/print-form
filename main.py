from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import os
import uuid
import json
import datetime

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
        emergency = request.form.get('emergency') == 'on'
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return "No valid files uploaded!"
        
        submission_id = str(uuid.uuid4())
        submission_folder = os.path.join(UPLOAD_FOLDER, submission_id)
        os.makedirs(submission_folder, exist_ok=True)
        timestamp = datetime.datetime.now().isoformat()
        saved_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(submission_folder, filename)
                file.save(filepath)
                saved_files.append(filename)
        
        submission = {
            "id": submission_id,
            "name": name,
            "email": email,
            "location_confirmed": location_confirmed,
            "location_details": location_details,
            "emergency": emergency,
            "files": saved_files,
            "timestamp": timestamp
        }
        
        with open(os.path.join(submission_folder, 'submission.json'), 'w') as f:
            json.dump(submission, f, indent=4)
        
        return "Files uploaded successfully!"
    
    return render_template('upload.html')

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('index'))
    submissions = []
    for submission_id in os.listdir(UPLOAD_FOLDER):
        submission_folder = os.path.join(UPLOAD_FOLDER, submission_id)
        if os.path.isdir(submission_folder):
            json_path = os.path.join(submission_folder, 'submission.json')
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    submissions.append(json.load(f))
    return render_template('admin.html', submissions=submissions)

@app.route('/download/<submission_id>/<filename>')
def download(submission_id, filename):
    if not session.get('admin'):
        return redirect(url_for('index'))
    submission_folder = os.path.join(UPLOAD_FOLDER, submission_id)
    return send_from_directory(submission_folder, filename)

@app.route('/delete_submission/<submission_id>')
def delete_submission(submission_id):
    if not session.get('admin'):
        return redirect(url_for('index'))
    submission_folder = os.path.join(UPLOAD_FOLDER, submission_id)
    if os.path.exists(submission_folder):
        for file in os.listdir(submission_folder):
            os.remove(os.path.join(submission_folder, file))
        os.rmdir(submission_folder)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
