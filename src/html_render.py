import asyncio
from playwright.async_api import async_playwright
import json
import random

from models import Post

def get_rank_colors(rank: int) -> dict:
    colors = {
        1: {"highlight": "#FFF176", "base": "#FFD700", "shadow": "#B8860B", "glow": "rgba(255,215,0,0.8)"},
        2: {"highlight": "#FFFFFF", "base": "#E8E8E8FF", "shadow": "#909090", "glow": "rgba(192,192,192,0.8)"},
        3: {"highlight": "#FFD4A0", "base": "#CD7F32", "shadow": "#8B4513", "glow": "rgba(205,127,50,0.95)"},
    }
    return colors.get(rank, {"highlight": "#FFFFFF", "base": "#6AAEE8", "shadow": "#1A5EA8", "glow": "rgba(74,144,217,0.6)"})

async def screenshot_card(html_content, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1350})
        await page.set_content(html_content)
        await page.wait_for_timeout(300)  # let webfonts load
        card = page.locator(".slide")
        await card.screenshot(path=output_path)
        await browser.close()


def render_content_slide_html(image_url, rank, game_title, description):
    with open("html_templates/content_slide_template.html", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__IMAGE_URL__", image_url)
    html = html.replace("__RANK__", rank)
    html = html.replace("__GAME_TITLE__", game_title)
    html = html.replace("__DESCRIPTION__", description)
    
    rank_colors = get_rank_colors(int(rank))
    html = html.replace("__RANK_HIGHLIGHT__", rank_colors["highlight"])
    html = html.replace("__RANK_COLOR__", rank_colors["base"])
    html = html.replace("__RANK_SHADOW__", rank_colors["shadow"])
    html = html.replace("__RANK_GLOW__", rank_colors["glow"])
    return html


def render_topic_slide_html(topic, hook, image_url):
    with open("html_templates/topic_slide_template.html", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__TOPIC__", topic)
    html = html.replace("__HOOK__", hook)
    html = html.replace("__IMAGE_URL__", image_url)
    return html

def render_last_slide_html(topic, cta, winner):
    with open("html_templates/final_slide_template.html", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__TOPIC__", topic)
    html = html.replace("__CTA__", cta)
    html = html.replace("__WINNER__", winner)
    return html

def render_slide_images(post: Post, output_path):

    # Choose random background out of the rankings for topic slide
    topic_html = render_topic_slide_html(post.topic, post.hook, random.choice(post.items).image_url)
    asyncio.run(screenshot_card(topic_html, f"{output_path}/slide_0.png"))
    print(f"Rendered topic slide for {post.topic} to {output_path}")

    for i, item in enumerate(post.items):
        html_content = render_content_slide_html(
            item.image_url, 
            str(item.rank), 
            item.name, 
            item.description
            )
        
        asyncio.run(screenshot_card(html_content, f"{output_path}/slide_{i+1}.png"))
        print(f"Rendered slide {i+1} for {item.name} to {output_path}")

    # Rankings in post object already sorted so [-1] will give the winner
    last_slide_html = render_last_slide_html(post.topic, post.cta, post.items[-1].name)
    asyncio.run(screenshot_card(last_slide_html, f"{output_path}/slide_final.png"))

