"""
Comando de gestión Django para limpieza automática de archivos basura.

Limpia:
- Archivos de solicitudes no terminadas (pendientes sin editar en X días)
- Archivos de solicitudes expiradas
- Archivos de solicitudes rechazadas hace X días
- Archivos huérfanos (sin solicitud asociada)

Uso:
    python manage.py limpiar_archivos_solicitudes
    python manage.py limpiar_archivos_solicitudes --dry-run  # Simular sin borrar
    python manage.py limpiar_archivos_solicitudes --dias-rechazadas 60
"""

import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from core.models import SolicitudMatriculacion


class Command(BaseCommand):
    help = 'Limpia archivos basura de solicitudes expiradas, rechazadas y no terminadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la limpieza sin borrar archivos realmente',
        )
        parser.add_argument(
            '--dias-rechazadas',
            type=int,
            default=30,
            help='Días después de rechazo para eliminar archivos (default: 30)',
        )
        parser.add_argument(
            '--dias-sin-editar',
            type=int,
            default=15,
            help='Días sin editar para considerar solicitud abandonada (default: 15)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dias_rechazadas = options['dias_rechazadas']
        dias_sin_editar = options['dias_sin_editar']

        self.stdout.write(self.style.WARNING(
            f'\n{"=" * 70}\n'
            f'  LIMPIEZA DE ARCHIVOS BASURA - SOLICITUDES\n'
            f'{"=" * 70}\n'
        ))

        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 MODO SIMULACIÓN - No se borrarán archivos\n'))

        total_archivos_eliminados = 0
        total_espacio_liberado = 0

        # 1. Limpiar solicitudes expiradas
        archivos, espacio = self._limpiar_solicitudes_expiradas(dry_run)
        total_archivos_eliminados += archivos
        total_espacio_liberado += espacio

        # 2. Limpiar solicitudes rechazadas antiguas
        archivos, espacio = self._limpiar_solicitudes_rechazadas(dry_run, dias_rechazadas)
        total_archivos_eliminados += archivos
        total_espacio_liberado += espacio

        # 3. Limpiar solicitudes abandonadas (pendientes sin editar)
        archivos, espacio = self._limpiar_solicitudes_abandonadas(dry_run, dias_sin_editar)
        total_archivos_eliminados += archivos
        total_espacio_liberado += espacio

        # 4. Limpiar archivos huérfanos
        archivos, espacio = self._limpiar_archivos_huerfanos(dry_run)
        total_archivos_eliminados += archivos
        total_espacio_liberado += espacio

        # Resumen final
        self.stdout.write(self.style.SUCCESS(
            f'\n{"=" * 70}\n'
            f'  RESUMEN DE LIMPIEZA\n'
            f'{"=" * 70}\n'
            f'  📁 Total archivos eliminados: {total_archivos_eliminados}\n'
            f'  💾 Espacio liberado: {self._formatear_bytes(total_espacio_liberado)}\n'
            f'{"=" * 70}\n'
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '⚠️  Esto fue una simulación. Ejecuta sin --dry-run para borrar realmente.\n'
            ))

    def _limpiar_solicitudes_expiradas(self, dry_run):
        """Limpia archivos de solicitudes expiradas o canceladas por expiración"""
        self.stdout.write(self.style.HTTP_INFO('\n🕐 Buscando solicitudes expiradas/canceladas...'))
        
        ahora = timezone.now()
        solicitudes_expiradas = SolicitudMatriculacion.objects.filter(
            estado__in=['cancelado_expiracion']  # Canceladas automáticamente por expiración
        )

        count = solicitudes_expiradas.count()
        self.stdout.write(f'   Encontradas: {count} solicitudes canceladas por expiración')

        archivos_eliminados = 0
        espacio_liberado = 0

        for solicitud in solicitudes_expiradas:
            archivos, espacio = self._eliminar_archivos_solicitud(solicitud, dry_run)
            archivos_eliminados += archivos
            espacio_liberado += espacio

        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {archivos_eliminados} archivos eliminados '
            f'({self._formatear_bytes(espacio_liberado)})'
        ))

        return archivos_eliminados, espacio_liberado

    def _limpiar_solicitudes_rechazadas(self, dry_run, dias_rechazadas):
        """Limpia archivos de solicitudes rechazadas hace X días"""
        self.stdout.write(self.style.HTTP_INFO(
            f'\n❌ Buscando solicitudes rechazadas hace más de {dias_rechazadas} días...'
        ))
        
        fecha_limite = timezone.now() - timedelta(days=dias_rechazadas)
        solicitudes_rechazadas = SolicitudMatriculacion.objects.filter(
            estado='rechazado',
            fecha_creacion__lt=fecha_limite
        )

        count = solicitudes_rechazadas.count()
        self.stdout.write(f'   Encontradas: {count} solicitudes rechazadas antiguas')

        archivos_eliminados = 0
        espacio_liberado = 0

        for solicitud in solicitudes_rechazadas:
            archivos, espacio = self._eliminar_archivos_solicitud(solicitud, dry_run)
            archivos_eliminados += archivos
            espacio_liberado += espacio

        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {archivos_eliminados} archivos eliminados '
            f'({self._formatear_bytes(espacio_liberado)})'
        ))

        return archivos_eliminados, espacio_liberado

    def _limpiar_solicitudes_abandonadas(self, dry_run, dias_sin_editar):
        """Limpia archivos de solicitudes pendientes sin editar en X días"""
        self.stdout.write(self.style.HTTP_INFO(
            f'\n⏱️  Buscando solicitudes abandonadas (sin editar en {dias_sin_editar} días)...'
        ))
        
        fecha_limite = timezone.now() - timedelta(days=dias_sin_editar)
        
        # Solicitudes pendientes sin completar información básica
        solicitudes_abandonadas = SolicitudMatriculacion.objects.filter(
            estado='pendiente',
            fecha_creacion__lt=fecha_limite,
            nombres_nino__isnull=True  # Sin datos del niño = no empezó a llenar
        )

        count = solicitudes_abandonadas.count()
        self.stdout.write(f'   Encontradas: {count} solicitudes abandonadas')

        archivos_eliminados = 0
        espacio_liberado = 0

        for solicitud in solicitudes_abandonadas:
            archivos, espacio = self._eliminar_archivos_solicitud(solicitud, dry_run)
            archivos_eliminados += archivos
            espacio_liberado += espacio

        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {archivos_eliminados} archivos eliminados '
            f'({self._formatear_bytes(espacio_liberado)})'
        ))

        return archivos_eliminados, espacio_liberado

    def _limpiar_archivos_huerfanos(self, dry_run):
        """Limpia archivos en /solicitudes/ sin solicitud asociada"""
        self.stdout.write(self.style.HTTP_INFO('\n🔍 Buscando archivos huérfanos...'))
        
        solicitudes_dir = os.path.join(settings.MEDIA_ROOT, 'solicitudes')
        
        if not os.path.exists(solicitudes_dir):
            self.stdout.write('   No existe el directorio de solicitudes')
            return 0, 0

        archivos_eliminados = 0
        espacio_liberado = 0

        # Obtener todos los archivos de solicitudes existentes en BD
        archivos_bd = set()
        for solicitud in SolicitudMatriculacion.objects.all():
            for campo in self._get_campos_archivo():
                archivo = getattr(solicitud, campo, None)
                if archivo and archivo.name:
                    archivos_bd.add(os.path.join(settings.MEDIA_ROOT, archivo.name))

        # Recorrer archivos en disco y comparar
        for root, dirs, files in os.walk(solicitudes_dir):
            for file in files:
                filepath = os.path.join(root, file)
                
                if filepath not in archivos_bd:
                    try:
                        tamanio = os.path.getsize(filepath)
                        
                        if not dry_run:
                            os.remove(filepath)
                        
                        archivos_eliminados += 1
                        espacio_liberado += tamanio
                        
                        self.stdout.write(self.style.WARNING(
                            f'   🗑️  Huérfano: {os.path.relpath(filepath, settings.MEDIA_ROOT)}'
                        ))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'   ❌ Error al eliminar {filepath}: {e}'
                        ))

        # Eliminar carpetas vacías
        if not dry_run:
            self._eliminar_carpetas_vacias(solicitudes_dir)

        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {archivos_eliminados} archivos huérfanos eliminados '
            f'({self._formatear_bytes(espacio_liberado)})'
        ))

        return archivos_eliminados, espacio_liberado

    def _eliminar_archivos_solicitud(self, solicitud, dry_run):
        """Elimina todos los archivos asociados a una solicitud"""
        archivos_eliminados = 0
        espacio_liberado = 0

        campos_archivo = self._get_campos_archivo()

        for campo in campos_archivo:
            archivo = getattr(solicitud, campo, None)
            
            if archivo and archivo.name:
                try:
                    filepath = archivo.path
                    
                    if os.path.exists(filepath):
                        tamanio = os.path.getsize(filepath)
                        
                        if not dry_run:
                            os.remove(filepath)
                        
                        archivos_eliminados += 1
                        espacio_liberado += tamanio
                        
                        self.stdout.write(
                            f'   🗑️  [{solicitud.id}] {campo}: {os.path.basename(filepath)}'
                        )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'   ❌ Error al eliminar {campo} de solicitud {solicitud.id}: {e}'
                    ))

        return archivos_eliminados, espacio_liberado

    def _get_campos_archivo(self):
        """Retorna lista de campos FileField en SolicitudMatriculacion"""
        return [
            'foto_nino',
            'carnet_vacunacion_nino',
            'certificado_eps_nino',
            'registro_civil_nino',
            'documento_identidad_padre',
            'clasificacion_sisben_padre',
        ]

    def _eliminar_carpetas_vacias(self, directorio):
        """Elimina carpetas vacías recursivamente"""
        for root, dirs, files in os.walk(directorio, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Si está vacía
                        os.rmdir(dir_path)
                        self.stdout.write(f'   📁 Carpeta vacía eliminada: {dir_path}')
                except Exception:
                    pass

    def _formatear_bytes(self, bytes):
        """Formatea bytes a KB, MB, GB"""
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f'{bytes:.2f} {unidad}'
            bytes /= 1024.0
        return f'{bytes:.2f} TB'
