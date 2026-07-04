import os

from llm_selection import llm_select
from IGDB_Fetch import fetch_post_images, get_igdb_token
from config import client_id, client_secret
from html_render import render_slide_images


def main():
    post = llm_select()
    token = get_igdb_token(client_id, client_secret)
    post = fetch_post_images(post, token)
    render_slide_images(post, "slide_images")


if __name__ == "__main__":
    main()