import unittest
from my_app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(password='almond')
        self.assertTrue(user.password_hash is not None)

    def test_password_no_getter(self):
        user = User(password='almond')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password='almond')
        self.assertTrue(user.password_verification('almond'))
        self.assertFalse(user.password_verification('pistachio'))

    def test_salt_random(self):
        user = User(password='almond')
        user2 = User(password='almond')
        self.assertTrue(user.password_hash != user2.password_hash)
