from dataclasses import dataclass
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
from sqlite3 import IntegrityError

from grasshopper.tracker.model.db import get_db


class UserAlreadyExistsError(Exception):
    pass


@dataclass
class User:
    id: str
    username: str
    password: str
    email: str

    @staticmethod
    def find_by_id(user_id):
        """ Retrieve a user by id """
        db = get_db()

        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if user is None:
            return None
        return User(id=user['id'],
                    username=user['username'],
                    password=user['password'],
                    email=user['email'])

    @staticmethod
    def find_by_username(username):
        """ Retrieve a user by username """
        db = get_db()

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            return None
        return User(id=user['id'],
                    username=user['username'],
                    password=user['password'],
                    email=user['email'])

    @staticmethod
    def create(username, email, password):
        """
        Create a new user.
        Raise an error if the user already exists.
        """
        db = get_db()

        try:
            db.execute('''
                INSERT INTO
                    user (id, username, email, password)
                VALUES (?, ?, ?, ?)
                ''',
                       (uuid4().bytes,
                        username,
                        email,
                        generate_password_hash(password)))
            db.commit()
        except IntegrityError as e:
            raise UserAlreadyExistsError(e)

    def check_password(self, password):
        return check_password_hash(self.password, password)
