from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from models import mongo

goal_bp = Blueprint('goals', __name__)

# Endpoint to create a goal
@goal_bp.route('/goals', methods=['POST'])
@jwt_required()
def create_goal():
    data = request.get_json()
    title = data.get('title')
    category = data.get('category')
    finished = data.get('finished', False)  # Default to False
    current_user = get_jwt_identity()

    if not category or not title: 
        return jsonify({"msg": "Missing data"}), 400
    
    result = mongo.db.goals.insert_one({
        "user_id": ObjectId(current_user),
        "category": category,
        "title": title,  
        "finished": finished  
    })
    
    # If the goal was created successfully in the database
    if result.acknowledged:
        return jsonify({"msg": "Goal created successfully"}), 201
    else:
        return jsonify({"msg": "An error occurred. The data was not saved"}), 400

# Endpoint to get all the goals
@goal_bp.route('/goals', methods=['GET'])
@jwt_required()
def get_goals():
    current_user = get_jwt_identity()
    user = str(current_user)
    goals = list(mongo.db.goals.find({"user_id": ObjectId(user)}, {"_id": 0, "user_id": 0}))
    
    if goals:   
        return jsonify({'Goals:': goals}), 200
    else: 
        return jsonify({'msg': 'The user has no goals regitered'}), 404 

# Endpoint to get the information of a goal
@goal_bp.route('/goals/<goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    current_user = get_jwt_identity()
    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id), "user_id": ObjectId(current_user)})

    if goal:
        goal['_id'] = str(goal['_id'])  
        return jsonify(goal), 200
    else:
        return jsonify({"msg": "Goal not found or unauthorized"}), 404

# Endpoint to update a goal
@goal_bp.route('/goals/<goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    category = data.get('category')
    title = data.get('title')  
    finished = data.get('finished')  

    update_data = {}
    if category:
        update_data['category'] = category
    if title:  
        update_data['title'] = title
    if finished is not None:
        update_data['finished'] = finished

    result = mongo.db.goals.update_one(
        {"_id": ObjectId(goal_id), "user_id": ObjectId(current_user)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"msg": "Goal not found or unauthorized"}), 404

    return jsonify({"msg": "Goal updated successfully"}), 200

# Endpoint to delete a goal
@goal_bp.route('/goals/<goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    current_user = get_jwt_identity()
    result = mongo.db.goals.delete_one(
        {"_id": ObjectId(goal_id), "user_id": ObjectId(current_user)}
    )

    if result.deleted_count == 0:
        return jsonify({"msg": "Goal not found or unauthorized"}), 404

    # Delete the related tasks if they exist
    mongo.db.tasks.delete_many({"goal_id": ObjectId(goal_id)})

    return jsonify({"msg": "Goal deleted successfully"}), 200
