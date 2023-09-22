from dataclasses import dataclass


@dataclass(kw_only=True)
class User:
    name: str
    email: str
