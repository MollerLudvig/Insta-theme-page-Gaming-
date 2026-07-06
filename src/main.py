import os

from IGDB_Fetch import fetch_post_images, get_igdb_token
from config import client_id, client_secret
from html_render import render_slide_images
from post_builder import build_post


def main():
    num_rankings = 5

    post = build_post(num_rankings)

    token = get_igdb_token(client_id, client_secret)
    post = fetch_post_images(post, token)
    render_slide_images(post, "slide_images")


if __name__ == "__main__":
    main()