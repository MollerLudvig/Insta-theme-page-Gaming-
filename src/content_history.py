import json

EMPTY_CONTENT = {"topic": "", "items": []}

def update_previous_ideas(topic: str, items: list):
    with open("previous_ideas.json", "r") as f:
        history = json.load(f)
    
    history.insert(0, {
        "topic": topic,
        "games": [item.name for item in items]
    })
    
    with open("previous_ideas.json", "w") as f:
        json.dump(history, f, indent=2)


def clear_content_file():
    with open("content.json", "w") as f:
        json.dump(EMPTY_CONTENT, f, indent=2)