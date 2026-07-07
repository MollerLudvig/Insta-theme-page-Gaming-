import json

EMPTY_CONTENT = {
  "topic": "",
  "hook": "",
  "items": [
    {"rank": 5, "name": "", "description": ""},
    {"rank": 4, "name": "", "description": ""},
    {"rank": 3, "name": "", "description": ""},
    {"rank": 2, "name": "", "description": ""},
    {"rank": 1, "name": "", "description": ""}
  ]
}

def update_previous_ideas(topic: str, hook: str, items: list):
    with open("previous_ideas.json", "r") as f:
        history = json.load(f)
    
    history.insert(0, {
        "topic": topic,
        "hook": hook,
        "games": [item.name for item in items]
    })
    
    with open("previous_ideas.json", "w") as f:
        json.dump(history, f, indent=2)


def clear_content_file():
    with open("content.json", "w") as f:
        json.dump(EMPTY_CONTENT, f, indent=2)