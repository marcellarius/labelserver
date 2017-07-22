from labelserver import app

@app.route("/")
def home():
    return "Home"
