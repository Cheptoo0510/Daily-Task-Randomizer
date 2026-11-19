
import random
import mysql.connector
from datetime import date, timedelta

# ==========================================
# DATABASE CONNECTION
# ==========================================

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="daily_productivity",
        port=3306
    )

    cursor = connection.cursor()

    print("Successfully connected to MySQL!")

except mysql.connector.Error as error:
    print("Database connection failed:", error)
    raise SystemExit


# ==========================================
# INITIAL SETUP
# ==========================================

today = date.today()
tomorrow = today + timedelta(days=1)

tasks = []
completed_tasks = []
current_task = None


# ==========================================
# LOAD TODAY'S PENDING TASKS
# ==========================================

print("\n================================")
print("     DAILY TASK RANDOMIZER")
print("================================")

print("\nToday's date:", today)

# Load today's tasks and any older unfinished tasks
cursor.execute("""
    SELECT task_id, task_name, task_date
    FROM tasks
    WHERE task_date <= %s
    AND status = 'pending'
""", (today,))

tasks = cursor.fetchall()

print("\nPending tasks loaded:", len(tasks))


# ==========================================
# MAIN PROGRAM
# ==========================================

while True:

    # Select a random task if there is no current task
    if tasks and current_task is None:
        current_task = random.choice(tasks)

    # Display current task
    if current_task is not None:

        print("\n================================")
        print("🎯 YOUR NEXT TASK:")
        print(current_task[1])
        print("================================")

    else:
        print("\nYou have no pending tasks right now!")

    print("\nCommands:")
    print("done     - Complete current task")
    print("add      - Add a task for today")
    print("tomorrow - Schedule a task for tomorrow")
    print("skip     - Get another random task")
    print("history  - View completed tasks")
    print("quit     - Exit the program")

    command = input("\nYour response: ").strip().lower()


    # ======================================
    # COMPLETE A TASK
    # ======================================

    if command == "done":

        if current_task is None:
            print("\nThere is no task to complete!")

        else:

            task_id = current_task[0]

            cursor.execute("""
                UPDATE tasks
                SET status = 'completed'
                WHERE task_id = %s
            """, (task_id,))

            connection.commit()

            completed_tasks.append(current_task[1])

            tasks = [
                task for task in tasks
                if task[0] != task_id
            ]

            current_task = None

            print("\n🎉 Excellent! Task completed!")


    # ======================================
    # ADD A TASK FOR TODAY
    # ======================================

    elif command == "add":

        new_task = input("\nEnter your new task: ").strip()

        if new_task:

            cursor.execute("""
                INSERT INTO tasks (task_name, task_date, status)
                VALUES (%s, %s, 'pending')
            """, (new_task, today))

            connection.commit()

            new_task_id = cursor.lastrowid

            tasks.append((new_task_id, new_task, today))

            print("\n✅ Task saved to the database!")

        else:
            print("\nNo task was entered.")


    # ======================================
    # SCHEDULE A TASK FOR TOMORROW
    # ======================================

    elif command == "tomorrow":

        new_task = input("\nEnter tomorrow's task: ").strip()

        if new_task:

            cursor.execute("""
                INSERT INTO tasks (task_name, task_date, status)
                VALUES (%s, %s, 'pending')
            """, (new_task, tomorrow))

            connection.commit()

            print("\n✅ Task successfully scheduled for tomorrow!")
            print("Scheduled date:", tomorrow)

        else:
            print("\nNo task was entered.")


    # ======================================
    # SKIP CURRENT TASK
    # ======================================

    elif command == "skip":

        if current_task is None:
            print("\nThere is no task to skip!")

        elif len(tasks) == 1:
            print("\nOnly one unfinished task remains!")
            print("You'll have to tackle this one! 💪")

        else:

            other_tasks = [
                task for task in tasks
                if task[0] != current_task[0]
            ]

            current_task = random.choice(other_tasks)

            print("\nNo problem! Here's another task.")


    # ======================================
    # VIEW COMPLETED TASK HISTORY
    # ======================================

    elif command == "history":

        cursor.execute("""
            SELECT task_name, task_date
            FROM tasks
            WHERE status = 'completed'
            ORDER BY task_date DESC, task_id DESC
        """)

        history = cursor.fetchall()

        print("\n================================")
        print("       COMPLETED TASK HISTORY")
        print("================================")

        if history:

            for number, task in enumerate(history, start=1):
                print(f"{number}. {task[0]} (Date: {task[1]})")

            print("\nTotal completed tasks:", len(history))

        else:
            print("\nNo completed tasks found yet.")


    # ======================================
    # QUIT PROGRAM
    # ======================================

    elif command == "quit":

        print("\n⏸️ You have exited the program.")

        break


    # ======================================
    # INVALID COMMAND
    # ======================================

    else:

        print("\nInvalid command!")
        print("Please enter a valid command.")


# ==========================================
# SESSION SUMMARY
# ==========================================

print("\n================================")
print("          SESSION SUMMARY")
print("================================")

print("\nTasks completed this session:")

if completed_tasks:

    for number, task in enumerate(completed_tasks, start=1):
        print(f"{number}. {task}")

else:
    print("No tasks completed this session.")

print("\nTotal completed this session:", len(completed_tasks))

print("\nRemaining pending tasks:")

if tasks:

    for task in tasks:
        print("-", task[1])

else:
    print("No pending tasks for today!")

print("\nKeep going! You've got this. 💪")


# ==========================================
# CLOSE DATABASE CONNECTION
# ==========================================

cursor.close()
connection.close()

print("\nDatabase connection closed successfully.")
