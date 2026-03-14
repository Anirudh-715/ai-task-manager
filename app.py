from flask import Flask, render_template, request, redirect, session
from authlib.integrations.flask_client import OAuth
from database import db
from models import User
from task_manager import get_tasks, generate_insights
from ai_engine import analyze_mood, ai_chat
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
chat_memory = {}
user_tasks = {}
app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db.init_app(app)


# GOOGLE OAUTH SETUP

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# LOGIN WITH GOOGLE

@app.route("/login")
def login():
    return google.authorize_redirect("http://127.0.0.1:5500/auth")


# GOOGLE CALLBACK

@app.route("/auth")
def auth():

    token = google.authorize_access_token()

    resp = google.get("https://openidconnect.googleapis.com/v1/userinfo")

    user_info = resp.json()

    session["user"] = user_info

    return redirect("/")


# LOGOUT

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


# HOME PAGE

@app.route("/")
def home():

    user = session.get("user")

    return render_template("index.html", user=user)


# HISTORY API

@app.route("/history")
def history():

    if "user" not in session:
        return []

    user_email = session["user"]["email"]

    filename = f"{user_email}_history.json"

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except:
        data = []

    return data


# TASK GENERATION

@app.route("/tasks", methods=["POST"])
def generate_tasks():

    if "user" not in session:
        return redirect("/login")

    user_email = session["user"]["email"]

    filename = f"{user_email}_history.json"

    user_text = request.form["mood"]

    ai_result = analyze_mood(user_text)

    mood = "unknown"
    energy = 5

    for line in ai_result.split("\n"):

        if "mood" in line:
            mood = line.split(":")[1].strip()

        if "energy" in line:
            try:
                energy = int(line.split(":")[1].strip())
            except:
                energy = 5


    data = {
        "mood": mood,
        "energy": energy,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


    try:
        with open(filename, "r") as f:
            history = json.load(f)
    except:
        history = []


    history.append(data)


    with open(filename, "w") as f:
        json.dump(history, f, indent=4)


    insights = generate_insights(history)

    recommended = get_tasks(energy)


    return render_template(
    "dashboard.html",
    mood=mood,
    energy=energy,
    tasks=recommended,
    insights=insights,
    user=session.get("user")
)

@app.route("/add_task", methods=["POST"])
def add_task():

    if "user" not in session:
        return {"status": "error"}

    user_email = session["user"]["email"]

    task_text = request.json["task"]
    priority = request.json["priority"]
    date = request.json["date"]

    filename = f"{user_email}_tasks.json"

    try:
        with open(filename, "r") as f:
            tasks = json.load(f)
    except:
        tasks = []

    tasks.append({
        "text": task_text,
        "priority": priority,
        "date": date
    })

    with open(filename, "w") as f:
        json.dump(tasks, f)

    return {"status": "ok"}
@app.route("/get_tasks")
def get_user_tasks():

    if "user" not in session:
        return []

    user_email = session["user"]["email"]

    filename = f"{user_email}_tasks.json"

    try:
        with open(filename, "r") as f:
            tasks = json.load(f)
    except:
        tasks = []

    return tasks

@app.route("/chat", methods=["POST"])
def chat():

    if "user" not in session:
        return {"reply": "Please login first."}

    user_email = session["user"]["email"]

    user_message = request.json["message"]

    if user_email not in chat_memory:
        chat_memory[user_email] = []

    chat_memory[user_email].append(
        {"role": "user", "content": user_message}
    )

    response = ai_chat(chat_memory[user_email])

    chat_memory[user_email].append(
        {"role": "assistant", "content": response}
    )

    return {"reply": response}
# PRODUCTIVITY SCORE

@app.route("/complete", methods=["POST"])
def complete_tasks():

    completed = request.form.getlist("completed")

    total_tasks = 3

    score = int((len(completed) / total_tasks) * 100)

    return render_template(
        "result.html",
        score=score
    )


if __name__ == "__main__":
    app.run(debug=True, port=5500)


with app.app_context():
    db.create_all()

