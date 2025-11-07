# schemas.py
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr

# SCHEMAS PARA LOGIN


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TipoUsuarioResponse(BaseModel):
    tipo_id: int
    nombre_tipo_usuario: str


class UsuarioResponse(BaseModel):
    id_usuario: int
    id_tipo: int
    nombre: str
    correo: Optional[str] = None
    tipo_usuario: Optional[TipoUsuarioResponse] = None


class TipoRondaResponse(BaseModel):
    id_tipo: int
    nombre_tipo_ronda: str


class CoordenadaAdminResponse(BaseModel):
    id_coordenada_admin: int
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    nombre_coordenada: str
    codigo_qr: Optional[str] = None


class RondaCoordenadaResponse(BaseModel):
    id_coordenada_admin: int
    orden: int


class RondaAsignadaResponse(BaseModel):
    id_ronda_asignada: int
    id_tipo: int
    id_usuario: int
    fecha_de_ejecucion: str  # Formato: "2025-11-03"
    hora_de_ejecucion: str  # Formato: "2025-11-03T14:30:00"
    distancia_permitida: Optional[float] = 50.0
    coordenadas: List[RondaCoordenadaResponse]


class LoginResponse(BaseModel):
    usuario: UsuarioResponse
    tipos_ronda: List[TipoRondaResponse]
    coordenadas_admin: List[CoordenadaAdminResponse]
    rondas_asignadas: List[RondaAsignadaResponse]


# SCHEMAS PARA SUBIR RONDAS


class CoordenadaUsuarioRequest(BaseModel):
    hora_actual: str  # Formato: "2025-11-03T14:30:00"
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None
    codigo_qr: Optional[str] = None
    verificador: bool


class SubirRondaRequest(BaseModel):
    id_usuario: int
    id_ronda_asignada: int
    fecha: str  # Formato: "2025-11-03"
    hora_inicio: str  # Formato: "2025-11-03T14:30:00"
    hora_final: str  # Formato: "2025-11-03T16:30:00"
    coordenadas: List[CoordenadaUsuarioRequest]


class SubirRondaResponse(BaseModel):
    success: bool
    message: str
    id_ronda_usuario: Optional[int] = None


# SCHEMAS GENERALES


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
