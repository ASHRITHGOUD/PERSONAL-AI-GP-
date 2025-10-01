# backend/core/natural_language_understanding.py

import re
# CORRECTED IMPORT: Go up one level (..) to 'backend', then down to 'tasks.workers'
from ..tasks.workers.utility_worker import set_reminder, add_note, get_notes, get_weather, web_search, send_email, calculate

def detect_task(msg: str):
    """
    Analyzes the user message for keywords and patterns to detect a specific task.
    If a task is detected, it returns the result of the Celery task call (AsyncResult).
    """
    msg = msg.lower()

    # --- Reminder ---
    # Pattern: "remind me in [X] minutes to [MESSAGE]"
    match = re.match(r"remind me in (\d+) minutes? to (.+)", msg)
    if match:
        # Calls the Celery task and returns the result object
        return set_reminder.delay(match.group(2), int(match.group(1)))

    # --- Notes ---
    if msg.startswith("note "):
        return add_note.delay(msg.replace("note ", ""))
    if msg.startswith("show notes"):
        return get_notes.delay()

    # --- Weather ---
    if msg.startswith("weather "):
        city = msg.replace("weather ", "")
        return get_weather.delay(city)

    # --- Web Search ---
    if msg.startswith("search "):
        query = msg.replace("search ", "")
        return web_search.delay(query)

    # --- Email ---
    # Pattern: "email [RECIPIENT] subject:[SUBJECT] body:[BODY]"
    if msg.startswith("email "):
        match = re.match(r"email (.+?) subject:(.+?) body:(.+)", msg)
        if match:
            return send_email.delay(
                match.group(1).strip(),
                match.group(2).strip(),
                match.group(3).strip()
            )

    # --- Calculator ---
    if msg.startswith("calc "):
        expr = msg.replace("calc ", "")
        return calculate.delay(expr)

    # If no task is detected, return None (handled by DialogueManager)
    return None