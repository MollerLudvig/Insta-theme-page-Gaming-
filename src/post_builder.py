import json
import os
import random

from models import Post, GameItem
from llm_selection import llm_generate_topic, llm_generate_ranking, llm_generate_description, llm_generate_hook, llm_generate_caption
from engagement_phrases import HOOKS, CTAS

def create_post_object(data: dict) -> Post:
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
        hook=data["hook"],
        cta=data["cta"],
        caption=data["caption"],
        page_name=os.getenv("INSTAGRAM_USERNAME"),
        items=items
    )


HASHTAGS = "#gaming #gamer #top5games #gamingcommunity #pcgaming #consolegaming #gamerecommendations"

def build_full_caption(topic: str, llm_caption: str, cta: str) -> str:
    return f"MY {topic} 🎮\n\n{llm_caption}\n\n{cta} 👇\n\n{HASHTAGS}"


def build_post(num_rankings: int = 5) -> Post:
    with open("content.json", "r") as file:
        post_json = json.load(file)

    if not post_json.get("topic"):
        post_json["topic"] = llm_generate_topic()

    # Use from a pool of pre-made hooks
    if not post_json.get("hook"):
        post_json["hook"] = random.choice(HOOKS)

    if not post_json.get("cta"):
        post_json["cta"] = random.choice(CTAS)


    # LLM generates hook
    # if not post_json.get("hook"):
    #     post_json["hook"] = llm_generate_hook(post_json["topic"])
    #     print(post_json["hook"])

    existing_games = [item for item in post_json["items"] if item.get("name")]
    if len(existing_games) < num_rankings:
        new_games = llm_generate_ranking(post_json["topic"], existing_games, num_rankings - len(existing_games))
        for game in new_games:
            game["description"] = ""
        all_games = existing_games + new_games
        post_json["items"] = sorted(all_games, key=lambda x: x["rank"], reverse=True)


    # Could generate only for the empty description fieldsWhile still feeding the existing description
    # Fields for context so the LLM doesn't repeat itself across multiple descriptions
    descriptions = llm_generate_description(post_json["topic"], post_json["items"])
    for item in post_json["items"]:
        matching = next((d for d in descriptions if d["name"].lower() == item["name"].lower()), None)
        if matching and not item["description"]:
            item["description"] = matching["description"]


    if not post_json.get("caption"):
        post_json["caption"] = llm_generate_caption(post_json["topic"], post_json["items"])
        post_json["caption"] = build_full_caption(post_json["topic"], post_json["caption"], post_json["cta"])

    return create_post_object(post_json)

if __name__ == "__main__":
    post = build_post()
    print(post)