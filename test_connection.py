import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="daily_productivity",
        port=3306
    )

    if connection.is_connected():
        print("SUCCESS! Python is connected to MySQL!")

        cursor = connection.cursor()

        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()

        print("Connected database:", result[0])

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("\nTables in your database:")

        for table in tables:
            print(table[0])

        cursor.close()
        connection.close()

        print("\nConnection closed successfully.")

except mysql.connector.Error as error:
    print("CONNECTION FAILED!")
    print("Error:", error)