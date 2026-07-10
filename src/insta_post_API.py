from instagrapi import Client
from instagrapi.types import StoryHashtag
import os


def upload_carousel(slide_paths: list[str], caption: str):
    cl = Client()
    cl.login(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))
    
    media = cl.album_upload(
        paths=slide_paths,
        caption=caption,
        extra_data={
            "original_width": 1080,
            "original_height": 1350,
        }
    )
    
    print(f"Posted successfully: https://www.instagram.com/p/{media.code}/")
    return media