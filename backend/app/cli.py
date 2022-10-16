import os
import click


def register(app):
    @app.cli.command()
    @click.option('--test_patern', default='test*.py',
                  help='Patern to use for finding test cases.')
    @click.option('--verbosity', default=2, help='Verbosity level.', type=int)
    def test(test_patern, verbosity):
        import unittest
        tests = unittest.TestLoader().discover('tests', test_patern)
        unittest.TextTestRunner(verbosity=verbosity).run(tests)