import os
import requests

#CASE 1. Production debug mode
DEBUG = True

#CASE 2. Database credentials embedded in the connection string
DATABASE_URL = "mysql://admin:password123@localhost:3306/customerdb"


def get_user(user_id):
    #CASE 3. URL construction from user input
    url = "https://api.example.com/users/" + user_id

    #CASE 4. No error handling and No request timeout
    response = requests.get(url)

    return response.json()


def process_payment(amount):
    if amount > 0:
        print("Payment processed:", amount)

    return True


def load_config():
    config = {
        "environment": "production",
        "debug": DEBUG,
        "database": DATABASE_URL
    }

    return config


def send_data(data):
    #CASE 5. No request timeout
    requests.post(
        "https://api.example.com/upload",
        json=data
    )


def get_file(filename):
    #CASE 6. User-controlled file path
    file_path = "/app/uploads/" + filename

    with open(file_path, "r") as file:
        return file.read()


if __name__ == "__main__":
    user_id = input("Enter user ID: ")

    user = get_user(user_id)
    #CASE 7. Sensitive data handling
    print(user)

    process_payment(100)

    send_data(user)