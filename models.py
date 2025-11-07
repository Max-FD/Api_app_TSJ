from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class TipoUsuario(SQLModel, table=True):
    __tablename__ = "tipos_de_usuarios"

    tipo_id: Optional[int] = Field(default=None, primary_key=True)
    nombre_tipo_usuario: str = Field(max_length=50)


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    id_tipo: int = Field(foreign_key="tipos_de_usuarios.tipo_id")
    nombre: str = Field(max_length=100)
    contrasena: str = Field(max_length=255)
    correo: Optional[str] = Field(default=None, max_length=100)


class TipoRonda(SQLModel, table=True):
    __tablename__ = "Tipo_ronda"

    id_tipo: Optional[int] = Field(default=None, primary_key=True)
    nombre_tipo_ronda: str = Field(max_length=50)


class CoordenadaAdmin(SQLModel, table=True):
    __tablename__ = "Coordenadas_admin"

    id_coordenada_admin: Optional[int] = Field(default=None, primary_key=True)
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    codigo_qr: Optional[str] = Field(default=None, max_length=255, unique=True)
    nombre_coordenada: str = Field(max_length=100)
    fecha_creacion: Optional[datetime] = Field(default_factory=datetime.now)


class Ruta(SQLModel, table=True):
    __tablename__ = "Rutas"

    id_ruta: Optional[int] = Field(default=None, primary_key=True)
    nombre_ruta: str = Field(max_length=100)
    descripcion: Optional[str] = None
    fecha_creacion: Optional[datetime] = Field(default_factory=datetime.now)


class RutaCoordenada(SQLModel, table=True):
    __tablename__ = "Ruta_coordenadas"

    id_ruta: int = Field(foreign_key="Rutas.id_ruta", primary_key=True)
    id_coordenada_admin: int = Field(
        foreign_key="Coordenadas_admin.id_coordenada_admin", primary_key=True
    )
    orden: int


class RondaAsignada(SQLModel, table=True):
    __tablename__ = "Ronda_asignada"

    id_ronda_asignada: Optional[int] = Field(default=None, primary_key=True)
    id_tipo: int = Field(foreign_key="Tipo_ronda.id_tipo")
    id_usuario: int = Field(foreign_key="usuarios.id_usuario")
    id_ruta: int = Field(foreign_key="Rutas.id_ruta")
    fecha_de_ejecucion: date
    hora_de_ejecucion: time
    distancia_permitida: Decimal


class RondaUsuario(SQLModel, table=True):
    __tablename__ = "rondas_usuarios"

    id_ronda_usuario: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id_usuario")
    id_ronda_asignada: int = Field(foreign_key="Ronda_asignada.id_ronda_asignada")
    fecha: date
    hora_inicio: time
    hora_final: Optional[time] = None
    sincronizada: int = Field(default=0)


class CoordenadaUsuario(SQLModel, table=True):
    __tablename__ = "coordenadas_usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_ronda_usuario: int = Field(foreign_key="rondas_usuarios.id_ronda_usuario")
    hora_actual: time
    latitud_actual: Optional[Decimal] = None
    longitud_actual: Optional[Decimal] = None
    codigo_qr: Optional[str] = Field(default=None, max_length=255)
    verificador: int = Field(default=0)
