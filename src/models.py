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
    items: list[GameItem]