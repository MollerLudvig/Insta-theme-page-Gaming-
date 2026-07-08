import json
import os
import random

from models import Post, GameItem
from llm_selection import llm_generate_topic, llm_generate_ranking, llm_generate_description, llm_generate_hook
from hooks import HOOKS

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
        caption="",  # generated separately or written manually later
        items=items
    )


def build_post(num_rankings: int = 5) -> Post:
    with open("content.json", "r") as file:
        post_json = json.load(file)

    if not post_json.get("topic"):
        post_json["topic"] = llm_generate_topic()

    # Use from a pool of pre-made hooks
    if not post_json.get("hook"):
        post_json["hook"] = random.choice(HOOKS)

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


    descriptions = llm_generate_description(post_json["topic"], post_json["items"])
    for item in post_json["items"]:
        matching = next((d for d in descriptions if d["name"] == item["name"]), None)
        if matching:
            item["description"] = matching["description"]

    return create_post_object(post_json)

if __name__ == "__main__":
    post = build_post()
    print(post)