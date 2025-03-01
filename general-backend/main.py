from app import create_app
from flask import jsonify

app = create_app()

@app.route("/", methods=["GET", "POST"])
def home():
    return "Welcome to the API"

if __name__ == "__main__":
    app.run(debug=True)
