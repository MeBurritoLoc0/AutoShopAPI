from app import create_app
from app.extensions import db   # import the db object

app = create_app("DevelopmentConfig")

# create tables if they don't exist yet
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
