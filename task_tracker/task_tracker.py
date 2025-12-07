#import random
import sys
import os
from datetime import datetime
import json

'''class Task:
    def __init__(self, name, task_id):
        self.name = name
        self.task_id = task_id '''

TASK_FILE = "tasks.json"

STATUS_TODO = "todo"
STATUS_IN_PROGRESS = "in-progress"
STATUS_DONE = "done"


def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    
def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

'''class TaskTracker:
    def __init__(self, task_id, description, status, createdAt, updatedAt):
        self.tasks = load_tasks()
        #self.name = name
        #self.task_id = task_id
        #self.description = description
        #self.status = status
        #self.createdAt = createdAt
        #self.updatedAt = updatedAt
        

    def add_task(self, task):
        self.tasks.append(task)

    def delete_task(self, task):
        self.tasks.remove(task)

    def get_tasks(self):
        return self.tasks
    
    def get_name(self):
        return self.name
    
    def get_task_id(self):
        return self.task_id
    

    def taskId(self, task):
        self.task_id = 0
        for task in self.tasks:
            self.task_id += 1
        return self.task_id'''
    

def add_task(description):
    '''self.tasks.append(task)
    self.task_id = 0
    for task in self.tasks:
        self.task_id += 1
    self.update_task("todo")
    self.createdAt = datetime.datetime.now()
    self.updatedAt = datetime.datetime.now()
    return self.tasks'''
    #GENERATE ID 
    if not description:
        print("Error: Task description cannot be empty.")
        return False
    
    tasks = load_tasks()

    new_id = max([task['id'] for task in tasks], default=0) + 1

    task = {
        'id' : new_id,
        'description': description,
        'status' : STATUS_TODO,
        'createdAt' : datetime.now().isoformat(),
        'updatedAt' : datetime.now().isoformat()
    }

    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID : {new_id})")
    return True

    #else:
        #Logic to find max ID + 1
        #new_id = self.tasks[-1]["id"] + 1
    
    '''new_task = {
        "id": new_id,
        "description": description,
        "status": "todo",
        "createdAt": str(datetime.datetime.now()),
        "updatedAt": str(datetime.datetime.now())
    }
    self.tasks.append(new_task)
    save_tasks(self.tasks)
    print(f"Task added successfully (ID : {new_id})")'''


    '''def update_status(self, status):
        self.status = status
        if self.status == "done":
            self.updatedAt = datetime.datetime.now()
        elif self.status == "in-progess":
            self.updatedAt = datetime.datetime.now()
        elif self.status == "todo":
            self.createdAt = datetime.datetime.now()'''
    
def update_task(task_id, new_description):
    #self.tasks = task_id, description, status, createdAt, updatedAt

    '''for task in self.tasks:
        if task.task_id == target_id:
            task.description = new_description
            task.status = new_status
            task.createdAt = createdAt
            task.updatedAt = new_updatedAt'''
    
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == task_id:
            task['description'] = new_description
            task['updatedAt'] = datetime.now().isoformat()
            
            save_tasks(tasks)
            print(f"Task updated successfully (ID : {task_id})")
            return True
        
    print(f"Task with ID {task_id} not found.")
    return False

def change_status(task_id, new_status, status_filter=None):
    try:
        task_id = int(task_id)
    except ValueError:
        print("Error: Task ID must be an integer.")
        return False

    valid_status = [STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE]

    if new_status not in valid_status:
        print(f"Error: status must be one of: {','.join(valid_status)}")
        return False

    tasks = load_tasks()

    for task in tasks:
        #if task['status'] == status_filter:
        if task['id'] == task_id:
            task['status'] = new_status
            task['updatedAt'] = datetime.now().isoformat()
            save_tasks(tasks)

            status_display = {
                STATUS_TODO: "todo",
                STATUS_IN_PROGRESS: "in-progress",
                STATUS_DONE: "done"
            }

            print(f"Task {task_id} status changed to {status_display[new_status]}")
            return True
    
    print(f"Error: Task with ID {task_id} not found.")
    return False
       

def list_tasks(status_filter=None):
    '''if status_filter is None:
        return self.tasks
    
    filtered_tasks = []
    for task in self.tasks:
        if task.status == status_filter:
            filtered_tasks.append(task)
    return filtered_tasks'''

    tasks = load_tasks()

    if status_filter is not None:
        tasks = [task for task in tasks if task['status'] == status_filter]

    if not tasks:
        filtered_text = f"with status '{status_filter}'" if status_filter else ""
        print(f"No tasks found. {filtered_text}")
        return
    
    print(f"\n{'ID':<5} {'Status':<15} {'Description':<40} {'Created At':<20}")
    print("-" * 85)

    for task in tasks:
        status_display = {
            STATUS_TODO: "TODO",
            STATUS_IN_PROGRESS: "IN-PROGRESS",
            STATUS_DONE: "DONE"
        }[task['status']]

        created_date = datetime.fromisoformat(task['createdAt']).strftime('%Y-%m-%d %H:%M')

        description = (task['description'][:37] + '...') if len(task['description']) > 40 else task['description']

        print(f"{task['id']:<5} {status_display:<15} {description:<40} {created_date:<20}")

    print(f"\n Total: {len(tasks)} task(s)")

def delete_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        print("Error: Task ID must be an integer.")
        return False

    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            save_tasks(tasks)
            print(f"Task deleted successfully (ID : {task_id})")

def show_help():
    """Display help information."""
    help_text = """
Task Tracker CLI - Manage your tasks efficiently

Commands:
    add <description>         Add a new task
    update <id> <description> Update task description
    delete <id>              Delete a task
    start <id>               Mark task as in progress
    done <id>                Mark task as done
    todo <id>                Mark task as to do
    list                     List all tasks
    list-done                List completed tasks
    list-todo                List tasks to do
    list-progress            List tasks in progress
    help                     Show this help message
    version                  Show version information

Examples:
    python task_tracker.py add "Buy groceries"
    python task_tracker.py start 1
    python task_tracker.py list
    python task_tracker.py delete 3
    """
    print(help_text)

def show_version():
    print("task tracker version - 1.0.0")

def main():
    if len(sys.argv) < 2:
        show_help()
        return 
    
    command = sys.argv[1].lower()

    try:
        if command == "add":
            if len(sys.argv) < 3:
                print("Error: Task description required")
                print("Usage: python task_tracker.py add \"Task description\"")
                return
            description = " ".join(sys.argv[2:])
            add_task(description)

        elif command == "update":
            if len(sys.argv) < 4:
                print("Error: Task ID and new description required")
                print("Usage: python task_tracker.py update <task_id> \"new description\"")
                return
            task_id = int(sys.argv[2])
            new_description = " ".join(sys.argv[3:])
            update_task(task_id, new_description)

        elif command == "delete":
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                print("Usage: python task_tracker.py delete <task.id> ")
                return
            task_id = int(sys.argv[2])
            delete_task(task_id)

        elif command == "start":
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                print("Usage: python task_tracker.py start <task.id>")
                return
            change_status(sys.argv[2], STATUS_IN_PROGRESS)

        elif command == "done":
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                print("Usage: python task_tracker.py done <task.id>")
                return
            change_status(sys.argv[2], STATUS_DONE)
        
        elif command == "todo":
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                print("Usage: python task_tracker.py todo <task.id>")
                return
            change_status(sys.argv[2], STATUS_TODO)

        elif command == "list":   
            list_tasks()

        elif command == "list-done":
            list_tasks(STATUS_DONE)

        elif command == "list-in-progress":
            list_tasks(STATUS_IN_PROGRESS)

        elif command == "list-todo":
            list_tasks(STATUS_TODO)
        
        elif command == "help":
            show_help()
        
        elif command == "version":
            show_version()

        else:
            print("Error: Unknown command '{command}'")
            print("Use 'help' to see available commands.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
          

if __name__ == "__main__":
    main() 



    #def get_tasks(self):
        #self.update_status("todo") 
        #return self.tasks

'''
def get_todo_list(self):
    self.update_task("todo")        # <---- DANGER
    return self.tasks

def get_done_list(self):
    self.update_task("done")
    return self.tasks

def get_in_progress_list(self):
    self.update_task("in-progess")
    return self.tasks
    

add_task = TaskTracker( "task_id", "description", "status", "createdAt", "updatedAt")
print(add_task.add_task("do some pushups"))
print(add_task.add_task("eat healthy food"))
print(add_task.add_task("do some yoga"))
print(type(add_task.add_task("do some pushups")))
print(id(add_task.add_task("do some pushups")))
print(id(add_task.add_task("eat healthy food")))'''

#get_tasks = TaskTracker("name", "task_id", "description", "status", "createdAt", "updatedAt")
#print(get_tasks.get_tasks())

#delete_task = TaskTracker( "task_id", "description", "status", "createdAt", "updatedAt")
#print(delete_task.delete_task())



