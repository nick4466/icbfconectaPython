/**
 * FUNCIONES PARA GENERAR HISTORIAL DE VISITAS
 * Genera HTML completo con toda la información de las actas de visita
 */

// Función para escapar HTML y prevenir XSS
function escapeHtml(text) {
  if (!text) return '';
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.toString().replace(/[&<>"']/g, m => map[m]);
}

function generarHTMLHistorial(visitas, nombreHogar) {
  let html = '<div style="padding: 20px;">';
  
  visitas.forEach((visita, index) => {
    const estadoBadge = obtenerBadgeEstado(visita.estado);
    const resultadoBadge = visita.acta ? obtenerBadgeResultado(visita.acta.resultado_visita) : '';
    
    html += `
      <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid var(--primary);">
        <!-- ENCABEZADO DE LA VISITA -->
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; border-bottom: 2px solid #f0f0f0; padding-bottom: 16px;">
          <div>
            <h3 style="margin: 0 0 8px 0; color: var(--primary); font-size: 20px;">
              <i class="fas fa-clipboard-check"></i> ${escapeHtml(visita.tipo_visita_display)}
            </h3>
            <p style="margin: 0; color: var(--text-light); font-size: 14px;">
              <i class="fas fa-calendar"></i> Programada: <strong>${escapeHtml(visita.fecha_programada)}</strong>
            </p>
            ${visita.fecha_realizacion ? `<p style="margin: 4px 0 0 0; color: var(--success); font-size: 14px;"><i class="fas fa-check-circle"></i> Realizada: <strong>${escapeHtml(visita.fecha_realizacion)}</strong></p>` : ''}
          </div>
          <div style="text-align: right;">
            ${estadoBadge}
            ${resultadoBadge}
          </div>
        </div>
        
        <!-- INFORMACIÓN BÁSICA -->
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px;">
          <div>
            <p style="margin: 0; font-size: 13px; color: var(--text-light);">Visitador</p>
            <p style="margin: 4px 0 0 0; font-weight: 600; color: var(--text);">
              <i class="fas fa-user-tie"></i> ${escapeHtml(visita.visitador || 'No asignado')}
            </p>
          </div>
          <div>
            <p style="margin: 0; font-size: 13px; color: var(--text-light);">Creado por</p>
            <p style="margin: 4px 0 0 0; font-weight: 600; color: var(--text);">
              <i class="fas fa-user"></i> ${escapeHtml(visita.creado_por)}
            </p>
          </div>
        </div>
        
        ${visita.observaciones_agenda ? `
          <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
            <p style="margin: 0; font-size: 13px; color: var(--text-light); margin-bottom: 4px;"><strong>Observaciones al Agendar:</strong></p>
            <p style="margin: 0; color: var(--text);">${escapeHtml(visita.observaciones_agenda)}</p>
          </div>
        ` : ''}
        
        ${visita.acta ? generarDetalleActa(visita.acta) : (visita.observaciones_visita ? generarObservacionesTexto(visita.observaciones_visita) : '<p style="color: var(--text-light); font-style: italic; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;"><i class="fas fa-info-circle"></i> Visita pendiente de completar el acta de evaluación</p>')}
      </div>
    `;
  });
  
  html += '</div>';
  return html;
}

function generarDetalleActa(acta) {
  return `
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 12px; margin-top: 16px;">
      <h4 style="margin: 0 0 16px 0; color: var(--primary); border-bottom: 2px solid var(--primary-light); padding-bottom: 8px;">
        <i class="fas fa-file-alt"></i> Acta de Evaluación Completa
      </h4>
      
      ${generarSeccionGeolocalizacion(acta)}
      ${generarSeccionServicios(acta)}
      ${generarSeccionInfraestructura(acta)}
      ${generarSeccionAreas(acta)}
      ${generarSeccionBanos(acta)}
      ${generarSeccionRiesgos(acta)}
      ${generarSeccionConclusiones(acta)}
    </div>
  `;
}

function generarObservacionesTexto(observaciones) {
  return `
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 12px; margin-top: 16px;">
      <h4 style="margin: 0 0 16px 0; color: var(--primary); border-bottom: 2px solid var(--primary-light); padding-bottom: 8px;">
        <i class="fas fa-file-alt"></i> Evaluación de Visita Técnica
      </h4>
      <div style="background: white; padding: 16px; border-radius: 8px; font-family: 'Courier New', monospace; white-space: pre-wrap; font-size: 13px; line-height: 1.8; color: #333;">
${escapeHtml(observaciones)}</div>
    </div>
  `;
}

function generarSeccionGeolocalizacion(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-map-marker-alt"></i> Geolocalización y Dirección Verificada
      </h5>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Latitud</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.geolocalizacion_lat_verificada}</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Longitud</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.geolocalizacion_lon_verificada}</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Estrato Verificado</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.estrato_verificado}</p>
        </div>
      </div>
      <div style="margin-top: 12px;">
        <p style="margin: 0; font-size: 12px; color: var(--text-light);">Dirección Verificada</p>
        <p style="margin: 4px 0 0 0; font-weight: 600;">${escapeHtml(acta.direccion_verificada)}</p>
        <p style="margin: 8px 0 0 0; font-size: 13px;">
          ${acta.direccion_coincide ? '<span style="color: var(--success);"><i class="fas fa-check-circle"></i> Dirección coincide con FUR</span>' : '<span style="color: var(--warning);"><i class="fas fa-exclamation-triangle"></i> Dirección NO coincide</span>'}
        </p>
      </div>
      ${acta.observaciones_direccion ? `<div style="margin-top: 12px; padding: 12px; background: #fff3cd; border-radius: 6px;"><p style="margin: 0; font-size: 13px;"><strong>Observaciones:</strong> ${escapeHtml(acta.observaciones_direccion)}</p></div>` : ''}
    </div>
  `;
}

function generarSeccionServicios(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-plug"></i> Servicios Públicos
      </h5>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
        <div style="text-align: center; padding: 12px; background: ${acta.tiene_agua_potable ? '#d4edda' : '#f8d7da'}; border-radius: 6px;">
          <i class="fas fa-tint" style="font-size: 24px; color: ${acta.tiene_agua_potable ? '#155724' : '#721c24'};"></i>
          <p style="margin: 8px 0 0 0; font-size: 13px; font-weight: 600;">${acta.tiene_agua_potable ? 'Agua Potable' : 'Sin Agua'}</p>
          ${acta.tiene_agua_potable ? `<p style="margin: 4px 0 0 0; font-size: 11px;">${acta.agua_continua ? '✓ Continua' : '✗ No continua'} | ${acta.agua_legal ? '✓ Legal' : '✗ Ilegal'}</p>` : ''}
        </div>
        <div style="text-align: center; padding: 12px; background: ${acta.tiene_energia ? '#d4edda' : '#f8d7da'}; border-radius: 6px;">
          <i class="fas fa-bolt" style="font-size: 24px; color: ${acta.tiene_energia ? '#155724' : '#721c24'};"></i>
          <p style="margin: 8px 0 0 0; font-size: 13px; font-weight: 600;">${acta.tiene_energia ? 'Energía' : 'Sin Energía'}</p>
          ${acta.tiene_energia ? `<p style="margin: 4px 0 0 0; font-size: 11px;">${acta.energia_continua ? '✓ Continua' : '✗ No continua'} | ${acta.energia_legal ? '✓ Legal' : '✗ Ilegal'}</p>` : ''}
        </div>
        <div style="text-align: center; padding: 12px; background: ${acta.tiene_alcantarillado ? '#d4edda' : '#f8d7da'}; border-radius: 6px;">
          <i class="fas fa-water" style="font-size: 24px; color: ${acta.tiene_alcantarillado ? '#155724' : '#721c24'};"></i>
          <p style="margin: 8px 0 0 0; font-size: 13px; font-weight: 600;">${acta.tiene_alcantarillado ? 'Alcantarillado' : 'Sin Alcantarillado'}</p>
        </div>
      </div>
    </div>
  `;
}

function generarSeccionInfraestructura(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-home"></i> Estado de Infraestructura
      </h5>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Pisos</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.estado_pisos_display}</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Paredes</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.estado_paredes_display}</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Techos</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.estado_techos_display}</p>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px;">
        <div>
          <p style="margin: 0; font-size: 13px;">
            ${acta.ventilacion_adecuada ? '<i class="fas fa-check-circle" style="color: var(--success);"></i> Ventilación adecuada' : '<i class="fas fa-times-circle" style="color: var(--danger);"></i> Ventilación deficiente'}
          </p>
        </div>
        <div>
          <p style="margin: 0; font-size: 13px;">
            ${acta.iluminacion_natural_adecuada ? '<i class="fas fa-check-circle" style="color: var(--success);"></i> Iluminación adecuada' : '<i class="fas fa-times-circle" style="color: var(--danger);"></i> Iluminación deficiente'}
          </p>
        </div>
      </div>
    </div>
  `;
}

function generarSeccionAreas(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-ruler-combined"></i> Medidas y Capacidad
      </h5>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Área Social</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.area_social_largo}m × ${acta.area_social_ancho}m = ${acta.area_social_total}m²</p>
        </div>
        ${acta.tiene_patio_cubierto ? `
          <div>
            <p style="margin: 0; font-size: 12px; color: var(--text-light);">Patio Cubierto</p>
            <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.patio_largo}m × ${acta.patio_ancho}m = ${acta.patio_total}m²</p>
          </div>
        ` : ''}
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Capacidad Calculada</p>
          <p style="margin: 4px 0 0 0; font-weight: 600; color: var(--info);">${acta.capacidad_calculada} niños (1.5m² por niño)</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Capacidad Recomendada</p>
          <p style="margin: 4px 0 0 0; font-weight: 600; color: var(--success); font-size: 18px;">${acta.capacidad_recomendada} niños</p>
        </div>
      </div>
      ${acta.justificacion_capacidad ? `<div style="margin-top: 12px; padding: 12px; background: #e7f3ff; border-radius: 6px;"><p style="margin: 0; font-size: 13px;"><strong>Justificación:</strong> ${escapeHtml(acta.justificacion_capacidad)}</p></div>` : ''}
    </div>
  `;
}

function generarSeccionBanos(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-toilet"></i> Baños y Condiciones Sanitarias
      </h5>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Número de Baños</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.num_banos_verificado}</p>
        </div>
        <div>
          <p style="margin: 0; font-size: 12px; color: var(--text-light);">Estado de Higiene</p>
          <p style="margin: 4px 0 0 0; font-weight: 600;">${acta.estado_higiene_banos_display}</p>
        </div>
      </div>
    </div>
  `;
}

function generarSeccionRiesgos(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-exclamation-triangle"></i> Riesgos Ambientales
      </h5>
      <div style="margin-bottom: 12px;">
        <p style="margin: 0; font-size: 12px; color: var(--text-light);">Nivel de Riesgo General</p>
        <p style="margin: 4px 0 0 0; font-weight: 600; font-size: 16px;">${obtenerBadgeRiesgo(acta.nivel_riesgo_general, acta.nivel_riesgo_general_display)}</p>
      </div>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
        <div style="font-size: 13px;">${acta.proximidad_rios ? '<i class="fas fa-check" style="color: var(--warning);"></i> Proximidad a ríos' : '<i class="fas fa-times" style="color: var(--text-light);"></i> Sin riesgo de ríos'}</div>
        <div style="font-size: 13px;">${acta.proximidad_deslizamientos ? '<i class="fas fa-check" style="color: var(--warning);"></i> Riesgo de deslizamientos' : '<i class="fas fa-times" style="color: var(--text-light);"></i> Sin riesgo de deslizamientos'}</div>
        <div style="font-size: 13px;">${acta.proximidad_trafico_intenso ? '<i class="fas fa-check" style="color: var(--warning);"></i> Tráfico intenso' : '<i class="fas fa-times" style="color: var(--text-light);"></i> Sin tráfico intenso'}</div>
        <div style="font-size: 13px;">${acta.proximidad_contaminacion ? '<i class="fas fa-check" style="color: var(--warning);"></i> Contaminación cercana' : '<i class="fas fa-times" style="color: var(--text-light);"></i> Sin contaminación'}</div>
      </div>
      ${acta.descripcion_riesgos ? `<div style="margin-top: 12px; padding: 12px; background: #fff3cd; border-radius: 6px;"><p style="margin: 0; font-size: 13px;"><strong>Descripción de Riesgos:</strong> ${escapeHtml(acta.descripcion_riesgos)}</p></div>` : ''}
    </div>
  `;
}

function generarSeccionConclusiones(acta) {
  return `
    <div style="background: white; padding: 16px; border-radius: 8px;">
      <h5 style="margin: 0 0 12px 0; color: var(--primary); font-size: 16px;">
        <i class="fas fa-file-signature"></i> Observaciones y Conclusiones
      </h5>
      <div style="background: #f8f9fa; padding: 14px; border-radius: 6px; margin-bottom: 12px;">
        <p style="margin: 0; font-size: 13px; line-height: 1.6;">${escapeHtml(acta.observaciones_generales)}</p>
      </div>
      ${acta.recomendaciones ? `
        <div style="background: #d1ecf1; padding: 14px; border-radius: 6px; margin-bottom: 12px;">
          <p style="margin: 0; font-size: 12px; color: var(--info); font-weight: 600; margin-bottom: 4px;">RECOMENDACIONES:</p>
          <p style="margin: 0; font-size: 13px; line-height: 1.6;">${escapeHtml(acta.recomendaciones)}</p>
        </div>
      ` : ''}
      ${acta.condiciones_aprobacion ? `
        <div style="background: #fff3cd; padding: 14px; border-radius: 6px;">
          <p style="margin: 0; font-size: 12px; color: var(--warning); font-weight: 600; margin-bottom: 4px;">CONDICIONES DE APROBACIÓN:</p>
          <p style="margin: 0; font-size: 13px; line-height: 1.6;">${escapeHtml(acta.condiciones_aprobacion)}</p>
        </div>
      ` : ''}
    </div>
  `;
}

function obtenerBadgeEstado(estado) {
  const estados = {
    'agendada': { color: 'var(--info)', icono: 'calendar-alt', texto: 'Agendada' },
    'en_proceso': { color: 'var(--warning)', icono: 'spinner', texto: 'En Proceso' },
    'completada': { color: 'var(--success)', icono: 'check-circle', texto: 'Completada' },
    'cancelada': { color: 'var(--danger)', icono: 'times-circle', texto: 'Cancelada' },
    'reprogramada': { color: 'var(--secondary)', icono: 'redo', texto: 'Reprogramada' },
  };
  const est = estados[estado] || { color: '#666', icono: 'question', texto: estado };
  return `<span style="display: inline-block; padding: 6px 12px; background: ${est.color}; color: white; border-radius: 20px; font-size: 12px; font-weight: 600;"><i class="fas fa-${est.icono}"></i> ${est.texto}</span>`;
}

function obtenerBadgeResultado(resultado) {
  const resultados = {
    'aprobado': { color: 'var(--success)', icono: 'check-circle', texto: 'APROBADO' },
    'aprobado_condiciones': { color: 'var(--warning)', icono: 'exclamation-circle', texto: 'APROBADO CON CONDICIONES' },
    'rechazado': { color: 'var(--danger)', icono: 'times-circle', texto: 'RECHAZADO' },
    'requiere_segunda_visita': { color: 'var(--info)', icono: 'redo', texto: 'REQUIERE 2DA VISITA' },
  };
  const res = resultados[resultado] || { color: '#666', icono: 'question', texto: resultado };
  return `<span style="display: inline-block; padding: 8px 16px; background: ${res.color}; color: white; border-radius: 6px; font-size: 13px; font-weight: 700; margin-top: 8px;"><i class="fas fa-${res.icono}"></i> ${res.texto}</span>`;
}

function obtenerBadgeRiesgo(nivel, texto) {
  const colores = {
    'sin_riesgo': 'var(--success)',
    'riesgo_bajo': '#28a745',
    'riesgo_medio': 'var(--warning)',
    'riesgo_alto': '#fd7e14',
    'riesgo_critico': 'var(--danger)'
  };
  return `<span style="display: inline-block; padding: 6px 12px; background: ${colores[nivel] || '#666'}; color: white; border-radius: 6px; font-weight: 600;">${texto}</span>`;
}
