from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from models import mongo

task_bp = Blueprint('task_bps', __name__)

# Endpoint to create a task
@task_bp.route('/goals/<goal_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(goal_id):
    data = request.get_json()
    task_name = data.get('name')
    current_user = get_jwt_identity()

    if not task_name:
        return jsonify({"msg": "Task name is required"}), 400

    # Check if the goal belongs to the user
    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id), "user_id": ObjectId(current_user)})

    if not goal:
        return jsonify({"msg": "Goal not found or unauthorized"}), 404


    result = mongo.db.tasks.insert_one({
        "name": task_name,
        "status": False,  # Default status for a new task
        "goal_id": ObjectId(goal_id)  # Link the task to the goal
    })  # Save the task
    
    if result.acknowledged:
        return jsonify({"msg": "Task created successfully"}), 201
    else:
        return jsonify({"msg": "An error occurred. The data was not saved"})

# Endpoint to get all the tasks
@task_bp.route('/goals/<goal_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(goal_id):
    current_user = get_jwt_identity()
    
    # Check if the goal belongs to the user
    goal = mongo.db.goals.find_one({"_id": ObjectId(goal_id), "user_id": ObjectId(current_user)})
    tasks = list(mongo.db.tasks.find({"goal_id": ObjectId(goal_id)}, {"_id": 0, "goal_id": 0}))
    
    if not goal:
        return jsonify({"msg": "Goal not found or unauthorized"}), 404
    
    if tasks:
        return jsonify(tasks), 200
    else:
        return jsonify({'msg': 'The goal has no tasks regitered'}), 404

# Endpoint to update a task
@task_bp.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    task_name = data.get('name')
    status = data.get('status')

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    # Check if the associated goal belongs to the user
    goal = mongo.db.goals.find_one({"_id": task['goal_id'], "user_id": ObjectId(current_user)})
    
    if not goal:
        return jsonify({"msg": "Unauthorized access to this task"}), 403

    update_data = {}
    if task_name is not None:
        update_data['name'] = task_name
    if status is not None:
        update_data['status'] = status

    mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})

    return jsonify({"msg": "Task updated successfully"}), 200

# Endpoint to delete a task
@task_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    # Check if the associated goal belongs to the user
    goal = mongo.db.goals.find_one({"_id": task['goal_id'], "user_id": ObjectId(current_user)})
    
    if not goal:
        return jsonify({"msg": "Unauthorized access to this task"}), 403

    mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})  # Remove the task

    return jsonify({"msg": "Task deleted successfully"}), 200

