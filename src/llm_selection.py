import requests
import json

from models import GameItem, Post
from prompts import TOPIC_SYSTEM_PROMPT, RANKING_SYSTEM_PROMPT, DESCRIPTION_SYSTEM_PROMPT, CAPTION_SYSTEM_PROMPT, HOOK_SYSTEM_PROMPT


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


def build_hook_prompt(topic: str) -> str:
    return f"Topic: {topic}\n\nWrite a hook for this carousel post."

def llm_generate_hook(topic) ->str:
    data_str = build_hook_prompt(topic)
    return prompt_model(data_str, HOOK_SYSTEM_PROMPT)


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
"You MUST generate exactly {num_missing} games, no more, no less"
Games already placed:
{existing_str}

Previously used topics and games (avoid reusing the same games repeatedly):
{previous_str}

Generate {num_missing} game(s) for the remaining ranks."""

def llm_generate_ranking(topic: str, existing_games: list, num_missing: int) -> str:
    data_str = build_ranking_prompt(topic, existing_games, num_missing)

    raw_output = prompt_model(data_str, RANKING_SYSTEM_PROMPT)
    return raw_to_JSON(raw_output)

    # # Retry logic if the LLM generates an unfinished list. 
    # # Should be solved with better prompting but just in case it is needed
    # if len(result) < num_missing:
    #         print(f"LLM only generated {len(result)} games, expected {num_missing}. Retrying...")
    #         raw_output = prompt_model(data_str, RANKING_SYSTEM_PROMPT)
    #         result = raw_to_JSON(raw_output)


def build_description_prompt(topic: str, items: list) -> str:
    games_str = "\n".join([f"Rank {item['rank']}: {item['name']}" for item in items])
    return f"Topic: {topic}\n\nGames to describe (worst to best):\n{games_str}\n\nWrite a description for each game."

def llm_generate_description(topic: str, items: list) -> list:
    data_str = build_description_prompt(topic, items)
    raw_output = prompt_model(data_str, DESCRIPTION_SYSTEM_PROMPT)
    return raw_to_JSON(raw_output)

def build_caption_prompt(topic: str, items: list) -> str:
    games_str = "\n".join([f"#{item['rank']}: {item['name']}" for item in items])
    return f"Topic: {topic}\n\nGames in the post:\n{games_str}\n\nWrite the caption lines."

def llm_generate_caption(topic: str, items: list) -> str:
    data_str = build_caption_prompt(topic, items)
    raw_output = prompt_model(data_str, CAPTION_SYSTEM_PROMPT)
    result = raw_to_JSON(raw_output)
    return f"{result['criteria']}\n\n{result['flavor']}"


if __name__ == "__main__":  
    None

    