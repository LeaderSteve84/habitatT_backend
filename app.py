#!/usr/bin/env python3
"""module for flask application"""
from app import create_app
from flask_mail import Mail

app = create_app()
app.config.from_object('app.config.Config')
mail = Mail()


if __name__ == "__main__":
    app.run()
