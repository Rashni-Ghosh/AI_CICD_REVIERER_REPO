import os

def get_username():
    return os.getenv("USERNAME")
def greet_user(username):
    if not username:
        return "Hello user"

    return f"Hello {username}"
if __name__ == "__main__":
    username = get_username()
    print(greet_user(username))