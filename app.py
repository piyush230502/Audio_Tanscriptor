import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from backend.backend import transcribe_file

logging.basicConfig(level=logging.INFO)



app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load API key
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        try:
            if 'audiofile' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['audiofile']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                transcript = transcribe_file(filepath)
                flash('File successfully transcribed!')
        except Exception as e:
            logging.error(f"Error during file upload or transcription: {e}")
            flash('An error occurred during transcription.')

    return render_template("index.html", transcript=transcript)

if __name__ == "__main__":
    app.run(debug=True,port = 5050)
