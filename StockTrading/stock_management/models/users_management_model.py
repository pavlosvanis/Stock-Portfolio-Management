import os
import sqlite3
import logging
from dataclasses import dataclass
from stock_management.utils.sql_utils import get_db_connection
from flask_bcrypt import Bcrypt
from stock_management.utils.logger import configure_logger

bcrypt = Bcrypt()

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class User:
    username: str
    password_hash: str
    salt: str

    def __post_init__(self):
        if not self.username or len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long")

def create_user(username: str, password: str) -> None:
    """
    Creates a new user in the users table.

    Args:
        username (str): The desired username.
        password (str): The user's password.

    Raises:
        ValueError: If the username already exists or validation fails (e.g. password length).
        sqlite3.Error: If any database error occurs.
    """
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the username already exists before generate the salt
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                logger.error("User with username '%s' already exists.", username)
                raise ValueError(f"Username '{username}' already exists")

            salt = bcrypt.generate_password_hash(username).decode('utf-8')[:32]
            password_hash = bcrypt.generate_password_hash(password + salt).decode('utf-8')

            # Insert the new user
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt),
            )
            conn.commit()

            logger.info("User: %s created succesfully", username)

    except sqlite3.Error as e:
        logger.error("Database error while creating the user: %s", str(e))
        raise sqlite3.Error(f"Database error: {e}")

def get_user_by_username(username: str) -> User:
    """
    Retrieves a user by their username.

    Args:
        username (str): The username to look up.

    Returns:
        User: The User object if found.

    Raises:
        ValueError: If the user is not found.
        sqlite3.Error: If a database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve user with username %s", username)
            cursor.execute(
                "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if not row:
                logger.info("User with username %s not found", username)
                raise ValueError(f"User '{username}' not found")
            
            logger.info("User with username %s not found", username)
            return User(id=row[0], username=row[1], password_hash=row[2], salt=row[3])

    except sqlite3.Error as e:
        logger.error("Database error while retrieving the user by username %s: %s", username, str(e))
        raise sqlite3.Error(f"Database error: {e}")

def update_user_password(username: str, new_password: str) -> None:
    """
    Updates a user's password.

    Args:
        username (str): The username of the user.
        new_password (str): The new password.

    Raises:
        ValueError: If the user is not found or validation fails.
        sqlite3.Error: If any database error occurs.
    """
    if len(new_password) < 6:
        logger.error("The new password entered is less than 6 characters long")
        raise ValueError("New password must be at least 6 characters long")

    try:
        user = get_user_by_username(username)

        # Generate a new salt and hash the new password
        salt = bcrypt.generate_password_hash(username).decode('utf-8')[:32]
        password_hash = bcrypt.generate_password_hash(new_password + salt).decode('utf-8')

        # Update the user's password in the database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?",
                (password_hash, salt, username),
            )
            conn.commit()
        
        logger.info("Password updated for user: %s", username)

    except sqlite3.Error as e:
        logger.error("Database error while creating the user: %s", str(e))
        raise sqlite3.Error(f"Database error: {e}")

def verify_user_credentials(username: str, password: str) -> bool:
    """
    Verifies a user's credentials.

    Args:
        username (str): The username.
        password (str): The plaintext password to verify.

    Returns:
        bool: True if credentials are valid, False otherwise.

    Raises:
        ValueError: If the user is not found.
        sqlite3.Error: If any database error occurs.
    """
    try:
        user = get_user_by_username(username)
        logger.info("Password checked successfully. Results will be determined...")
        return bcrypt.check_password_hash(user.password_hash, password + user.salt)
    except sqlite3.Error as e:
        logger.error("Database error while creating the user: %s", str(e))
        raise sqlite3.Error(f"Database error: {e}")
