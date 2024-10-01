from contextlib import _RedirectStream
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import mysql.connector

# Replace with your MySQL connection details
MYSQL_CONFIG = {
    "host": "localhost",
    "port":3306,
    "user": "root",
    "password": "root@sql",
    "database": "fast",
}



def create_users_table(cursor):
    try:
        # SQL query to create a users table
        create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(255)
            )
        """
        cursor.execute(create_table_query)
        print("Users table created successfully.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

def insert_user(cursor, name, email, username, password):
    try:
        # SQL query to insert a user into the users table
        insert_query = """
            INSERT INTO users (name, email, username, password)
            VALUES (%s, %s, %s, %s)
        """
        user_data = (name, email, username, password)
        cursor.execute(insert_query, user_data)
        print("User inserted successfully.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")

# Establish a connection to the MySQL database
try:
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    # Create users table
    create_users_table(cursor)

    # Insert a user into the users table
    # insert_user(cursor, "John Doe", "john@example.com", "johndoe", "password123")

    conn.commit()

except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()


def get_all_items_from_table():
    try:
        # Establish a connection to the MySQL database
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # Execute a SELECT query to retrieve all items from the table
        cursor.execute("SELECT * FROM users")

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Process the fetched rows
        # for row in rows:
        #     print(row)  # Print or process each row as needed
        
        return rows

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

users = get_all_items_from_table()

# print(users)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("Login.html", {"request": request})

@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse("Welcome.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):

    for user in users:
        # print(user)
        username_curr = user[3]
        password_curr = user[4]
        if(username_curr == username and password_curr == password):
            return templates.TemplateResponse("Users.html", {"request": request, "user_list":users})
    
    return templates.TemplateResponse("Login.html", {"request": request})

@app.get('/register', response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("Register.html", {"request": request})


@app.post('/register-post')
async def register(request: Request, username: str = Form(...), name: str = Form(...), password: str = Form(...), email: str = Form(...)):

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    insert_user(cursor, name, email, username, password)

    conn.commit()

    return {"message": "user added"}
