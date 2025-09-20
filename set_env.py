import sys
import random
import string

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_env.py <APP_IMAGE>")
        sys.exit(1)

    app_image = sys.argv[1]
    db_user = "items-user"
    db_name = "items-db" 
    db_host = "db"
    db_pass = generate_password(12)

    env_content = f"""APP_IMAGE={app_image}
DB_USER={db_user}
DB_PASS={db_pass}
DB_NAME={db_name}
DB_HOST={db_host}
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print(".env file generated successfully.")

if __name__ == "__main__":
    main()
