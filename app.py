import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, login_manager
from models import User
from auth.auth import auth_bp
from controllers.user import user_bp
from controllers.admin import admin_bp
from controllers.api import api_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img/products'

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)