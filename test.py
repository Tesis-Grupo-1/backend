from app.services import DetectionService

image_path = "modelo\\Pupa\\image_75.jpeg"  # Cambia esto por la ruta de tu imagen

gg = DetectionService.detect_plaga(image_path)

