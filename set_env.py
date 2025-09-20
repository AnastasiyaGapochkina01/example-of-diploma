import sys
import random
import string
import os

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

    if os.path.exists(".env"):
        # читаем существующие переменные
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
                # сохраняем старый пароль
                db_pass_line = line
                new_lines.append(line)
            else:
                new_lines.append(line)

        # если APP_IMAGE не было найдено, добавляем в конец
        if not updated:
            new_lines.append(f"APP_IMAGE={app_image}\n")

        # если почему-то DB_PASS не было — создаём
        if db_pass_line is None:
            new_lines.append(f"DB_PASS={generate_password(12)}\n")

        with open(".env", "w") as f:
            f.writelines(new_lines)

        print(".env file updated: APP_IMAGE set (DB_PASS preserved)")
    else:
        # генерируем всё заново
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
