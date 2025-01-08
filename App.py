from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

uri = "mongodb+srv://ayushbillade11:ay123%40%24AB@cluster0.s8pk0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["todo_db"]
tasks_collection = db["tasks"]

# Ping MongoDB
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data or not data.get("title"):
        return jsonify({"error": "Task title is required"}), 400
    task = {"title": data["title"], "description": data.get("description", ""), "completed": False}
    task_id = tasks_collection.insert_one(task).inserted_id
    return jsonify({"id": str(task_id), "message": "Task added successfully"}), 201

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    for task in tasks_collection.find():
        tasks.append({
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "completed": task["completed"]
        })
    return jsonify(tasks), 200

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    updated_task = {}
    if "title" in data:
        updated_task["title"] = data["title"]
    if "description" in data:
        updated_task["description"] = data["description"]
    if "completed" in data:
        updated_task["completed"] = data["completed"]
    result = tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": updated_task})
    if result.matched_count == 0:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted successfully"}), 200

@app.route('/api/tasks', methods=['DELETE'])
def delete_all_tasks():
    tasks_collection.delete_many({})
    return jsonify({"message": "All tasks deleted successfully"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Default to 5000 locally, use Netlify's port in production
    app.run(host="0.0.0.0", port=port)
