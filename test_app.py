import unittest
import json
from App import app, tasks_collection

class TestTaskAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.base_url = "/api/tasks"
        # Clear the database before each test
        tasks_collection.delete_many({})

    def test_add_task(self):
        response = self.client.post(self.base_url, json={"title": "Test Task", "description": "Test Description"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)
        self.assertEqual(response.json["message"], "Task added successfully")

    def test_add_task_without_title(self):
        response = self.client.post(self.base_url, json={"description": "No Title"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Task title is required")

    def test_get_tasks(self):
        # Add a task first
        self.client.post(self.base_url, json={"title": "Test Task", "description": "Test Description"})
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["title"], "Test Task")

    def test_edit_task(self):
        # Add a task first
        add_response = self.client.post(self.base_url, json={"title": "Old Title", "description": "Old Description"})
        task_id = add_response.json["id"]
        # Edit the task
        response = self.client.put(f"{self.base_url}/{task_id}", json={"title": "New Title"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Task updated successfully")


    def test_delete_task(self):
        add_response = self.client.post(self.base_url, json={"title": "Test Task"})
        task_id = add_response.json["id"]
        # Delete the task
        response = self.client.delete(f"{self.base_url}/{task_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Task deleted successfully")

    def test_delete_all_tasks(self):
        # Add multiple tasks
        self.client.post(self.base_url, json={"title": "Task 1"})
        self.client.post(self.base_url, json={"title": "Task 2"})
        # Delete all tasks
        response = self.client.delete(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "All tasks deleted successfully")
        # Verify no tasks remain
        get_response = self.client.get(self.base_url)
        self.assertEqual(len(get_response.json), 0)

if __name__ == "__main__":
    unittest.main()
