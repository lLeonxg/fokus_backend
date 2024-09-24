# Backend FOKUS APP
# Melanie y Leo


from flask import Blueprint, Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from bson.json_util import ObjectId
from flask_bcrypt import Bcrypt

from models import mongo, init_db
from config import Config

# Import routes
from routes.user_routes import user_bp
from routes.goal_routes import goal_bp
from routes.task_routes import task_bp

# Initialize app using config file
app = Flask(__name__)
app.config.from_object(Config)

# Bcrypt and JWT initialization
bycrypt = Bcrypt(app)
jwt = JWTManager(app)

# DB inicialization
init_db(app)

# Call routes
app.register_blueprint(user_bp)
app.register_blueprint(goal_bp)
app.register_blueprint(task_bp)

if __name__ == '__main__':
    app.run(debug=True)