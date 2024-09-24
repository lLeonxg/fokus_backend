#
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId
from models import mongo

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()

# Endpoint to register a user
@user_bp.route('/register', methods=['POST'])
def register():
    # Requested data
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    # If a field is missing
    if not all([name, email, password]):
        return jsonify({"msg": "Missing information"}), 400
    
    # If the email was already registered
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"msg": "Email already exists"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    result = mongo.db.users.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })
    
    # If the user was registered successfully in the database    
    if result.acknowledged:
        return jsonify({"msg": "User registered successfully"}), 201
    else:
        return jsonify({"msg": "An error occurred. The data was not saved"}), 400

# Endpoint to login
@user_bp.route('/login', methods=['POST'])
def login():
    # Requsted data
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({"email": email})
    
    # If the input was correct
    if user and bcrypt.check_password_hash(user['password'], password):
        token = create_access_token(identity=str(user['_id']))
        return jsonify({"token": token}), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
    
# Endpoint to get the user data (protected)
@user_bp.route('/userdata', methods=['GET'])
@jwt_required()
def userdata():
    current_user = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(current_user)})
    
    return jsonify({
        "name": user['name'],
        "email": user['email']
    }), 200
