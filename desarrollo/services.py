import calendar
from collections import Counter
from datetime import timedelta

from django.db.models import Avg

from .models import DesarrolloNino, SeguimientoDiario
from core.models import Asistencia
from novedades.models import Novedad


class GeneradorEvaluacionMensual:
    """
    Servicio para generar automáticamente el informe de desarrollo mensual de un niño.
    """

    def __init__(self, evaluacion_instance: DesarrolloNino):
        self.evaluacion = evaluacion_instance
        self.nino = self.evaluacion.nino
        self.fecha_fin_mes = self.evaluacion.fecha_fin_mes
        self.fecha_inicio_mes = self.fecha_fin_mes.replace(day=1)

        # Obtenemos los datos del mes una sola vez
        self.seguimientos_mes = self._get_seguimientos()
        self.novedades_mes = self._get_novedades()

    def run(self, only_tendencia=False, save_instance=True):
        """
        Ejecuta todos los pasos para generar y guardar la evaluación.
        Si only_tendencia=True, solo recalcula la tendencia respecto al mes anterior.
        Si save_instance=False, solo ejecuta la lógica pero no guarda el objeto.
        """
        if only_tendencia:
            self._generar_valoracion_general(only_asistencia=True)  # Solo asistencia
            if save_instance:
                self.evaluacion.save(run_generator=False) # Guardar sin volver a llamar al generador
            return
        self._generar_valoracion_general()
        self._generar_evaluacion_por_areas()
        self._generar_fortalezas()
        self._generar_aspectos_a_mejorar()
        self._generar_alertas()
        self._generar_conclusion_general()
        if save_instance:
            self.evaluacion.save(run_generator=False) # Guardar sin volver a llamar al generador

    def _get_seguimientos(self):
        return SeguimientoDiario.objects.filter(
            nino=self.nino,
            fecha__gte=self.fecha_inicio_mes,
            fecha__lte=self.fecha_fin_mes
        )

    def _get_novedades(self):
        return Novedad.objects.filter(
            nino=self.nino,
            fecha__gte=self.fecha_inicio_mes,
            fecha__lte=self.fecha_fin_mes
        )

    def _get_asistencias(self):
        return Asistencia.objects.filter(
            nino=self.nino,
            fecha__gte=self.fecha_inicio_mes,
            fecha__lte=self.fecha_fin_mes
        )

    def _generar_valoracion_general(self, only_asistencia=False):
        if not self.seguimientos_mes.exists():
            return

        # 1. Logro del Mes (Cualitativo)
        valoraciones = self.seguimientos_mes.values_list('valoracion', flat=True)
        if valoraciones:
            conteo = Counter(valoraciones)
            # Agrupar valoraciones por categoría
            alto = conteo[5] + conteo[4]
            adecuado = conteo[3]
            en_proceso = conteo[2] + conteo[1]
            
            # Determinar la categoría dominante
            categorias = {'Alto': alto, 'Adecuado': adecuado, 'En Proceso': en_proceso}
            logro_dominante = max(categorias, key=categorias.get)
            self.evaluacion.logro_mes = logro_dominante

        # 2. Tendencia
        mes_anterior_fin = self.fecha_inicio_mes - timedelta(days=1)
        try:
            evaluacion_anterior = DesarrolloNino.objects.get(
                nino=self.nino,
                fecha_fin_mes__year=mes_anterior_fin.year,
                fecha_fin_mes__month=mes_anterior_fin.month
            )
            if evaluacion_anterior.logro_mes and self.evaluacion.logro_mes:
                # Mapeo de logros a un valor numérico para comparación
                orden_logros = {'Alto': 3, 'Adecuado': 2, 'En Proceso': 1}
                logro_actual_val = orden_logros.get(self.evaluacion.logro_mes, 0)
                logro_anterior_val = orden_logros.get(evaluacion_anterior.logro_mes, 0)

                if logro_actual_val > logro_anterior_val:
                    self.evaluacion.tendencia_valoracion = 'Avanza'
                elif logro_actual_val < logro_anterior_val:
                    self.evaluacion.tendencia_valoracion = 'Retrocede'
                else:
                    self.evaluacion.tendencia_valoracion = 'Se Mantiene'
            else:
                self.evaluacion.tendencia_valoracion = 'Se Mantiene'
        except DesarrolloNino.DoesNotExist:
            self.evaluacion.tendencia_valoracion = 'Sin datos previos'

        # 3. Participación y Comportamiento más frecuentes
        participaciones = self.seguimientos_mes.values_list('participacion', flat=True)
        if participaciones:
            self.evaluacion.participacion_frecuente = Counter(participaciones).most_common(1)[0][0]

        comportamientos = self.seguimientos_mes.values_list('comportamiento_logro', flat=True)
        if comportamientos:
            self.evaluacion.comportamiento_frecuente = Counter(comportamientos).most_common(1)[0][0]

        # 4. Porcentaje de Asistencia
        asistencias_mes = self._get_asistencias()
        total_dias_registrados = asistencias_mes.count()
        dias_presente = asistencias_mes.filter(estado='Presente').count()

        if total_dias_registrados > 0:
            porcentaje = round((dias_presente / total_dias_registrados) * 100)
            self.evaluacion.porcentaje_asistencia = porcentaje
        else:
            # Si no hay registros de asistencia, no se puede calcular.
            self.evaluacion.porcentaje_asistencia = None

        if only_asistencia:
            return

    def _generar_evaluacion_por_areas(self):
        # Esta es una implementación simplificada. Se puede expandir con análisis de texto más avanzado.
        if not self.seguimientos_mes.exists():
            self.evaluacion.evaluacion_cognitiva = "No hay suficientes datos para una evaluación."
            # ... y así para las demás áreas
            return

        logro = self.evaluacion.logro_mes
        
        # Mapeo simple de palabras clave a dimensiones
        palabras_clave = {
            'evaluacion_cognitiva': ['aprende', 'resuelve', 'entiende', 'curioso', 'concentra', 'idea'],
            'evaluacion_comunicativa': ['habla', 'expresa', 'cuenta', 'pregunta', 'dialoga', 'canta'],
            'evaluacion_socio_afectiva': ['comparte', 'amigos', 'ayuda', 'juega con', 'emociones', 'ríe', 'llora'],
            'evaluacion_corporal': ['corre', 'salta', 'baila', 'dibuja', 'arma', 'equilibrio'],
            'evaluacion_autonomia': ['solo', 'independiente', 'come', 'viste', 'guarda', 'control'],
        }

        observaciones_texto = " ".join(s.observaciones for s in self.seguimientos_mes if s.observaciones and s.observacion_relevante)

        for area, keywords in palabras_clave.items():
            texto_area = self._crear_texto_area(area, logro, observaciones_texto, keywords)
            setattr(self.evaluacion, area, texto_area)

    def _crear_texto_area(self, nombre_area, logro, observaciones, keywords):
        # Genera un texto descriptivo para un área de desarrollo
        if logro == 'Alto':
            desempeno = "un desempeño destacado, mostrando avances significativos"
        elif logro == 'Adecuado':
            desempeno = "un progreso adecuado y constante"
        else:
            desempeno = "algunas dificultades y requiere apoyo adicional"

        palabras_encontradas = [kw for kw in keywords if kw in observaciones.lower()]
        
        texto = f"En el área {nombre_area.replace('evaluacion_', '').replace('_', ' ')}, el niño/a ha mostrado {desempeno}."
        if self.evaluacion.participacion_frecuente:
            texto += f" Su participación general fue '{self.evaluacion.get_participacion_frecuente_display()}'."
        if palabras_encontradas:
            texto += f" En las observaciones se aprecian actividades relacionadas con: {', '.join(palabras_encontradas)}."
        
        return texto

    def _generar_fortalezas(self):
        fortalezas = []
        if not self.seguimientos_mes.exists():
            self.evaluacion.fortalezas_mes = "No hay datos para identificar fortalezas."
            return

        if self.evaluacion.logro_mes == 'Alto':
            fortalezas.append("Valoraciones generales consistentemente altas durante el mes.")
        
        if self.evaluacion.participacion_frecuente in ['alta', 'media']:
            fortalezas.append(f"Participación activa y frecuente en las actividades ('{self.evaluacion.get_participacion_frecuente_display()}').")

        if self.evaluacion.comportamiento_frecuente in ['excelente', 'bueno']:
            fortalezas.append(f"Demostración de comportamiento positivo ('{self.evaluacion.get_comportamiento_frecuente_display()}').")

        novedades_alta_prioridad = [n for n in self.novedades_mes if n.get_prioridad() >= 4]
        if not novedades_alta_prioridad:
            fortalezas.append("Ausencia de novedades de alta prioridad, indicando un mes estable.")

        self.evaluacion.fortalezas_mes = "- " + "\n- ".join(fortalezas) if fortalezas else "Se requiere más observación para definir fortalezas claras."

    def _generar_aspectos_a_mejorar(self):
        aspectos = []
        if not self.seguimientos_mes.exists():
            self.evaluacion.aspectos_a_mejorar = "No hay datos para identificar aspectos a mejorar."
            return

        valoraciones_bajas = self.seguimientos_mes.filter(valoracion__lte=2).count()
        if valoraciones_bajas > 2:
            aspectos.append(f"Se registraron {valoraciones_bajas} días con valoraciones bajas, indicando la necesidad de observar qué sucedió en esas fechas.")

        if self.evaluacion.participacion_frecuente == 'baja':
            aspectos.append("La participación general en actividades fue baja. Es importante motivar una mayor integración.")

        if self.evaluacion.comportamiento_frecuente in ['dificultad', 'bajo']:
            aspectos.append("Se observaron comportamientos de 'dificultad' de manera recurrente.")

        novedades_asistencia = self.novedades_mes.filter(tipo='c').count()
        if novedades_asistencia > 2:
            aspectos.append(f"Se registraron {novedades_asistencia} novedades por inasistencia, lo cual puede afectar su proceso.")

        # Nuevo: Aspecto a mejorar si la tendencia es de retroceso
        if self.evaluacion.tendencia_valoracion == 'Retrocede':
            aspectos.append("Se observa un retroceso en el logro general en comparación con el mes anterior. Es importante identificar las causas.")

        self.evaluacion.aspectos_a_mejorar = "- " + "\n- ".join(aspectos) if aspectos else "No se identificaron aspectos críticos a mejorar este mes."

    def _generar_alertas(self):
        alertas = []
        
        # Alerta: Múltiples novedades del mismo tipo
        tipos_novedades = Counter(n.get_tipo_display() for n in self.novedades_mes)
        for tipo, count in tipos_novedades.items():
            if count >= 3:
                alertas.append(f"Alerta: Se registraron {count} novedades del tipo '{tipo}'. Se recomienda analizar la recurrencia.")

        # Alerta: Valoraciones muy bajas consecutivas o frecuentes
        valoraciones_muy_bajas = self.seguimientos_mes.filter(valoracion=1).count()
        if valoraciones_muy_bajas >= 3:
            alertas.append(f"Alerta: El niño/a tuvo {valoraciones_muy_bajas} días con la valoración más baja (1 estrella).")

        # Alerta: Tendencia de retroceso
        if self.evaluacion.tendencia_valoracion == 'Retrocede':
            alertas.append("Alerta de Retroceso: El desempeño general del niño ha disminuido en comparación con el mes anterior.")

        # Alerta: Inasistencias
        inasistencias = self.novedades_mes.filter(tipo='c').count()
        if inasistencias > 3:
             alertas.append(f"Alerta: Se registraron {inasistencias} inasistencias este mes.")

        # Alerta: Novedades de salud o emoción de prioridad alta
        novedades_criticas = [n for n in self.novedades_mes if n.tipo in ['a', 'b'] and n.get_prioridad() >= 4]
        if novedades_criticas:
            alertas.append(f"Alerta: Se registraron {len(novedades_criticas)} novedades críticas de salud o estado emocional.")

        self.evaluacion.alertas_mes = "- " + "\n- ".join(alertas) if alertas else "No se generaron alertas automáticas este mes."

    def _generar_conclusion_general(self):
        if not self.seguimientos_mes.exists():
            self.evaluacion.conclusion_general = "No es posible generar una conclusión debido a la falta de seguimientos diarios este mes."
            return

        logro = self.evaluacion.logro_mes
        
        if logro == 'Alto' and not self.evaluacion.aspectos_a_mejorar.startswith("-"):
            estado = "cumplió con los objetivos esperados para el mes, mostrando un desarrollo sobresaliente."
            recomendacion = "Se recomienda continuar estimulando sus habilidades y curiosidad."
        elif logro == 'Adecuado':
            estado = "se encuentra en proceso, mostrando un progreso constante y adecuado."
            recomendacion = "Se recomienda reforzar las áreas donde se identificaron oportunidades de mejora y mantener la motivación."
        else:
            estado = "necesita apoyo adicional para alcanzar los objetivos de desarrollo."
            recomendacion = "Es crucial enfocarse en los 'aspectos por mejorar' y trabajar en conjunto con la familia para crear un plan de acción."

        mes_nombre = calendar.month_name[self.fecha_fin_mes.month].capitalize()
        conclusion = f"Durante el mes de {mes_nombre}, el niño/a {estado} {recomendacion}"
        self.evaluacion.conclusion_general = conclusion
