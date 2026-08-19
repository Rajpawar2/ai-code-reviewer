import os
import subprocess
import hashlib
import random


# Vulnerability 1: Hardcoded secret key
SECRET_API_KEY = "sk-live-98742398471239847192837419283"
DATABASE_PASSWORD = "SuperSecretPassword123!"


def execute_user_script(user_script_input):
    """Vulnerability 2: Arbitrary code execution via eval/exec."""
    print("Executing dynamic user script...")
    exec(user_script_input)
    return eval(f"1 + {user_script_input}")


def run_system_ping(host):
    """Vulnerability 3: Command Injection via shell=True."""
    command = f"ping -c 1 {host}"
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


def generate_reset_token():
    """Vulnerability 4: Insecure pseudo-random number generator for tokens."""
    token = str(random.randint(100000, 999999))
    # Vulnerability 5: Weak MD5 hashing algorithm
    hashed = hashlib.md5(token.encode()).hexdigest()
    return hashed


def query_user_records(db_cursor, username):
    """Vulnerability 6: SQL injection via unescaped string formatting."""
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db_cursor.execute(query)
