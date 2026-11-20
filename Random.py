
import mysql.connector
import random
from datetime import date


# ---------------- DATABASE CONNECTION ----------------

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="daily_productivity",
        port=3306
    )


# ---------------- DISPLAY FUNCTIONS ----------------

def show_pending_tasks(cursor):
    cursor.execute("""
        SELECT task_id, task_name, task_date
        FROM tasks
        WHERE status = 'pending'
          AND task_date <= CURDATE()
        ORDER BY task_date, task_id
    """)

    tasks = cursor.fetchall()

    print("\n========== YOUR PENDING TASKS ==========")

    if not tasks:
        print("You have no pending tasks for today.")
    else:
        for number, task in enumerate(tasks, start=1):
            print(f"{number}. ID: {task[0]} | {task[1]} (Date: {task[2]})")

    return [task[0] for task in tasks]


def show_history(cursor):
    cursor.execute("""
        SELECT task_name, completed_at
        FROM tasks
        WHERE status = 'completed'
        ORDER BY completed_at DESC
    """)

    history = cursor.fetchall()

    print("\n========== TASK HISTORY ==========")

    if not history:
        print("No completed tasks yet.")
    else:
        for task_name, completed_at in history:
            print(f"- {task_name} | Completed: {completed_at}")


def show_todays_completed_tasks(cursor):
    cursor.execute("""
        SELECT task_name, completed_at
        FROM tasks
        WHERE status = 'completed'
          AND DATE(completed_at) = CURDATE()
        ORDER BY completed_at
    """)

    tasks = cursor.fetchall()

    print("\n========== TODAY'S COMPLETED TASKS ==========")

    if not tasks:
        print("No tasks were completed today.")
    else:
        for number, task in enumerate(tasks, start=1):
            print(f"{number}. {task[0]} | {task[1]}")

    print(f"\nTotal completed today: {len(tasks)}")


# ---------------- ADD TASK FUNCTION ----------------

def add_task(cursor, connection):
    task_name = input("\nEnter the task name: ").strip()

    if not task_name:
        print("Task name cannot be empty.")
        return None

    cursor.execute("""
        INSERT INTO tasks (task_name, task_date, status)
        VALUES (%s, %s, 'pending')
    """, (task_name, date.today()))

    connection.commit()

    task_id = cursor.lastrowid

    print(f"Task '{task_name}' saved successfully!")

    return task_id


# ---------------- DELETE TASK FUNCTIONS ----------------

def delete_task(cursor, connection, task_id):
    cursor.execute("""
        DELETE FROM tasks
        WHERE task_id = %s
          AND status = 'pending'
    """, (task_id,))

    connection.commit()

    return cursor.rowcount > 0


def delete_task_prompt(cursor, connection, active_tasks, skipped_tasks):

    cursor.execute("""
        SELECT task_id, task_name, task_date
        FROM tasks
        WHERE status = 'pending'
        ORDER BY task_date, task_id
    """)

    tasks = cursor.fetchall()

    if not tasks:
        print("\nThere are no pending tasks to delete.")
        return

    print("\n========== DELETE A TASK ==========")

    for task_id, task_name, task_date in tasks:
        print(f"ID: {task_id} | {task_name} | Date: {task_date}")

    try:
        task_id = int(input("\nEnter the ID of the task to delete: "))
    except ValueError:
        print("Please enter a valid task ID.")
        return

    existing_ids = [task[0] for task in tasks]

    if task_id not in existing_ids:
        print("Task ID not found.")
        return

    confirmation = input(
        "Are you sure you want to delete this task? (YES/NO): "
    ).strip().upper()

    if confirmation == "YES":

        if delete_task(cursor, connection, task_id):

            if task_id in active_tasks:
                active_tasks.remove(task_id)

            if task_id in skipped_tasks:
                skipped_tasks.remove(task_id)

            print("Task deleted successfully!")

        else:
            print("Could not delete the task.")

    else:
        print("Deletion cancelled.")


# ---------------- MAIN PROGRAM ----------------

def main():

    connection = None
    cursor = None

    try:
        connection = connect_db()
        cursor = connection.cursor()

        print("\n======================================")
        print("       DAILY TASK RANDOMIZER")
        print("======================================")

        # Load previously saved pending tasks
        active_tasks = show_pending_tasks(cursor)

        # Tasks skipped during this session
        skipped_tasks = []

        # ----------------------------------
        # WAITING FOR USER TO START
        # ----------------------------------

        print("\nYou can add, delete or view tasks before starting.")
        print("Type START when you are ready.")

        while True:

            command = input(
                "\nCommand (START / ADD / DELETE / HISTORY / QUIT): "
            ).strip().upper()

            if command == "START":
                break

            elif command == "ADD":

                task_id = add_task(cursor, connection)

                if task_id is not None:
                    active_tasks.append(task_id)

            elif command == "DELETE":

                delete_task_prompt(
                    cursor, connection, active_tasks, skipped_tasks
                )

            elif command == "HISTORY":

                show_history(cursor)

            elif command == "QUIT":

                print("\nYour pending tasks have been saved.")
                print("See you next time!")
                return

            else:
                print("Invalid command. Try START, ADD, DELETE, HISTORY or QUIT.")

        # ----------------------------------
        # RANDOM TASK SESSION
        # ----------------------------------

        print("\n========== LET'S GET TO WORK! ==========")

        while active_tasks:

            # Randomly select a task
            selected_id = random.choice(active_tasks)

            cursor.execute("""
                SELECT task_name
                FROM tasks
                WHERE task_id = %s
                  AND status = 'pending'
            """, (selected_id,))

            result = cursor.fetchone()

            if result is None:
                active_tasks.remove(selected_id)
                continue

            task_name = result[0]

            print("\n--------------------------------------")
            print(f"YOUR NEXT TASK: {task_name}")
            print("--------------------------------------")

            command = input(
                "\nEnter DONE, SKIP, ADD, DELETE, TOMORROW, HISTORY or QUIT: "
            ).strip().upper()

            if command == "DONE":

                cursor.execute("""
                    UPDATE tasks
                    SET status = 'completed',
                        completed_at = NOW()
                    WHERE task_id = %s
                """, (selected_id,))

                connection.commit()

                active_tasks.remove(selected_id)

                print("Great job! Task completed.")

            elif command == "SKIP":

                active_tasks.remove(selected_id)
                skipped_tasks.append(selected_id)

                print("Task skipped. It remains pending in your database.")

            elif command == "ADD":

                task_id = add_task(cursor, connection)

                if task_id is not None:
                    active_tasks.append(task_id)

            elif command == "DELETE":

                delete_task_prompt(
                    cursor, connection, active_tasks, skipped_tasks
                )

            elif command == "TOMORROW":

                cursor.execute("""
                    UPDATE tasks
                    SET task_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                    WHERE task_id = %s
                """, (selected_id,))

                connection.commit()

                active_tasks.remove(selected_id)

                print("Task postponed until tomorrow.")

            elif command == "HISTORY":

                show_history(cursor)

            elif command == "QUIT":

                print("\nSession ended.")
                print("Your unfinished tasks remain saved as pending.")
                return

            else:
                print("Invalid command. Please try again.")

        # ----------------------------------
        # SESSION SUMMARY
        # ----------------------------------

        print("\n========== SESSION FINISHED ==========")

        if skipped_tasks:
            print(f"You skipped {len(skipped_tasks)} task(s).")
            print("They are still pending and will appear next time.")

        print("There are no more active tasks for this session.")

        # Display today's completed tasks
        show_todays_completed_tasks(cursor)

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()
