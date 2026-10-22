
import getpass
import os

from database import create_user, initialize_database, get_user_by_username


def main():
    initialize_database()

    accounts = [
        ("alice", "INITIAL_ALICE_PASSWORD", "user"),
        ("bob", "INITIAL_BOB_PASSWORD", "user"),
        ("admin", "INITIAL_ADMIN_PASSWORD", "admin"),
    ]

    for username, variable_name, role in accounts:
        if get_user_by_username(username) is not None:
            print(f"{username}: account already exists; leaving unchanged.")
            continue

        password = os.environ.get(variable_name)

        if not password:
            password = getpass.getpass(
                f"Set a password for {username} (minimum 12 characters): "
            )

        create_user(username, password, role)
        print(f"{username}: account created.")

    print("Database initialization complete.")


if __name__ == "__main__":
    main()
