import os

from flask_script import Manager

from app import app

manager = Manager(app)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)