import os
import unittest

from my_app.models import *
from my_app import create_app, db


flask_app = create_app('default')


@flask_app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
