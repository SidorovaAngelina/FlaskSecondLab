import unittest
from my_app.models import User, Permission, AnonymousUser, Role, db


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(gender='female')
        user.set_password('almond')
        self.assertTrue(user.password_hash is not None)

    def test_password_no_getter(self):
        user = User()
        user.set_password('almond')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(email='test@sample.com')
        user.set_password('almond')
        self.assertTrue(user.password_verification('almond'))
        self.assertFalse(user.password_verification('pistachio'))

    def test_salt_random(self):
        user = User(gender='male')
        user.set_password('almond')
        db.session.add(user)
        user2 = User(gender='female')
        user2.set_password('almond')
        db.session.add(user2)
        self.assertTrue(user.password_hash != user2.password_hash)

    def test_user_role(self):
        Role.insert_roles()
        user = User(email='test@sample.com', gender='male')
        user.set_password('nut')
        db.session.add(user)
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_anonim(self):
        Role.insert_roles()
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))
