import unittest
import os

from gitapply import user


class UsersTest(unittest.TestCase):
    def test_users_from_file(self):
        users = user.Users.from_file(path=os.path.join(os.path.dirname(__file__), 'users'))
        self.assertTrue(users.has_user('user1'), 'user1 should exists')
        self.assertTrue(users.has_user('user2'), 'user2 should exists')
        self.assertTrue(users.has_user('user3'), 'user3 should exists')

    def test_user_password_check(self):
        users = user.Users.from_file(path=os.path.join(os.path.dirname(__file__), 'users'))
        try:
            users.check('user2', 'xxx')
        except Exception as ex:
            self.assertIsInstance(ex, user.UserNotEnabledException)

        try:
            users.check('user1', '1234')
        except Exception as ex:
            self.assertIsInstance(ex, user.UserPasswordIncorrectException)

        users.check('user1', '123456')
        users.check('user3', 'xxxxxx')

        try:
            users.check('user4', 'xxx')
        except Exception as ex:
            self.assertIsInstance(ex, user.UserNotFoundException)