from flask import Flask, render_template, request

from modules.db import add_case

import os, uuid

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

def save_image(image):
    if not image or image.filename == "":
        return "" 
                         # no image uploaded
    ext = os.path.splitext(image.filename)[1].lower()
    new_name = uuid.uuid4().hex + ext
    path = os.path.join(app.config["UPLOAD_FOLDER"], new_name)
    image.save(path)
    return path

@app.route("/")
def new_case():
    return render_template("input.html")

@app.route("/submit", methods=["POST"])
def submit():
    username = request.form.get("username", "").strip()
    location = request.form.get("claimed_location", "").strip()
    
    if not username:
        return "Username is required", 400
    
    image = request.files.get("photo")
    image_name = save_image(image)
    case_id = add_case(username, image_name, location)
    return f"Case {case_id} saved"   # proper page comes on Day 15

if __name__ == "__main__":
    app.run(debug=True)

