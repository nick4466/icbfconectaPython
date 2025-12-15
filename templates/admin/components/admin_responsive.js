// ========== CONTROL DEL SIDEBAR RESPONSIVO ==========

/**
 * Inicializar evento de hamburger menu
 */
document.addEventListener('DOMContentLoaded', function() {
  const hamburgerBtn = document.querySelector('.hamburger-toggle');
  const sidebar = document.querySelector('.sidebar');
  const sidebarOverlay = document.querySelector('.sidebar-overlay');

  // Verificar si los elementos existen antes de continuar
  if (!hamburgerBtn || !sidebar) {
    console.log('Hamburger button o sidebar no encontrados');
    return;
  }

  // Evento para abrir/cerrar sidebar al hacer clic en hamburger
  hamburgerBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    toggleSidebar();
  });

  // Cerrar sidebar al hacer clic en el overlay
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', function() {
      closeSidebar();
    });
  }

  // Cerrar sidebar cuando se hace clic en un link de navegación
  const navLinks = sidebar.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      // Esperar a que se complete la navegación antes de cerrar
      setTimeout(() => {
        closeSidebar();
      }, 100);
    });
  });

  // Cerrar sidebar al presionar ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeSidebar();
    }
  });

  // Manejar resize del window para asegurar estado correcto
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      if (window.innerWidth > 768) {
        // En pantallas grandes, asegurar que el sidebar esté visible
        sidebar.classList.remove('active');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
      }
    }, 250);
  });
});

/**
 * Alternar estado del sidebar
 */
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebar) {
    sidebar.classList.toggle('active');
  }

  if (overlay) {
    overlay.classList.toggle('active');
  }
}

/**
 * Abrir sidebar
 */
function openSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebar) {
    sidebar.classList.add('active');
  }

  if (overlay) {
    overlay.classList.add('active');
  }
}

/**
 * Cerrar sidebar
 */
function closeSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebar) {
    sidebar.classList.remove('active');
  }

  if (overlay) {
    overlay.classList.remove('active');
  }
}

// Exportar funciones si se usa como módulo
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { toggleSidebar, openSidebar, closeSidebar };
}
