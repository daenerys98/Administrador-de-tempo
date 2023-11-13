from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask.cli import FlaskGroup
from admin import app, db

# Configuração do Flask-Migrate
migrate = Migrate(app, db)
cli = FlaskGroup(app)

# Adiciona os comandos de migração ao Flask-CLI
cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    cli()
