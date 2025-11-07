import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash

    IMPORTANTE: La BD usa hashes de PHP ($2y$)
    bcrypt en Python usa $2b$ pero son compatibles
    """
    try:
        if hashed_password.startswith("$2y$"):
            hashed_password = "$2b$" + hashed_password[4:]

        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {e}")
        return False
