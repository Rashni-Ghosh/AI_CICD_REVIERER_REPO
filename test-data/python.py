import subprocess
import os

# TEST CASE 1: Hard-coded password
password = "MySecretPassword123"

# TEST CASE 2: Hard-coded API key
api_key = "123456789"

# TEST CASE 3: Hard-coded token
token = "abc123-super-secret-token"

# TEST CASE 4: Dangerous command execution
user_input = input("Enter a command to execute: ")
subprocess.run(user_input, shell=True)

# TEST CASE 5: os.system
os.system(user_input)

# TEST CASE 6: eval
user_code = input("Enter Python expression: ")
result = eval(user_code)

# TEST CASE 7: exec
exec(user_code)