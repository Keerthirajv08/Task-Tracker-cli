'''class Task:
    def __init__(self, name, task_id):
        self.name = name
        self.task_id = task_id '''

class TaskTracker:
    def __init__(self, name, task_id):
        self.tasks = []
        self.name = name
        self.task_id = task_id



    def add_task(self, task):
        self.tasks.append(task)

    def delete_task(self, task):
        self.tasks.remove(task)

    def get_tasks(self):
        return self.tasks
    