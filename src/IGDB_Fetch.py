from dotenv import load_dotenv
import os
import requests
from models import GameItem, Post
from config import client_id, client_secret
import re


TWITCH_URL = "https://id.twitch.tv/oauth2/token"
IGDB_URL = "https://api.igdb.com/v4/games"


def get_igdb_token(client_id, client_secret):
    response = requests.post(
        TWITCH_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
    response.raise_for_status()
    return response.json().get("access_token")

def igdb_request(endpoint, token, params=None):
    response = requests.post(
        endpoint,
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {token}",
        },
        data=params
    )
    response.raise_for_status()
    return response.json()

def get_cover_url(raw_url: str) -> str:
    url = raw_url.replace("t_thumb", "t_1080p")  # Replace the thumbnail size with a larger size
    if url.startswith("//"):
        url = "https:" + url  # IGDB omits the protocol, requests needs it
    return url

def clean_game_name(name: str) -> str:
    # remove trailing year in parentheses
    name = re.sub(r'\s*\(\d{4}\)\s*$', '', name)
    # remove DLC/edition suffixes after common separators
    name = re.sub(r'\s*[-–]\s*([\w\s]*(DLC|Edition|Pack|Expansion|Season Pass)[\w\s]*)', '', name, flags=re.IGNORECASE)
    return name.strip()

# Find the best match for a game name from a list of IGDB results
def best_match(game_name:str, results: list) -> dict:
    cleaned = game_name.lower().strip()
    
    def score(result):
        result_name = result["name"].lower().strip()

        cleaned_stripped = re.sub(r'[^\w\s]', '', cleaned)
        result_stripped = re.sub(r'[^\w\s]', '', result_name)

        if result_stripped == cleaned_stripped:
            return (3, result.get("rating_count", 0) or 0)  # exact match ignoring punctuation
        if result_stripped.startswith(cleaned_stripped) or cleaned_stripped.startswith(result_stripped):
            return (2, result.get("rating_count", 0) or 0)
        if cleaned_stripped in result_stripped or result_stripped in cleaned_stripped:
            return (1, result.get("rating_count", 0) or 0)
        return (0, result.get("rating_count", 0) or 0)

    
    return max(results, key=score)

def is_base_game(result: dict) -> bool:
    name = result["name"].lower()
    edition_keywords = ["deluxe", "complete", "definitive", "goty", "enhanced", "edition", "remastered"]
    return not any(keyword in name for keyword in edition_keywords)

def fetch_game(game_name: str, token: str) -> GameItem:
    cleaned_name = clean_game_name(game_name)

    # Try to search for exact game name
    result = igdb_request(
        IGDB_URL,
        token,
        f'fields name,genres.name,cover.url,rating, rating_count; where name ~ "{cleaned_name}"; limit 5;'
    )

    if not result:
        # If no exact match, try a broader search
        result = igdb_request(
            IGDB_URL,
            token,
            f'search "{cleaned_name}"; fields name,genres.name,cover.url,rating,rating_count; limit 10;'
        )
    
    if not result:
        raise ValueError(f"No IGDB results found for: {cleaned_name}")
    
    filtered = [r for r in result if is_base_game(r)]
    if not filtered:
        filtered = result
    game = best_match(cleaned_name, filtered)

    cover_url = get_cover_url(game["cover"]["url"]) if game.get("cover") else ""
    genres = [genre["name"] for genre in game.get("genres", [])]
    
    return game["name"], cover_url, genres

def fetch_post_images(post: Post, token: str) -> Post:
    for item in post.items:
        item.name, item.image_url, item.genres = fetch_game(item.name, token)
    return post


if __name__ == "__main__":
    game = fetch_game("the witcher 3: wild hunt", get_igdb_token(client_id, client_secret))
    print(game)
    