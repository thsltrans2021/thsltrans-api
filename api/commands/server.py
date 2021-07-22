# https://flask.palletsprojects.com/en/2.0.x/cli/
import click
from flask import Flask
from flask.cli import with_appcontext


def register_commands(app: Flask):
    app.cli.add_command(test_command)


@click.command('test-cmd')
@with_appcontext
def test_command():
    print("Something")

# use `flask routes` to list all routes of the application
