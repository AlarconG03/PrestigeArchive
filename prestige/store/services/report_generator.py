from abc import ABC, abstractmethod
from django.http import HttpResponse
from reportlab.pdfgen import canvas

class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, data):
        """Genera y devuelve una respuesta HTTP con el reporte."""
        pass

class PDFReportGenerator(ReportGenerator):
    def generate(self, data):
        # Configuración de la respuesta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'

        # Crear el lienzo de ReportLab
        p = canvas.Canvas(response)
        p.setTitle("Reporte de Productos")

        # Título del reporte
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Reporte de Productos Disponibles")

        # Encabezados de tabla
        p.setFont("Helvetica-Bold", 12)
        y = 770
        p.drawString(50, y, "ID")
        p.drawString(100, y, "Nombre")
        p.drawString(300, y, "Precio (€)")
        p.drawString(380, y, "Stock")
        y -= 20

        # Contenido
        p.setFont("Helvetica", 12)
        for producto in data:
            p.drawString(50, y, str(producto.product_id))
            p.drawString(100, y, producto.name[:30])  # recortar si es muy largo
            p.drawString(300, y, f"{producto.price}")
            p.drawString(380, y, str(producto.stock))
            y -= 20

            # Salto de página si es necesario
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 12)

        # Finalizar y enviar
        p.showPage()
        p.save()
        return response