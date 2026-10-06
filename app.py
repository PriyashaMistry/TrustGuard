from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def new_case():
    return render_template("input.html")
@app.route("/submit", methods=["POST"])
def submit():
    username = request.form["username"]
    location = request.form.get("claimed_location", "")
    photo = request.files["photo"]
    # Not saving to the database yet (that comes later)
    return f"Received {username}, {location}, {photo.filename}"
if __name__ == "__main__":
    app.run(debug=True)