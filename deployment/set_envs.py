import sys
import random
import string
import os

DB_USER = "items-user"
DB_NAME = "items-db"
DB_HOST = "db"

def generate_password(lenth=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(lenth))


def main():
    if len(sys.argv) < 2:
        print("Usage 'python3 set_envs.py <IMAGE_TAG>'")
        sys.exit(1)

    app_image = sys.argv[1]
    db_user = DB_USER
    db_name = DB_NAME
    db_host = DB_HOST

    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()
        
        new_lines = []
        updated = False
        db_pass_line = None

        for line in lines:
            if line.startswith("APP_IMAGE="):
                new_lines.append(f"APP_IMAGE={app_image}\n")
                updated = True
            elif line.startswith("DB_PASS="):
                db_pass_line = line
                new_lines.append(db_pass_line)
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"APP_IMAGE={app_image}\n")
        
        if db_pass_line is None:
            new_lines.append(f"DB_PASS={generate_password(lenth=12)}\n")

        with open(".env", "w") as f:
            f.writelines(new_lines)

        print(".env updated with APP_IMAGE")
    else:
        db_pass = generate_password(12)
        env_content = f"""APP_IMAGE={app_image}\nDB_USER={db_user}\nDB_PASS={db_pass}\nDB_NAME={db_name}\nDB_HOST={db_host}"""
        with open(".env", "w") as f:
            f.write(env_content)
        print(".env generated")

if __name__ == "__main__":
    main()