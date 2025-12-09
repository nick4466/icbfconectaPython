/**
 * 🆕 GEOGRAFÍA DE COLOMBIA - Cascada Dinámica
 * ============================================
 * Script para cargar dinámicamente:
 * - Municipios según departamento seleccionado
 * - Localidades de Bogotá si se selecciona Bogotá D.C.
 * 
 * Uso:
 * 1. Incluir este script en el template
 * 2. Llamar initGeografiaColombia() cuando el DOM esté listo
 * 3. Los select deben tener los IDs específicos o pasar selectores personalizados
 */

/**
 * Inicializa la cascada geográfica para un conjunto de campos
 * @param {Object} config - Configuración de selectores
 * @param {string} config.departamentoSelector - Selector del select de departamento (default: '#id_departamento_residencia')
 * @param {string} config.municipioSelector - Selector del select de municipio (default: '#id_ciudad_residencia')
 * @param {string} config.localidadSelector - Selector del select de localidad (default: '#id_localidad_bogota')
 * @param {string} config.localidadContainer - Selector del contenedor de localidad (default: '.localidad-container')
 */
function initGeografiaColombia(config = {}) {
    // Configuración por defecto
    const defaults = {
        departamentoSelector: '#id_departamento_residencia',
        municipioSelector: '#id_ciudad_residencia',
        localidadSelector: '#id_localidad_bogota',
        localidadContainer: '.localidad-container',
    };
    
    const settings = { ...defaults, ...config };
    
    const departamentoSelect = document.querySelector(settings.departamentoSelector);
    const municipioSelect = document.querySelector(settings.municipioSelector);
    const localidadSelect = document.querySelector(settings.localidadSelector);
    const localidadContainer = document.querySelector(settings.localidadContainer);
    
    if (!departamentoSelect || !municipioSelect) {
        console.warn('Geografia Colombia: No se encontraron los selectores de departamento o municipio');
        return;
    }
    
    // ========================================
    // CARGAR MUNICIPIOS AL CAMBIAR DEPARTAMENTO
    // ========================================
    departamentoSelect.addEventListener('change', function() {
        const departamentoId = this.value;
        
        // Limpiar municipio y localidad
        municipioSelect.innerHTML = '<option value="">Cargando...</option>';
        municipioSelect.disabled = true;
        
        if (localidadSelect) {
            localidadSelect.innerHTML = '<option value="">-- Seleccione una Localidad --</option>';
            localidadSelect.disabled = true;
        }
        if (localidadContainer) {
            localidadContainer.style.display = 'none';
        }
        
        if (!departamentoId) {
            municipioSelect.innerHTML = '<option value="">-- Seleccione una Ciudad --</option>';
            municipioSelect.disabled = true;
            return;
        }
        
        // Cargar municipios via AJAX
        fetch(`/ajax/cargar-municipios/?departamento_id=${departamentoId}`)
            .then(response => response.json())
            .then(data => {
                municipioSelect.innerHTML = '<option value="">-- Seleccione una Ciudad --</option>';
                
                data.forEach(municipio => {
                    const option = document.createElement('option');
                    option.value = municipio.id;
                    option.textContent = municipio.nombre;
                    if (municipio.es_capital) {
                        option.textContent += ' (Capital)';
                    }
                    municipioSelect.appendChild(option);
                });
                
                municipioSelect.disabled = false;
                
                // Si hay un valor seleccionado previamente (edición), seleccionarlo
                if (municipioSelect.dataset.selectedId) {
                    municipioSelect.value = municipioSelect.dataset.selectedId;
                    municipioSelect.dispatchEvent(new Event('change'));
                }
            })
            .catch(error => {
                console.error('Error al cargar municipios:', error);
                municipioSelect.innerHTML = '<option value="">Error al cargar ciudades</option>';
                municipioSelect.disabled = true;
            });
    });
    
    // ========================================
    // MOSTRAR LOCALIDADES SI ES BOGOTÁ
    // ========================================
    if (municipioSelect && localidadSelect && localidadContainer) {
        municipioSelect.addEventListener('change', function() {
            const municipioId = this.value;
            
            if (!municipioId) {
                localidadContainer.style.display = 'none';
                localidadSelect.disabled = true;
                return;
            }
            
            // Verificar si el municipio es Bogotá
            fetch(`/ajax/cargar-localidades-bogota/?municipio_id=${municipioId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.es_bogota && data.localidades) {
                        // Mostrar select de localidades
                        localidadSelect.innerHTML = '<option value="">-- Seleccione una Localidad --</option>';
                        
                        data.localidades.forEach(localidad => {
                            const option = document.createElement('option');
                            option.value = localidad.id;
                            option.textContent = `${localidad.numero}. ${localidad.nombre}`;
                            localidadSelect.appendChild(option);
                        });
                        
                        localidadContainer.style.display = 'block';
                        localidadSelect.disabled = false;
                        
                        // Si hay un valor seleccionado previamente, seleccionarlo
                        if (localidadSelect.dataset.selectedId) {
                            localidadSelect.value = localidadSelect.dataset.selectedId;
                        }
                    } else {
                        // Ocultar select de localidades
                        localidadContainer.style.display = 'none';
                        localidadSelect.disabled = true;
                        localidadSelect.value = '';
                    }
                })
                .catch(error => {
                    console.error('Error al verificar localidades de Bogotá:', error);
                    localidadContainer.style.display = 'none';
                });
        });
    }
    
    // ========================================
    // INICIALIZACIÓN: Si hay departamento seleccionado, cargar municipios
    // ========================================
    if (departamentoSelect.value) {
        departamentoSelect.dispatchEvent(new Event('change'));
    }
}

/**
 * Función helper para inicializar múltiples formularios en la misma página
 * Útil para formularios multi-paso o modales
 */
function initMultipleGeografia(configs) {
    configs.forEach(config => initGeografiaColombia(config));
}

// Auto-inicialización si se detectan los campos por defecto
document.addEventListener('DOMContentLoaded', function() {
    // Intentar inicialización automática
    if (document.querySelector('#id_departamento_residencia')) {
        initGeografiaColombia();
    }
    
    // Para formularios de padre (puede tener ID diferente)
    if (document.querySelector('#id_departamento_padre')) {
        initGeografiaColombia({
            departamentoSelector: '#id_departamento_padre',
            municipioSelector: '#id_ciudad_padre',
            localidadSelector: '#id_localidad_bogota_padre',
            localidadContainer: '.localidad-padre-container',
        });
    }
});
