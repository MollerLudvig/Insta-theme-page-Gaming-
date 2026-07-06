import json
import os

from models import Post, GameItem
from llm_selection import llm_generate_topic, llm_generate_ranking, llm_generate_description

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
        caption="",  # generated separately or written manually later
        items=items
    )


def build_post(num_rankings: int = 5) -> Post:
    with open("content.json", "r") as file:
        post_json = json.load(file)

    if not post_json.get("topic"):
        post_json["topic"] = llm_generate_topic()

    existing_games = [item for item in post_json["items"] if item.get("name")]

    if len(existing_games) < num_rankings:
        new_games = llm_generate_ranking(post_json["topic"], existing_games, num_rankings - len(existing_games))
        for game in new_games:
            game["description"] = ""
        all_games = existing_games + new_games
        post_json["items"] = sorted(all_games, key=lambda x: x["rank"], reverse=True)

    for game in post_json["items"]:
        if not game.get("description"):
            game["description"] = llm_generate_description(game["name"], post_json["topic"])

    return create_post_object(post_json)

if __name__ == "__main__":
    post = build_post()
    print(post)