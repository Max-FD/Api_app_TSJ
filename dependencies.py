from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import Usuario


def get_usuario_by_correo(correo: str, session: Session) -> Usuario:
    """
    Busca un usuario por correo
    Lanza HTTPException si no existe
    """
    statement = select(Usuario).where(Usuario.correo == correo)
    usuario = session.exec(statement).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    return usuario


def get_usuario_by_id(id_usuario: int, session: Session) -> Usuario:
    """
    Busca un usuario por ID
    Lanza HTTPException si no existe
    """
    usuario = session.get(Usuario, id_usuario)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return usuario
