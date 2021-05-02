class UserNotFoundException(Exception):
    pass


class UserPasswordIncorrectException(Exception):
    pass


class UserNotEnabledException(Exception):
    pass


class User:
    def __init__(self, username, password, enabled):
        self.username = username
        self.password = password
        self.enabled = enabled


class Users:
    def __init__(self, users_text=''):
        self.users = {}
        for user in users_text.split('\n'):
            if user and user.strip():
                username, password, enabled = user.split(':')
                if enabled == '0':
                    enabled = False
                self.users[username] = User(username, password, bool(enabled))

    @staticmethod
    def from_file(path):
        with open(path, 'rt') as f:
            return Users(f.read())

    def has_user(self, username):
        return username in self.users

    def check(self, username, password):
        if not self.has_user(username):
            raise UserNotFoundException('no such user: %s' % username)

        if not self.users[username].enabled:
            raise UserNotEnabledException('user %s not enabled' % username)

        if self.users[username].password != password:
            raise UserPasswordIncorrectException('incorrect password')


