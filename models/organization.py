class Organization:
    '''
    Represents an organization
    '''

    def __init__(self, login, avatar) -> None:
        self.login = login
        self.avatar = avatar

    def __str__(self) -> str:
        return {self.login}
