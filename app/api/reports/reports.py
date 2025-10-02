from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import List
from app.services.report_service import ReportService
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse, ReportGenerateRequest
from app.models.user import User
from app.api.auth.auth import get_current_active_user, get_boss_user
import os

router = APIRouter()

@router.post("/", response_model=ReportResponse,
             summary="Crear reporte manual",
             description="Crea un nuevo reporte manual con contenido proporcionado por el usuario.",
             responses={
                 201: {"description": "Reporte creado exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 404: {"description": "Campo o detección no encontrados"},
                 422: {"description": "Datos de entrada inválidos"}
             })
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea un nuevo reporte manual con contenido proporcionado por el usuario.
    
    - **title**: Título del reporte (requerido)
    - **content**: Contenido del reporte (requerido)
    - **field_id**: ID del campo relacionado (requerido)
    - **detection_id**: ID de la detección relacionada (requerido)
    """
    report = await ReportService.create_report(current_user.id, report_data)
    return ReportResponse.from_orm(report)

@router.post("/generate-ai", response_model=ReportResponse,
             summary="Generar reporte con IA",
             description="Genera un reporte automático usando Gemini AI basado en datos de detección.",
             responses={
                 201: {"description": "Reporte generado exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 404: {"description": "Campo o detección no encontrados"},
                 422: {"description": "Datos de entrada inválidos"},
                 500: {"description": "Error al generar contenido con IA"}
             })
async def generate_ai_report(
    report_data: ReportGenerateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera un reporte automático usando Gemini AI.
    
    La IA analiza los datos de la detección y genera un reporte técnico que incluye:
    - Resumen ejecutivo
    - Análisis de la situación actual
    - Evaluación del impacto en el campo
    - Recomendaciones técnicas
    - Plan de acción sugerido
    - Consideraciones de seguimiento
    
    - **title**: Título del reporte (requerido)
    - **field_id**: ID del campo relacionado (requerido)
    - **detection_id**: ID de la detección relacionada (requerido)
    - **additional_notes**: Notas adicionales opcionales para la IA
    """
    report = await ReportService.generate_ai_report(current_user.id, report_data)
    return ReportResponse.from_orm(report)

@router.get("/", response_model=List[ReportResponse],
            summary="Listar reportes del usuario",
            description="Obtiene todos los reportes del usuario autenticado.",
            responses={
                200: {"description": "Lista de reportes obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"}
            })
async def get_reports(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene todos los reportes del usuario autenticado.
    
    Retorna una lista con todos los reportes creados por el usuario.
    """
    reports = await ReportService.get_reports_by_user(current_user.id)
    return [ReportResponse.from_orm(report) for report in reports]

@router.get("/{report_id}", response_model=ReportResponse,
            summary="Obtener reporte específico",
            description="Obtiene la información de un reporte específico del usuario autenticado.",
            responses={
                200: {"description": "Reporte obtenido exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Reporte no encontrado"}
            })
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información de un reporte específico.
    
    - **report_id**: ID del reporte a obtener
    """
    report = await ReportService.get_report_by_id(report_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado"
        )
    return ReportResponse.from_orm(report)

@router.put("/{report_id}", response_model=ReportResponse,
            summary="Actualizar reporte",
            description="Actualiza la información de un reporte existente.",
            responses={
                200: {"description": "Reporte actualizado exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Reporte no encontrado"},
                422: {"description": "Datos de entrada inválidos"}
            })
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza la información de un reporte existente.
    
    - **report_id**: ID del reporte a actualizar
    - Todos los campos son opcionales en la actualización
    """
    report = await ReportService.update_report(report_id, current_user.id, report_data)
    return ReportResponse.from_orm(report)

@router.delete("/{report_id}",
               summary="Eliminar reporte",
               description="Elimina un reporte del usuario autenticado.",
               responses={
                   200: {"description": "Reporte eliminado exitosamente"},
                   401: {"description": "Token JWT inválido o expirado"},
                   404: {"description": "Reporte no encontrado"}
               })
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un reporte del usuario autenticado.
    
    - **report_id**: ID del reporte a eliminar
    
    ⚠️ **Advertencia**: Esta acción no se puede deshacer y eliminará también el archivo PDF asociado.
    """
    success = await ReportService.delete_report(report_id, current_user.id)
    return {"message": "Reporte eliminado exitosamente"}

@router.post("/{report_id}/export-pdf",
             summary="Exportar reporte a PDF",
             description="Genera y descarga un archivo PDF del reporte especificado.",
             responses={
                 200: {"description": "PDF generado y descargado exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 404: {"description": "Reporte no encontrado o PDF no disponible"},
                 500: {"description": "Error al generar el PDF"}
             })
async def export_report_to_pdf(
    report_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera y descarga un archivo PDF del reporte especificado.
    
    El PDF incluye:
    - Información del campo
    - Datos de la detección
    - Contenido del reporte (manual o generado por IA)
    - Formato profesional para uso agrícola
    
    - **report_id**: ID del reporte a exportar
    """
    filepath = await ReportService.export_report_to_pdf(report_id, current_user.id)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo PDF no encontrado"
        )
    
    return FileResponse(
        path=filepath,
        media_type='application/pdf',
        filename=f"reporte_{report_id}.pdf"
    )

@router.get("/boss/employees", response_model=List[ReportResponse],
            summary="Listar reportes de empleados",
            description="Obtiene todos los reportes de los empleados vinculados al jefe autenticado.",
            responses={
                200: {"description": "Lista de reportes de empleados obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo jefes pueden usar este endpoint"}
            })
async def get_employee_reports(current_user: User = Depends(get_boss_user)):
    """
    Obtiene todos los reportes de los empleados vinculados al jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    Los jefes pueden ver los reportes de sus empleados pero no modificarlos.
    """
    # Obtener empleados del jefe
    from app.services.auth_service import AuthService
    employees = await AuthService.get_employees_by_boss(current_user.id)
    employee_ids = [emp.id for emp in employees]
    
    # Obtener reportes de los empleados
    all_reports = []
    for emp_id in employee_ids:
        reports = await ReportService.get_reports_by_user(emp_id)
        all_reports.extend(reports)
    
    return [ReportResponse.from_orm(report) for report in all_reports]
