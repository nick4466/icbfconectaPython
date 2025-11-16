from django.db import models
from core.models import Nino
from django.core.validators import MinValueValidator, MaxValueValidator

class DesarrolloNino(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='desarrollos')
    fecha_fin_mes = models.DateField()
    
    # --- Calificaciones con Estrellas ---
    rating_cognitiva = models.PositiveSmallIntegerField(
        verbose_name="Rating Dimensión Cognitiva",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    rating_comunicativa = models.PositiveSmallIntegerField(
        verbose_name="Rating Dimensión Comunicativa",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    rating_socio_afectiva = models.PositiveSmallIntegerField(
        verbose_name="Rating Dimensión Socio-afectiva",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    rating_corporal = models.PositiveSmallIntegerField(
        verbose_name="Rating Dimensión Corporal",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )

    # Dimensiones del desarrollo
    dimension_cognitiva = models.TextField(verbose_name="Dimensión Cognitiva", null=True, blank=True)
    dimension_comunicativa = models.TextField(verbose_name="Dimensión Comunicativa", null=True, blank=True)
    dimension_socio_afectiva = models.TextField(verbose_name="Dimensión Socio-afectiva", null=True, blank=True)
    dimension_corporal = models.TextField(verbose_name="Dimensión Corporal", null=True, blank=True)

    def __str__(self):
        return f"Desarrollo de {self.nino.nombres} para {self.fecha_fin_mes.strftime('%B %Y')}"

    class Meta:
        verbose_name = "Desarrollo del Niño"
        verbose_name_plural = "Desarrollos de los Niños"
        ordering = ['-fecha_fin_mes']
