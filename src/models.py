from dataclasses import dataclass, field

@dataclass
class GameItem():
    name: str
    description: str
    rank: int
    image_url: str
    genres: list[str] = field(default_factory=list)


@dataclass
class Post():
    topic: str
    hook: str
    cta: str
    caption: str
    page_name: str
    items: list[GameItem]
    

def post_to_dict(post: Post) -> dict:
    return {
        "topic": post.topic,
        "hook": post.hook,
        "caption": post.caption,  # just the description part
        "cta": post.cta,
        "items": [
            {"rank": item.rank, "name": item.name, "description": item.description}
            for item in post.items
        ]
    }