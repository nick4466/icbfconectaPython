from django.db import models
from core.models import Nino

class DesarrolloNino(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='desarrollos')
    fecha_fin_mes = models.DateField()
    
    # Dimensiones del desarrollo
    dimension_cognitiva = models.TextField(verbose_name="Dimensión Cognitiva")
    dimension_comunicativa = models.TextField(verbose_name="Dimensión Comunicativa")
    dimension_socio_afectiva = models.TextField(verbose_name="Dimensión Socio-afectiva")
    dimension_corporal = models.TextField(verbose_name="Dimensión Corporal")

    def __str__(self):
        return f"Desarrollo de {self.nino.nombres} para {self.fecha_fin_mes.strftime('%B %Y')}"

    class Meta:
        verbose_name = "Desarrollo del Niño"
        verbose_name_plural = "Desarrollos de los Niños"
        ordering = ['-fecha_fin_mes']
