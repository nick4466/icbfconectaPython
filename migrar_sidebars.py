#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para migrar automáticamente todos los templates de la sidebar vieja a la moderna.
"""

import os
import re

# Archivos a migrar
ARCHIVOS_MIGRAR = [
    'templates/admin/madres_form.html',
    'templates/admin/hogares_list.html',
    'templates/admin/reportes.html',
    'templates/admin/visitas/listar_visitas.html',
]

# Template de la sidebar moderna
SIDEBAR_MODERNA = '''  <!-- ========== SIDEBAR ========== -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <a href="{% url 'home' %}" class="sidebar-logo">
        <img src="{% static 'img/logoSinFondo.png' %}" alt="ICBF">
        <div class="sidebar-logo-text">
          <h2>ICBF Conecta</h2>
          <p>Panel Administrativo</p>
        </div>
      </a>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-item">
        <a href="{% url 'dashboard_admin' %}" class="nav-link">
          <i class="fas fa-tachometer-alt"></i>
          <span>Inicio</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'hogares_dashboard' %}" class="nav-link">
          <i class="fas fa-home"></i>
          <span>Dashboard Hogares</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'listar_hogares' %}" class="nav-link">
          <i class="fas fa-house-user"></i>
          <span>Gestionar Hogares</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'listar_madres' %}" class="nav-link">
          <i class="fas fa-user-group"></i>
          <span>Agentes Educativos</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'listar_administradores' %}" class="nav-link">
          <i class="fas fa-user-shield"></i>
          <span>Administradores</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'admin_reportes' %}" class="nav-link">
          <i class="fas fa-chart-line"></i>
          <span>Reportes</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'editar_perfil' %}" class="nav-link">
          <i class="fas fa-user-pen"></i>
          <span>Editar Perfil</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'cambiar_contrasena' %}" class="nav-link">
          <i class="fas fa-key"></i>
          <span>Cambiar Contraseña</span>
        </a>
      </div>
      <div class="nav-item">
        <a href="{% url 'logout' %}" class="nav-link">
          <i class="fas fa-sign-out-alt"></i>
          <span>Cerrar Sesión</span>
        </a>
      </div>
    </nav>
  </aside>'''

TOPBAR_MODERNA = '''  <!-- ========== MAIN CONTENT ========== -->
  <main class="main-content">
    <!-- TOPBAR -->
    <div class="topbar">
      <div class="topbar-left">
        <h1>TITULO_PAGINA</h1>
      </div>
      <div class="topbar-right">
        <div class="user-menu">
          <div class="user-avatar">
            {{ request.user.nombres.0 }}{{ request.user.apellidos.0 }}
          </div>
          <div>
            <div style="font-weight: 600; font-size: 14px;">{{ request.user.nombres }}</div>
            <div style="font-size: 12px; color: var(--text-light);">Administrador</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="content-wrapper">'''


def extraer_titulo(contenido):
    """Extrae el título de la página del HTML"""
    # Buscar en <header><h1>
    match = re.search(r'<header[^>]*>.*?<h1[^>]*>(.*?)</h1>', contenido, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Buscar en <title>
    match = re.search(r'<title>(.*?)</title>', contenido)
    if match:
        return match.group(1).strip()
    
    return "Panel Administrativo"


def migrar_archivo(ruta_archivo):
    """Migra un archivo de sidebar vieja a moderna"""
    print(f"\n{'='*60}")
    print(f"Migrando: {ruta_archivo}")
    print(f"{'='*60}")
    
    if not os.path.exists(ruta_archivo):
        print(f"❌ ERROR: Archivo no encontrado: {ruta_archivo}")
        return False
    
    # Leer contenido
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Extraer título
    titulo = extraer_titulo(contenido)
    print(f"📄 Título detectado: {titulo}")
    
    # 1. Reemplazar fuente Poppins por Inter
    if 'Poppins' in contenido:
        contenido = contenido.replace(
            'family=Poppins',
            'family=Inter'
        )
        contenido = contenido.replace(
            '"Poppins"',
            '"Inter"'
        )
        contenido = contenido.replace(
            "'Poppins'",
            "'Inter'"
        )
        print("✅ Fuente migrada: Poppins → Inter")
    
    # 2. Reemplazar sidebar vieja por moderna
    # Patrón flexible para encontrar sidebar vieja
    patron_sidebar_vieja = r'<div class="sidebar">.*?</div>\s*</div>\s*(?=<div class="main">|<main)'
    
    if re.search(patron_sidebar_vieja, contenido, re.DOTALL):
        contenido = re.sub(patron_sidebar_vieja, SIDEBAR_MODERNA + '\n\n', contenido, flags=re.DOTALL)
        print("✅ Sidebar HTML reemplazada")
    else:
        print("⚠️  No se encontró sidebar vieja con patrón estándar")
    
    # 3. Reemplazar <div class="main"> por estructura moderna
    patron_main = r'<div class="main">\s*<header>.*?</header>'
    
    topbar_con_titulo = TOPBAR_MODERNA.replace('TITULO_PAGINA', titulo)
    
    if re.search(patron_main, contenido, re.DOTALL):
        contenido = re.sub(patron_main, topbar_con_titulo, contenido, flags=re.DOTALL)
        print("✅ Main content y topbar actualizados")
    else:
        print("⚠️  No se encontró estructura main estándar")
    
    # 4. Cerrar tags correctamente al final
    # Buscar penúltimo </div> y reemplazar por </div></main>
    contenido = re.sub(
        r'(</div>\s*</div>)\s*</body>',
        r'    </div> <!-- fin content-wrapper -->\n  </main> <!-- fin main-content -->\n\n</body>',
        contenido
    )
    
    # 5. Actualizar CSS a variables modernas
    reemplazos_css = [
        (r'#004080', 'var(--primary)'),
        (r'#007bff', 'var(--primary-light)'),
        (r'#28a745', 'var(--success)'),
        (r'#dc3545', 'var(--danger)'),
        (r'#f3f6fa', 'var(--light)'),
        (r'#333', 'var(--text)'),
    ]
    
    for viejo, nuevo in reemplazos_css:
        if viejo in contenido:
            contenido = contenido.replace(viejo, nuevo)
    
    print("✅ Variables CSS actualizadas")
    
    # Guardar archivo
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Archivo guardado exitosamente")
    return True


def main():
    """Función principal"""
    print("\n" + "="*60)
    print(" MIGRACIÓN AUTOMÁTICA DE SIDEBARS")
    print(" De sidebar vieja a sidebar moderna")
    print("="*60)
    
    exitosos = 0
    fallidos = 0
    
    for archivo in ARCHIVOS_MIGRAR:
        try:
            if migrar_archivo(archivo):
                exitosos += 1
            else:
                fallidos += 1
        except Exception as e:
            print(f"❌ ERROR al migrar {archivo}: {str(e)}")
            fallidos += 1
    
    print("\n" + "="*60)
    print(" RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📊 Total: {exitosos + fallidos}")
    print("="*60)


if __name__ == '__main__':
    main()
