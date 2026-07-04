import requests
import json

from models import GameItem, Post

SYSTEM_PROMPT = """You are a gaming expert creating Instagram carousel post ideas about video games.

You will be given a list of previously used post ideas and must NOT repeat them. Generate a fresh idea in a similar style.

Post format: a ranked list of 5 games around a specific theme or category.

Good topic examples:
- "Top 5 Most Underrated Games of All Time"
- "Top 5 Open World Games"
- "Top 5 Games with the Most Memorable Soundtracks"
- "Top 5 Games Better Than Their Movie Adaptations"
- "Top 5 Games with the Most Innovative Mechanics"
- "Top 5 Perfect Co-op Games"
- "The Evolution of [Game Franchise]"

What makes a good topic:
- Specific enough to be interesting, broad enough to find 5 strong games
- Debatable — people should want to argue about the list in comments
- Timeless — not dependent on recent news or releases

Descriptions should be 1-2 sentences max, written for people who already know games well.
Avoid generic praise ("great graphics", "fun gameplay") — focus on what specifically makes each game stand out for THIS topic.

Rank from worst to best (rank 1 = best).

Rules for listing games:
- Include numbers and subtitles that are part of the official title: 
"Resident Evil 3" not "Resident Evil", "Dark Souls III" is fine
- List ONLY the game title, no character names, subtitles, or descriptions in the name field
- Example: "God of War" not "God of War: Kratos vs Zeus" 
- Example: "Silent Hill 2" not "Silent Hill 2: Pyramid Head"
- List ONLY real, released video games. No movies, books, or fictional games
- Each rank must have exactly ONE game. Never list two games at the same rank
- Do NOT include release years in the name field. "God of War" not "God of War (2018)"
- List ONLY base games, never DLC, expansions, or editions. 
"Fallout: New Vegas" not "Fallout: New Vegas - Lonesome Road DLC"
- List specific game titles only, never a series or franchise. 
"Mass Effect" not "Mass Effect Series", "Dark Souls" not "Souls Series"

Respond with ONLY valid JSON, no explanation, no markdown, no code fences:
{
  "topic": "Top 5 ...",
  "items": [
    {"rank": 5, "name": "Game Name", "description": "Why it belongs here."},
    {"rank": 4, "name": "Game Name", "description": "Why it belongs here."},
    {"rank": 3, "name": "Game Name", "description": "Why it belongs here."},
    {"rank": 2, "name": "Game Name", "description": "Why it belongs here."},
    {"rank": 1, "name": "Game Name", "description": "Why it belongs here."}
  ]
}
"""

def build_selection_prompt() -> str:
    with open("used_ideas.md", "r") as file:
        previous_posts = file.read()
    return f"Generate a new idea for an instagram carousel post about video games,\
            avoiding these previous ideas:\n{previous_posts}"

def parse_llm_output(data: dict) -> Post:
    items = [
        GameItem(
            rank=item["rank"],
            name=item["name"],
            description=item["description"],
            image_url=""
        )
        for item in data["items"]
    ]

    items.sort(key=lambda x: x.rank, reverse=True) # In case the LLM gives rankings in wrong order for some reason.
    return Post(
        topic=data["topic"],
        caption="",  # generated separately or written manually later
        items=items
    )

def llm_select() -> dict:
    data_str = build_selection_prompt()

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:14b",
        "system": SYSTEM_PROMPT,
        "prompt": data_str,
        "stream": False,
        "options": {"num_ctx": 4096, "temperature": 0.75}
    })

    response.raise_for_status()

    raw_output = response.json()["response"]
    try:
        data = json.loads(raw_output)
        
        # Debug print to see what the LLM returned
        for item in data["items"]:
            print (item["name"])
            
        return parse_llm_output(data)
    except json.JSONDecodeError:
        print("LLM did not return valid JSON. Raw output:")
        print(raw_output)
        raise


if __name__ == "__main__":  
    selection = llm_select()
    print(selection)

    