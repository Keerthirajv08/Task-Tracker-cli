#task tracker using python 
import datetime

class taskTracker:
    def __init__(self, description):
        self.tasks = []
        self.task_id = 0
        self.description = description
        self.status = "todo"
        self.createdAt = str(datetime.datetime.now())
        self.updatedAt = str(datetime.datetime.now())

    def add_task(self):
        self.task_id += 1
        task = {
            "id": self.task_id,
            "description": self.description,
            "status": self.status,
            "createdAt": None,
            "updatedAt": None
        }
        self.tasks.append(task)
        task["createdAt"] = str(datetime.datetime.now())
        task["updatedAt"] = str(datetime.datetime.now())
        return self.tasks    

    def update_task(self, target_id):
        for task in self.tasks:
            if task["id"] == target_id:
                task["status"] = "done"
                task["updatedAt"] = str(datetime.datetime.now())
        return self.tasks
    

    def delete_task(self, target_id):
        for task in self.tasks:
            if task["id"] == target_id:
                self.tasks.remove(task)
        return self.tasks
        
        

if __name__ == "__main__":
    task = taskTracker("do some pushups")
    print(task.add_task())
    print(task.update_task(1))

    task = taskTracker("code n blood")
    print(task.add_task())
    print(task.update_task(2))

    '''task = taskTracker("eat healthy food", "todo", None, None)
    print(task.add_task())
    print(task.update_task(3))

    task = taskTracker("do some yoga", "todo", None, None)
    print(task.add_task())
    print(task.update_task(4))
    '''

