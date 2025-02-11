from dataclasses import dataclass
from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from sqlite3 import IntegrityError


class UserAlreadyExistsError(Exception):
    pass

@dataclass
class User:
    id: str
    username: str
    password: str
    email: str

    @staticmethod
    def find_by_username(username):
        """ Retrieve a user by username """
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            return None
        return User(id=user['id'], username=user['username'], password=user['password'], email=user['email'])

    @staticmethod
    def create(username, email, password):
        """ Create a new user, will raise an error if the user already exists """
        try:
            db = get_db()
            db.execute(
                "INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                (username, email, generate_password_hash(password)),
            )
            db.commit()
        except IntegrityError as e:
            raise UserAlreadyExistsError(e)

    def check_password(self, password):
        return check_password_hash(self.password, password)
