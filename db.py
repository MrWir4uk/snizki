import json
import os
from config import DB_FILE

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)
        

def get_user(db, user):
    # Якщо передали int — просто айді
    if isinstance(user, int):
        uid = str(user)
        username = None
        first_name = None
    else:
        uid = str(user.id)
        username = user.username
        first_name = user.first_name

    # Визначаємо ім’я користувача
    if username:
        name = f"@{username}"
    elif first_name:
        name = first_name
    else:
        name = uid  # fallback

    # Якщо юзера немає в БД
    if uid not in db:
        db[uid] = {
            "balance": 0,
            "cooldown": 0,
            "game": None,
            "username": name
        }
    else:
        # Оновлюємо username якщо вхідні дані мають новий
        db[uid]["username"] = name

    return db[uid]


