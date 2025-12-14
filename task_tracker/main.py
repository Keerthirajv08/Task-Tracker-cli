from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Task       #Import the blueprint you created earlier 

engine = create_engine('sqlite:///task_tracker.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#     #Initialize the database if it's empty
if session.query(Task).count() == 0:
    print("--- CREATING INITIAL TASK ---")
    new_task = Task(title="Prepare for SQLAlchemy tutorial", status="To Do")
    session.add(new_task)
    session.commit()
    print(f"Initial Task ID: {new_task.id} saved.")
else:
    print("---Skipping initial task creation (task already exists)---")


#print(f"Task saved successfully! ID: {new_task.id}")

#UPDATE: Change the status of a task
print("\n===UPDATING TASK STATUS===")

# Find the task to update
task_to_update = session.query(Task).filter(Task.title == "Prepare for SQLAlchemy tutorial").first()

if task_to_update:
    print(f"Changing status of Task ID: {task_to_update.id} from '{task_to_update.status}' to 'In Progress'")
    task_to_update.status = "In Progress"
    session.commit()
    print(f"Task updated successfully! ID: {task_to_update.id}")
else:
    print("Task not found for update.")

#print("\n===READING DATABASE===")
#tasks = session.query(Task).all()

#READ: verify the update
print("\n=== VERIFYING UPDATE (All Tasks) ===")
all_tasks = session.query(Task).all()

for task in all_tasks:
    print(f"ID: {task.id}, | Title: {task.title}, | Status: {task.status}")


#DELETE: Remove the task
print("\n=== DELETING TASK ===")

if task_to_update:
    print(f"Deleting Task ID: {task_to_update.id}: {task_to_update.title}")
    session.delete(task_to_update)
    session.commit()
    print(f"Task deleted successfully! ID: {task_to_update.id}")

#final read: confirm of deletion
print("\n=== FINAL CHECK (should be empty or fewer tasks) ===")
final_tasks = session.query(Task).all()

if not final_tasks:
    print("The database is now empty.")
else:
    print("The database still contains the following tasks:")
    for task in final_tasks:
        print(f"ID: {task.id}, | Title: {task.title}, | Status: {task.status}")



