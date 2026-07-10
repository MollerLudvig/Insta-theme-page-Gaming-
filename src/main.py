import os

from IGDB_Fetch import fetch_post_images, get_igdb_token
from config import client_id, client_secret
from html_render import render_slide_images
from post_builder import build_post
from content_history import update_previous_ideas, clear_content_file


def main():
    num_rankings = 5

    post = build_post(num_rankings)

    print(post.caption)

    token = get_igdb_token(client_id, client_secret)
    post = fetch_post_images(post, token)
    render_slide_images(post, "slide_images")


    response = input("Post this idea or not?: ")
    if response.lower() == "yes":
        update_previous_ideas(post.topic, post.hook, post.items)
        clear_content_file()



if __name__ == "__main__":
    main()