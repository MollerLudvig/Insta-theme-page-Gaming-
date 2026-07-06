import requests
import json

from models import GameItem, Post
from prompts import TOPIC_SYSTEM_PROMPT, RANKING_SYSTEM_PROMPT, DESCRIPTION_SYSTEM_PROMPT


def raw_to_JSON(raw_output: str) -> dict:
    try:
        data = json.loads(raw_output)
        return data
    
    except json.JSONDecodeError:
        print("LLM did not return valid JSON. Raw output:")
        print(raw_output)
        raise

def prompt_model(prompt: str, system_prompt: str) -> dict:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:14b",
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 4096, "temperature": 0.75}
    })

    response.raise_for_status()

    raw_output = response.json()["response"]
    return raw_output


def build_topic_prompt() -> str:
    with open("previous_ideas.json", "r") as file:
        previous_posts = json.load(file)
    return f"Generate a new topic for an Instagram gaming carousel post, \
            avoiding these previously used topics:\n{previous_posts}"

def llm_generate_topic() -> str:
    data_str = build_topic_prompt()
    return prompt_model(data_str, TOPIC_SYSTEM_PROMPT)


def build_ranking_prompt(topic: str, existing_games: list, num_missing: int) -> str:
    with open("previous_ideas.json", "r") as file:
        previous_posts = json.load(file)
    
    existing_str = ""
    if existing_games:
        existing_str = "\n".join(
            [f"Rank {g['rank']}: {g['name']}" for g in existing_games if g.get("name")]
        )
    
    previous_str = json.dumps(previous_posts, indent=2) if previous_posts else "None yet."
    
    return f"""Topic: {topic}
Number of games to generate: {num_missing}
Games already placed:
{existing_str}

Previously used topics and games (avoid reusing the same games repeatedly):
{previous_str}

Generate {num_missing} game(s) for the remaining ranks."""

def llm_generate_ranking(topic: str, existing_games: list, num_missing: int) -> str:
    data_str = build_ranking_prompt(topic, existing_games, num_missing)

    raw_output = prompt_model(data_str, RANKING_SYSTEM_PROMPT)
    return raw_to_JSON(raw_output)


def build_description_prompt(game_name: str, topic: str) -> str:
        return f"Game: {game_name}\nTopic: {topic}\n\nWrite a description for why this game belongs on this list."


def llm_generate_description(game_name: str, topic: str) -> str:
    data_str = build_description_prompt(game_name, topic)

    raw_output = prompt_model(data_str, DESCRIPTION_SYSTEM_PROMPT)
    return raw_output



if __name__ == "__main__":  
    None

    