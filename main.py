from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
import csv
import os
from datetime import datetime

# ------------- CONFIG -------------
CSV_FILE = "scores.csv"       # results land here
QUESTIONS = [
    {"q": "What is the capital of France?", "a": "paris"},
    {"q": "What is 5 + 7?", "a": "12"},
    {"q": "What planet is known as the Red Planet?", "a": "mars"},
    {"q": "Who wrote 'Hamlet'?", "a": "shakespeare"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is the largest ocean?", "a": "pacific"},
    {"q": "In which year did WW2 end?", "a": "1945"},
    {"q": "Which gas do plants breathe in?", "a": "carbon dioxide"},
    {"q": "What is the square root of 81?", "a": "9"},
    {"q": "What is H2O?", "a": "water"},
]
# ----------------------------------

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# in‑memory state per room
rooms: dict[str, dict] = {}


@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    await websocket.accept()

    # build room structure if first user
    if room not in rooms:
        rooms[room] = {"users": {}, "current_q": 0}

    room_users = rooms[room]["users"]
    room_users[username] = {"ws": websocket, "score": 0}

    await broadcast(room, f"{username} joined the game.")
    await send_question(room)

    try:
        while True:
            msg = await websocket.receive_text()
            await handle_answer(room, username, msg.strip().lower())
    except WebSocketDisconnect:
        room_users.pop(username, None)
        await broadcast(room, f"{username} left the game.")


async def handle_answer(room: str, username: str, message: str):
    room_data = rooms[room]
    idx = room_data["current_q"] - 1  # index of current asked question
    if idx >= len(QUESTIONS):          # no active question
        return

    correct = QUESTIONS[idx]["a"]
    if message == correct:
        room_data["users"][username]["score"] += 1
        await broadcast(room, f"✅ {username} got it right! (+1)")
        await send_scoreboard(room)
        await send_question(room)
    else:
        await room_data["users"][username]["ws"].send_text("❌ Wrong answer. Try again!")


async def send_question(room: str):
    room_data = rooms[room]
    if room_data["current_q"] >= len(QUESTIONS):
        await broadcast(room, "🎉 Game Over!")
        await send_scoreboard(room)
        save_scores(room)        #  <-- persist to CSV
        return

    q = QUESTIONS[room_data["current_q"]]["q"]
    await broadcast(room, f"❓ Question {room_data['current_q'] + 1}: {q}")
    room_data["current_q"] += 1


async def send_scoreboard(room: str):
    scores = rooms[room]["users"]
    board = "🏆 Scores:\n" + "\n".join(f"{u}: {d['score']}" for u, d in scores.items())
    await broadcast(room, board)


async def broadcast(room: str, message: str):
    for u in rooms[room]["users"].values():
        await u["ws"].send_text(message)


def save_scores(room: str):
    """Append all user scores of given room to CSV_FILE."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["room", "username", "score", "played_at"])
        ts = datetime.utcnow().isoformat(timespec="seconds")
        for username, data in rooms[room]["users"].items():
            writer.writerow([room, username, data["score"], ts])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
