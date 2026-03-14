tasks = {
    "easy": [
        "Check emails",
        "Organize notes",
        "Review today's goals"
    ],
    
    "medium": [
        "Practice coding",
        "Work on project module",
        "Study new topic"
    ],
    
    "hard": [
        "Solve algorithm problems",
        "Deep research reading",
        "Build project feature"
    ]
}


def get_tasks(energy):

    if energy <= 3:
        return tasks["easy"]

    elif energy <= 7:
        return tasks["medium"]

    else:
        return tasks["hard"]
    


def generate_insights(history):

    if len(history) < 3:
        return "Not enough data yet. Keep using the app!"

    last_three = history[-3:]

    avg_energy = sum([h["energy"] for h in last_three]) / 3

    if avg_energy <= 3:
        return "⚠ Your energy has been low recently. Consider taking breaks or doing lighter tasks."

    if avg_energy >= 7:
        return "🔥 Your energy levels are high. Great time for deep work!"

    return "⚖ Your energy seems balanced. Maintain a healthy routine."