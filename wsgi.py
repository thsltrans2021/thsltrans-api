import os
from app import app

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

if __name__ == '__main__':
    app.run()
