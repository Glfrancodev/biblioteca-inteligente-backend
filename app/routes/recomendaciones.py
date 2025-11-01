"""
Endpoints para el sistema de recomendaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.services.auth import get_current_active_user
from app.services.recommendation_service import recommendation_service
from app.utils.responses import create_success_response, create_error_response, ErrorCodes


router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])


@router.get("/entrenar")
async def entrenar_modelo(
    n_clusters: int = 5,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Entrena el modelo K-Means con los usuarios actuales
    Solo admin puede ejecutar esto
    """
    try:
        user_cluster_map = recommendation_service.train_model(db, n_clusters)
        
        return create_success_response(
            data={
                "clusters_creados": n_clusters,
                "usuarios_procesados": len(user_cluster_map),
                "distribucion": {
                    f"cluster_{i}": sum(1 for c in user_cluster_map.values() if c == i)
                    for i in range(n_clusters)
                }
            },
            message="Modelo entrenado exitosamente"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"Error al entrenar modelo: {str(e)}"
            )
        )


@router.get("")
async def obtener_recomendaciones(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene recomendaciones personalizadas para el usuario actual
    Basado en K-Means y preferencias (categorías, lenguajes, nivel)
    """
    try:
        recomendaciones = recommendation_service.get_recommendations(
            usuario_id=current_user.idUsuario,
            db=db,
            limit=limit
        )
        
        return create_success_response(
            data=recomendaciones,
            message=f"Se encontraron {len(recomendaciones)} recomendaciones",
            count=len(recomendaciones)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"Error al obtener recomendaciones: {str(e)}"
            )
        )


@router.get("/mi-cluster")
async def obtener_mi_cluster(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene el cluster al que pertenece el usuario actual
    Útil para debugging
    """
    try:
        cluster = recommendation_service.get_user_cluster(current_user, db)
        
        preferencia = current_user.preferencia
        
        return create_success_response(
            data={
                "usuario_id": current_user.idUsuario,
                "nombre": current_user.nombre,
                "cluster": cluster,
                "preferencias": {
                    "categorias": [pc.categoria.nombre for pc in preferencia.preferencia_categorias] if preferencia else [],
                    "lenguajes": [pl.lenguaje.nombre for pl in preferencia.preferencia_lenguajes] if preferencia else [],
                    "nivel": preferencia.nivel.nombre if preferencia and preferencia.nivel else None
                }
            },
            message="Cluster obtenido exitosamente"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"Error al obtener cluster: {str(e)}"
            )
        )
