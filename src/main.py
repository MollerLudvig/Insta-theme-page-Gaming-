import os
import json
import webbrowser
import pyperclip

from IGDB_Fetch import fetch_post_images, get_igdb_token
from config import client_id, client_secret
from html_render import render_slide_images
from post_builder import build_post
from content_history import update_previous_ideas, clear_content_file
from models import post_to_dict
from insta_post_API import upload_carousel


def main():
    num_rankings = 5
    slides_folder = "slide_images"
    slide_paths = [
        os.path.join(slides_folder, "slide_0.png"),  # topic slide
        os.path.join(slides_folder, "slide_1.png"),
        os.path.join(slides_folder, "slide_2.png"),
        os.path.join(slides_folder, "slide_3.png"),
        os.path.join(slides_folder, "slide_4.png"),
        os.path.join(slides_folder, "slide_5.png"),  # final slide
        os.path.join(slides_folder, "slide_final.png"),
    ]

    post = build_post()

    # write current state to content.json for review
    with open("content.json", "w") as f:
        json.dump(post_to_dict(post), f, indent=2)

    print("\nReview content.json and make any changes.")
    print("Leave description empty for any game you want re-described.")
    input("Press enter when ready to continue...\n")

    # rebuild from potentially edited content.json
    post = build_post()
    with open("content.json", "w") as f:
        json.dump(post_to_dict(post), f, indent=2)

    pyperclip.copy(post.caption)

    token = get_igdb_token(client_id, client_secret)
    post = fetch_post_images(post, token)
    render_slide_images(post, "slide_images")


    response = input("Post this idea or not?: ")
    if response.lower() == "y":
        # media = upload_carousel(slide_paths, post.caption)
        # webbrowser.open(f"https://www.instagram.com/p/{media.code}/")

        update_previous_ideas(post.topic, post.hook, post.items)
        clear_content_file()



if __name__ == "__main__":
    main()