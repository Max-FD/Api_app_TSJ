import logging
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from models import CoordenadaUsuario, RondaUsuario
from schemas import SubirRondaRequest, SubirRondaResponse

router = APIRouter(prefix="/api/rondas", tags=["Rondas"])
logger = logging.getLogger(__name__)


@router.post("/subir", response_model=SubirRondaResponse)
def subir_ronda(request: SubirRondaRequest, session: Session = Depends(get_session)):
    """
    Recibe una ronda completada desde Flutter y la guarda en MySQL

    Flujo:
    1. Convierte fechas de Flutter (strings) a tipos MySQL (date, time)
    2. Guarda en rondas_usuarios
    3. Guarda todas las coordenadas en coordenadas_usuarios
    4. Retorna el ID de la ronda creada
    """
    try:
        # 1. CONVERTIR FECHAS
        fecha = datetime.strptime(request.fecha, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(request.hora_inicio, "%Y-%m-%dT%H:%M:%S").time()
        hora_final = datetime.strptime(request.hora_final, "%Y-%m-%dT%H:%M:%S").time()

        # 2. CREAR RONDA_USUARIO
        nueva_ronda = RondaUsuario(
            id_usuario=request.id_usuario,
            id_ronda_asignada=request.id_ronda_asignada,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_final=hora_final,
            sincronizada=1,
        )

        session.add(nueva_ronda)
        session.commit()
        session.refresh(nueva_ronda)

        logger.info(
            f"Ronda creada - ID: {nueva_ronda.id_ronda_usuario}, "
            f"Usuario: {request.id_usuario}, "
            f"Coordenadas: {len(request.coordenadas)}"
        )

        # 3. GUARDAR COORDENADAS
        for coord_data in request.coordenadas:
            hora_actual = datetime.strptime(
                coord_data.hora_actual, "%Y-%m-%dT%H:%M:%S"
            ).time()

            coordenada = CoordenadaUsuario(
                id_ronda_usuario=nueva_ronda.id_ronda_usuario,
                hora_actual=hora_actual,
                latitud_actual=(
                    Decimal(str(coord_data.latitud_actual))
                    if coord_data.latitud_actual
                    else None
                ),
                longitud_actual=(
                    Decimal(str(coord_data.longitud_actual))
                    if coord_data.longitud_actual
                    else None
                ),
                codigo_qr=coord_data.codigo_qr,
                verificador=1 if coord_data.verificador else 0,
            )

            session.add(coordenada)

        session.commit()

        logger.info(f"Ronda {nueva_ronda.id_ronda_usuario} guardada exitosamente")

        return SubirRondaResponse(
            success=True,
            message=f"Ronda guardada exitosamente con {len(request.coordenadas)} coordenadas",
            id_ronda_usuario=nueva_ronda.id_ronda_usuario,
        )

    except ValueError as e:
        logger.warning(f"Formato de fecha inválido en subir_ronda: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido",
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error al guardar ronda: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar ronda",
        )


@router.get("/asignadas/{id_usuario}")
def obtener_rondas_asignadas(id_usuario: int, session: Session = Depends(get_session)):
    """
    Obtiene las rondas asignadas de un usuario (hoy y mañana)
    Útil si se quiere actualizar rondas sin hacer login completo
    """
    try:
        from datetime import date, timedelta

        from sqlmodel import select

        from models import RondaAsignada

        hoy = date.today()
        manana = hoy + timedelta(days=1)

        statement = select(RondaAsignada).where(
            RondaAsignada.id_usuario == id_usuario,
            RondaAsignada.fecha_de_ejecucion.in_([hoy, manana]),
        )

        rondas = session.exec(statement).all()

        logger.info(
            f"Usuario {id_usuario} consultó rondas asignadas - Total: {len(rondas)}"
        )

        return {
            "total": len(rondas),
            "rondas": [
                {
                    "id_ronda_asignada": r.id_ronda_asignada,
                    "fecha": r.fecha_de_ejecucion.strftime("%Y-%m-%d"),
                    "hora": r.hora_de_ejecucion.strftime("%H:%M:%S"),
                }
                for r in rondas
            ],
        }

    except Exception as e:
        logger.error(f"Error al obtener rondas asignadas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener rondas asignadas",
        )
