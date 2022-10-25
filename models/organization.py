class Organization:
    """
    Represents a GitHub Organization.
    """

    def __init__(self, login: str, avatar_url: str) -> None:
        self.login = login
        self.avatar_url = avatar_url

    def __str__(self) -> str:
        return self.login
