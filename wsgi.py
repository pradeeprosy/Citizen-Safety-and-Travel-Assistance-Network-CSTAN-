"""
WSGI entrypoint for CSTAN production deployment.
Compatible with Gunicorn, Waitress, uWSGI, Render, Railway, AWS, Heroku.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
