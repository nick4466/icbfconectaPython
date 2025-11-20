from django.db import models
from core.models import Nino
from planeaciones.models import Planeacion
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

# ------------------------
# 💡 NUEVO: Seguimiento Diario
# ------------------------
class SeguimientoDiario(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='seguimientos_diarios')
    planeacion = models.ForeignKey(Planeacion, on_delete=models.CASCADE, related_name='seguimientos_diarios')
    fecha = models.DateField()

    # --- Opciones para los campos de selección ---
    PARTICIPACION_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
        ('no_aplica', 'No Aplica'),
    ]
    COMPORTAMIENTO_CHOICES = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('bajo', 'Bajo'),
        ('dificultad', 'Presentó Dificultad'),
    ]

    # Campos de seguimiento
    participacion = models.CharField(
        max_length=10, choices=PARTICIPACION_CHOICES,
        verbose_name="¿Cómo participó el niño/a en la actividad?",
    )
    comportamiento_logro = models.CharField(
        max_length=10, choices=COMPORTAMIENTO_CHOICES,
        verbose_name="Comportamiento, interés y nivel de logro",
    )
    observaciones = models.TextField(
        verbose_name="Observaciones del educador",
        blank=True, null=True
    )
    valoracion = models.PositiveSmallIntegerField(
        verbose_name="Valoración del día",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Calificación de 1 a 5 estrellas."
    )

    class Meta:
        verbose_name = "Seguimiento Diario"
        verbose_name_plural = "Seguimientos Diarios"
        unique_together = ('nino', 'fecha')
        ordering = ['-fecha', 'nino']
