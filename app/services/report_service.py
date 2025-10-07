from typing import List, Optional
from fastapi import HTTPException, status
from app.models.report import Report
from app.models.detection import Detection
from app.models.field import Field
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate, ReportGenerateRequest
import google.generativeai as genai
from app.core import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
from datetime import datetime

# Configurar Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

class ReportService:
    
    @staticmethod
    async def create_report(user_id: int, report_data: ReportCreate) -> Report:
        """Crea un nuevo reporte"""
        # Verificar que el usuario existe
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que el campo existe y pertenece al usuario
        field = await Field.get_or_none(id=report_data.field_id, user_id=user_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo no encontrado"
            )
        
        # Verificar que la detección existe y pertenece al usuario
        detection = await Detection.get_or_none(id=report_data.detection_id, user_id=user_id)
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detección no encontrada"
            )
        
        # Crear reporte
        report = Report(
            title=report_data.title,
            content=report_data.content,
            user_id=user_id,
            field_id=report_data.field_id,
            detection_id=report_data.detection_id
        )
        await report.save()
        return report
    
    @staticmethod
    async def generate_ai_report(user_id: int, report_data: ReportGenerateRequest) -> Report:
        """Genera un reporte automático usando Gemini AI"""
        # Verificar que el usuario existe
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que el campo existe y pertenece al usuario
        field = await Field.get_or_none(id=report_data.field_id, user_id=user_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo no encontrado"
            )
        
        # Verificar que la detección existe y pertenece al usuario
        detection = await Detection.get_or_none(id_detection=report_data.detection_id, user_id=user_id)
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detección no encontrada"
            )
        
        # Generar contenido con Gemini AI
        ai_content = await ReportService._generate_ai_content(field, detection, report_data.additional_notes)
        
        # Crear reporte
        report = Report(
            title=report_data.title,
            user_id=user_id,
            field_id=report_data.field_id,
            detection_id=report_data.detection_id
        )

        report.content = "Reporte generado automáticamente por Gemini AI."
        report.ai_generated_content = ai_content

        await report.save()
        return report
    
    @staticmethod
    async def _generate_ai_content(field: Field, detection: Detection, additional_notes: Optional[str] = None) -> str:
        """Genera contenido del reporte usando Gemini AI"""
        prompt = f"""
        Genera un reporte técnico detallado sobre una detección de plagas en un campo agrícola con la siguiente información:

        INFORMACIÓN DEL CAMPO:
        - Nombre: {field.name}
        - Tamaño: {field.size_hectares} hectáreas
        - Ubicación: {field.location}
        - Descripción: {field.description or 'No disponible'}

        INFORMACIÓN DE LA DETECCIÓN:
        - Fecha: {detection.date_detection}
        - Hora de inicio: {detection.time_initial}
        - Hora de finalización: {detection.time_final}
        - Tipo de plaga detectada: {detection.result}
        - Valor de predicción: {detection.prediction_value}
        - Porcentaje del campo afectado: {detection.plague_percentage}%

        NOTAS ADICIONALES DEL USUARIO:
        {additional_notes or 'No hay notas adicionales'}

        El reporte debe incluir:
        1. Resumen ejecutivo
        2. Análisis de la situación actual
        3. Evaluación del impacto en el campo
        4. Recomendaciones técnicas
        5. Plan de acción sugerido
        6. Consideraciones de seguimiento

        Formato el reporte de manera profesional y técnica, adecuado para uso agrícola.
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content(prompt)
            print("Gemini AI response:", response.text)
            return response.text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar contenido con IA: {str(e)}"
            )
    
    @staticmethod
    async def export_report_to_pdf(report_id: int, user_id: int) -> str:
        """Exporta un reporte a PDF"""
        # Obtener reporte
        report = await Report.get_or_none(id=report_id, user_id=user_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Obtener información relacionada
        field = await Field.get_or_none(id=report.field_id)
        detection = await Detection.get_or_none(id=report.detection_id)
        
        # Crear directorio de reportes si no existe
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Generar nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_{report_id}_{timestamp}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Crear PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 20))
        
        # Información del campo
        story.append(Paragraph("INFORMACIÓN DEL CAMPO", styles['Heading2']))
        field_data = [
            ['Nombre del Campo:', field.name if field else 'N/A'],
            ['Tamaño (hectáreas):', str(field.size_hectares) if field else 'N/A'],
            ['Ubicación:', field.location if field else 'N/A'],
            ['Descripción:', field.description if field else 'N/A']
        ]
        field_table = Table(field_data, colWidths=[2*inch, 4*inch])
        field_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ]))
        story.append(field_table)
        story.append(Spacer(1, 20))
        
        # Información de la detección
        story.append(Paragraph("INFORMACIÓN DE LA DETECCIÓN", styles['Heading2']))
        detection_data = [
            ['Fecha:', str(detection.date_detection) if detection else 'N/A'],
            ['Hora de inicio:', str(detection.time_initial) if detection else 'N/A'],
            ['Hora de finalización:', str(detection.time_final) if detection else 'N/A'],
            ['Tipo de plaga:', detection.result if detection else 'N/A'],
            ['Valor de predicción:', detection.prediction_value if detection else 'N/A'],
            ['Porcentaje afectado:', f"{detection.plague_percentage}%" if detection else 'N/A']
        ]
        detection_table = Table(detection_data, colWidths=[2*inch, 4*inch])
        detection_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ]))
        story.append(detection_table)
        story.append(Spacer(1, 20))
        
        # Contenido del reporte
        story.append(Paragraph("CONTENIDO DEL REPORTE", styles['Heading2']))
        if report.ai_generated_content:
            # Dividir el contenido en párrafos
            paragraphs = report.ai_generated_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(report.content, styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        # Actualizar reporte con la ruta del PDF
        report.pdf_path = filepath
        await report.save()
        
        return filepath
    
    @staticmethod
    async def get_reports_by_user(user_id: int) -> List[Report]:
        """Obtiene todos los reportes de un usuario"""
        return await Report.filter(user_id=user_id)
    
    @staticmethod
    async def get_report_by_id(report_id: int, user_id: int) -> Optional[Report]:
        """Obtiene un reporte específico de un usuario"""
        return await Report.get_or_none(id=report_id, user_id=user_id)
    
    @staticmethod
    async def update_report(report_id: int, user_id: int, report_data: ReportUpdate) -> Report:
        """Actualiza un reporte"""
        report = await Report.get_or_none(id=report_id, user_id=user_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Actualizar campos
        for field_name, value in report_data.dict(exclude_unset=True).items():
            if hasattr(report, field_name):
                setattr(report, field_name, value)
        
        await report.save()
        return report
    
    @staticmethod
    async def delete_report(report_id: int, user_id: int) -> bool:
        """Elimina un reporte"""
        report = await Report.get_or_none(id=report_id, user_id=user_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Eliminar archivo PDF si existe
        if report.pdf_path and os.path.exists(report.pdf_path):
            os.remove(report.pdf_path)
        
        await report.delete()
        return True
