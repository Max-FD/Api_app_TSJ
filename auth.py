import logging
from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import (
    CoordenadaAdmin,
    RondaAsignada,
    RutaCoordenada,
    TipoRonda,
    TipoUsuario,
    Usuario,
)
from schemas import (
    CoordenadaAdminResponse,
    LoginRequest,
    LoginResponse,
    RondaAsignadaResponse,
    RondaCoordenadaResponse,
    TipoRondaResponse,
    TipoUsuarioResponse,
    UsuarioResponse,
)
from security import verify_password

router = APIRouter(prefix="/api", tags=["Autenticación"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """
    Autentica al usuario y retorna sus datos + rondas asignadas (hoy y mañana)
    """
    try:
        # 1. VALIDAR USUARIO
        statement = select(Usuario).where(Usuario.correo == request.correo)
        usuario = session.exec(statement).first()

        if not usuario:
            logger.warning(f"Intento de login fallido - correo no encontrado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
            )

        # Verificar contraseña
        if not verify_password(request.contrasena, usuario.contrasena):
            logger.warning(
                f"Intento de login fallido - contraseña incorrecta para usuario {usuario.id_usuario}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
            )

        logger.info(f"Login exitoso - Usuario: {usuario.id_usuario}")

        # Obtener tipo de usuario
        tipo_usuario = session.get(TipoUsuario, usuario.id_tipo)

        # 2. OBTENER TIPOS DE RONDA
        tipos_ronda = session.exec(select(TipoRonda)).all()
        tipos_ronda_response = [
            TipoRondaResponse(
                id_tipo=tr.id_tipo, nombre_tipo_ronda=tr.nombre_tipo_ronda
            )
            for tr in tipos_ronda
        ]

        # 3. OBTENER COORDENADAS ADMIN
        coordenadas = session.exec(select(CoordenadaAdmin)).all()
        coordenadas_response = []

        for coord in coordenadas:
            coord_data = CoordenadaAdminResponse(
                id_coordenada_admin=coord.id_coordenada_admin,
                latitud=float(coord.latitud) if coord.latitud is not None else None,
                longitud=float(coord.longitud) if coord.longitud is not None else None,
                nombre_coordenada=coord.nombre_coordenada,
                codigo_qr=coord.codigo_qr,
            )
            coordenadas_response.append(coord_data)

        # 4. OBTENER RONDAS ASIGNADAS (HOY Y MAÑANA)
        hoy = date.today()
        manana = hoy + timedelta(days=1)

        statement = select(RondaAsignada).where(
            RondaAsignada.id_usuario == usuario.id_usuario,
            RondaAsignada.fecha_de_ejecucion.in_([hoy, manana]),
        )
        rondas_asignadas = session.exec(statement).all()

        # 5. TRANSFORMAR RUTAS
        rondas_response = []
        for ronda in rondas_asignadas:
            # Obtener coordenadas de la ruta
            statement = (
                select(RutaCoordenada)
                .where(RutaCoordenada.id_ruta == ronda.id_ruta)
                .order_by(RutaCoordenada.orden)
            )

            ruta_coordenadas = session.exec(statement).all()

            coordenadas_ronda = [
                RondaCoordenadaResponse(
                    id_coordenada_admin=rc.id_coordenada_admin, orden=rc.orden
                )
                for rc in ruta_coordenadas
            ]

            # Formatear fechas para Flutter
            fecha_str = ronda.fecha_de_ejecucion.strftime("%Y-%m-%d")
            hora_str = f"{fecha_str}T{ronda.hora_de_ejecucion.strftime('%H:%M:%S')}"

            rondas_response.append(
                RondaAsignadaResponse(
                    id_ronda_asignada=ronda.id_ronda_asignada,
                    id_tipo=ronda.id_tipo,
                    id_usuario=ronda.id_usuario,
                    fecha_de_ejecucion=fecha_str,
                    hora_de_ejecucion=hora_str,
                    distancia_permitida=(
                        float(ronda.distancia_permitida)
                        if ronda.distancia_permitida
                        else 50.0
                    ),
                    coordenadas=coordenadas_ronda,
                )
            )

        logger.info(
            f"Usuario {usuario.id_usuario} obtuvo {len(rondas_response)} rondas asignadas"
        )

        # 6. CONSTRUIR RESPUESTA
        return LoginResponse(
            usuario=UsuarioResponse(
                id_usuario=usuario.id_usuario,
                id_tipo=usuario.id_tipo,
                nombre=usuario.nombre,
                correo=usuario.correo,
                tipo_usuario=(
                    TipoUsuarioResponse(
                        tipo_id=tipo_usuario.tipo_id,
                        nombre_tipo_usuario=tipo_usuario.nombre_tipo_usuario,
                    )
                    if tipo_usuario
                    else None
                ),
            ),
            tipos_ronda=tipos_ronda_response,
            coordenadas_admin=coordenadas_response,
            rondas_asignadas=rondas_response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/ping")
def ping():
    """
    Endpoint simple para verificar si la API está activa
    Útil para monitoreo y health checks
    """
    return {"message": "pong", "status": "ok"}
