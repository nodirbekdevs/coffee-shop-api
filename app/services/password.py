import secrets
import string
import hashlib
from typing import Optional
from passlib.context import CryptContext


class PasswordManager:
    def __init__(self, rounds: int = 12):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=rounds
        )

    def _pre_hash(self, password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def hash(self, plain_password: str) -> str:
        return self.pwd_context.hash(self._pre_hash(plain_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pre_hashed = self._pre_hash(plain_password)
            return self.pwd_context.verify(pre_hashed, hashed_password)
        except Exception:
            return False

    def needs_update(self, hashed_password: str) -> bool:
        return self.pwd_context.needs_update(hashed_password)

    def generate_random_password(self, length: int = 16) -> str:
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")

        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|"

        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special),
        ]

        all_chars = lowercase + uppercase + digits + special
        password += [secrets.choice(all_chars) for _ in range(length - 4)]

        secrets.SystemRandom().shuffle(password)

        return "".join(password)

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Optional[str]]:
        is_valid = self.verify(plain_password, hashed_password)

        if is_valid and self.needs_update(hashed_password):
            new_hash = self.hash(plain_password)
            return True, new_hash

        return is_valid, None


password_manager = PasswordManager()
