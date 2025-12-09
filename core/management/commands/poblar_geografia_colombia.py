"""
Comando para poblar la base de datos con:
- 33 Departamentos de Colombia (32 + Bogotá D.C.)
- Municipios principales por departamento
- 20 Localidades de Bogotá D.C.

Uso: python manage.py poblar_geografia_colombia
"""
from django.core.management.base import BaseCommand
from core.models import Departamento, Municipio, LocalidadBogota


class Command(BaseCommand):
    help = 'Pobla la base de datos con departamentos, municipios y localidades de Colombia'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando población de geografía de Colombia...'))
        
        # Poblar Departamentos
        self.poblar_departamentos()
        
        # Poblar Municipios
        self.poblar_municipios()
        
        # Poblar Localidades de Bogotá
        self.poblar_localidades_bogota()
        
        self.stdout.write(self.style.SUCCESS('✅ Población de geografía completada exitosamente'))

    def poblar_departamentos(self):
        """Crea los 33 departamentos de Colombia"""
        self.stdout.write('📍 Creando departamentos...')
        
        departamentos = [
            {'nombre': 'Amazonas', 'codigo': '91'},
            {'nombre': 'Antioquia', 'codigo': '05'},
            {'nombre': 'Arauca', 'codigo': '81'},
            {'nombre': 'Atlántico', 'codigo': '08'},
            {'nombre': 'Bolívar', 'codigo': '13'},
            {'nombre': 'Boyacá', 'codigo': '15'},
            {'nombre': 'Caldas', 'codigo': '17'},
            {'nombre': 'Caquetá', 'codigo': '18'},
            {'nombre': 'Casanare', 'codigo': '85'},
            {'nombre': 'Cauca', 'codigo': '19'},
            {'nombre': 'Cesar', 'codigo': '20'},
            {'nombre': 'Chocó', 'codigo': '27'},
            {'nombre': 'Córdoba', 'codigo': '23'},
            {'nombre': 'Cundinamarca', 'codigo': '25'},
            {'nombre': 'Guainía', 'codigo': '94'},
            {'nombre': 'Guaviare', 'codigo': '95'},
            {'nombre': 'Huila', 'codigo': '41'},
            {'nombre': 'La Guajira', 'codigo': '44'},
            {'nombre': 'Magdalena', 'codigo': '47'},
            {'nombre': 'Meta', 'codigo': '50'},
            {'nombre': 'Nariño', 'codigo': '52'},
            {'nombre': 'Norte de Santander', 'codigo': '54'},
            {'nombre': 'Putumayo', 'codigo': '86'},
            {'nombre': 'Quindío', 'codigo': '63'},
            {'nombre': 'Risaralda', 'codigo': '66'},
            {'nombre': 'San Andrés y Providencia', 'codigo': '88'},
            {'nombre': 'Santander', 'codigo': '68'},
            {'nombre': 'Sucre', 'codigo': '70'},
            {'nombre': 'Tolima', 'codigo': '73'},
            {'nombre': 'Valle del Cauca', 'codigo': '76'},
            {'nombre': 'Vaupés', 'codigo': '97'},
            {'nombre': 'Vichada', 'codigo': '99'},
            {'nombre': 'Bogotá D.C.', 'codigo': '11'},  # Distrito Capital
        ]
        
        created_count = 0
        for dept_data in departamentos:
            dept, created = Departamento.objects.get_or_create(
                nombre=dept_data['nombre'],
                defaults={'codigo': dept_data['codigo']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ {dept.nombre}')
        
        self.stdout.write(self.style.SUCCESS(f'  Departamentos creados: {created_count}/{len(departamentos)}'))

    def poblar_municipios(self):
        """Crea municipios principales por departamento"""
        self.stdout.write('🏙️  Creando municipios...')
        
        # Diccionario con departamento: [municipios]
        # Incluye capitales (marcadas con *) y municipios importantes
        municipios_data = {
            'Amazonas': ['Leticia*', 'Puerto Nariño'],
            'Antioquia': ['Medellín*', 'Bello', 'Itagüí', 'Envigado', 'Apartadó', 'Turbo', 'Rionegro', 
                          'Sabaneta', 'Caldas', 'La Estrella', 'Copacabana', 'Girardota', 'Barbosa',
                          'Jardín', 'Jericó', 'Ciudad Bolívar', 'Santa Fe de Antioquia'],
            'Arauca': ['Arauca*', 'Tame', 'Saravena'],
            'Atlántico': ['Barranquilla*', 'Soledad', 'Malambo', 'Sabanalarga', 'Puerto Colombia', 
                          'Galapa', 'Baranoa'],
            'Bolívar': ['Cartagena de Indias*', 'Magangué', 'Turbaco', 'Arjona', 'El Carmen de Bolívar',
                        'Achí', 'Simití'],
            'Boyacá': ['Tunja*', 'Duitama', 'Sogamoso', 'Chiquinquirá', 'Paipa', 'Villa de Leyva',
                       'Jenesano', 'Jordán'],
            'Caldas': ['Manizales*', 'La Dorada', 'Chinchiná', 'Villamaría', 'Riosucio'],
            'Caquetá': ['Florencia*', 'San Vicente del Caguán', 'Puerto Rico'],
            'Casanare': ['Yopal*', 'Aguazul', 'Villanueva', 'Tauramena'],
            'Cauca': ['Popayán*', 'Santander de Quilichao', 'Puerto Tejada', 'Patía', 'Jambaló'],
            'Cesar': ['Valledupar*', 'Aguachica', 'Bosconia', 'Codazzi', 'Pelaya'],
            'Chocó': ['Quibdó*', 'Istmina', 'Condoto', 'Tadó'],
            'Córdoba': ['Montería*', 'Cereté', 'Lorica', 'Sahagún', 'Planeta Rica'],
            'Cundinamarca': ['Bogotá D.C.*', 'Soacha', 'Fusagasugá', 'Facatativá', 'Zipaquirá', 'Chía',
                             'Mosquera', 'Madrid', 'Funza', 'Cajicá', 'Sibaté', 'Tocancipá', 'Girardot',
                             'Ubaté', 'Villeta', 'Jerusalén', 'Junín', 'La Calera'],
            'Guainía': ['Inírida*'],
            'Guaviare': ['San José del Guaviare*'],
            'Huila': ['Neiva*', 'Pitalito', 'Garzón', 'La Plata', 'Campoalegre'],
            'La Guajira': ['Riohacha*', 'Maicao', 'Uribia', 'Manaure'],
            'Magdalena': ['Santa Marta*', 'Ciénaga', 'Fundación', 'Plato', 'El Banco'],
            'Meta': ['Villavicencio*', 'Acacías', 'Granada', 'Puerto López', 'San Martín'],
            'Nariño': ['Pasto*', 'Tumaco', 'Ipiales', 'Túquerres', 'Samaniego'],
            'Norte de Santander': ['Cúcuta*', 'Ocaña', 'Pamplona', 'Villa del Rosario', 'Los Patios'],
            'Putumayo': ['Mocoa*', 'Puerto Asís', 'Orito', 'Valle del Guamuez'],
            'Quindío': ['Armenia*', 'Calarcá', 'La Tebaida', 'Montenegro', 'Circasia'],
            'Risaralda': ['Pereira*', 'Dosquebradas', 'Santa Rosa de Cabal', 'La Virginia'],
            'San Andrés y Providencia': ['San Andrés*', 'Providencia'],
            'Santander': ['Bucaramanga*', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja',
                          'San Gil', 'Socorro', 'Málaga', 'Jesús María', 'Jordán'],
            'Sucre': ['Sincelejo*', 'Corozal', 'Sampués', 'San Marcos'],
            'Tolima': ['Ibagué*', 'Espinal', 'Melgar', 'Honda', 'Chaparral', 'Líbano'],
            'Valle del Cauca': ['Cali*', 'Palmira', 'Buenaventura', 'Tuluá', 'Cartago', 'Buga',
                                'Jamundí', 'Yumbo', 'Candelaria'],
            'Vaupés': ['Mitú*'],
            'Vichada': ['Puerto Carreño*'],
            'Bogotá D.C.': ['Bogotá D.C.*'],  # Bogotá es ciudad y departamento
        }
        
        created_count = 0
        total_count = 0
        
        for dept_nombre, municipios in municipios_data.items():
            try:
                departamento = Departamento.objects.get(nombre=dept_nombre)
                
                for municipio_nombre in municipios:
                    # Detectar si es capital (termina con *)
                    es_capital = municipio_nombre.endswith('*')
                    nombre_limpio = municipio_nombre.rstrip('*')
                    
                    mun, created = Municipio.objects.get_or_create(
                        nombre=nombre_limpio,
                        departamento=departamento,
                        defaults={'es_capital': es_capital}
                    )
                    total_count += 1
                    if created:
                        created_count += 1
                        
            except Departamento.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ❌ Departamento no encontrado: {dept_nombre}'))
        
        self.stdout.write(self.style.SUCCESS(f'  Municipios creados: {created_count}/{total_count}'))

    def poblar_localidades_bogota(self):
        """Crea las 20 localidades de Bogotá D.C."""
        self.stdout.write('🏙️  Creando localidades de Bogotá...')
        
        localidades = [
            {'numero': 1, 'nombre': 'Usaquén'},
            {'numero': 2, 'nombre': 'Chapinero'},
            {'numero': 3, 'nombre': 'Santa Fe'},
            {'numero': 4, 'nombre': 'San Cristóbal'},
            {'numero': 5, 'nombre': 'Usme'},
            {'numero': 6, 'nombre': 'Tunjuelito'},
            {'numero': 7, 'nombre': 'Bosa'},
            {'numero': 8, 'nombre': 'Kennedy'},
            {'numero': 9, 'nombre': 'Fontibón'},
            {'numero': 10, 'nombre': 'Engativá'},
            {'numero': 11, 'nombre': 'Suba'},
            {'numero': 12, 'nombre': 'Barrios Unidos'},
            {'numero': 13, 'nombre': 'Teusaquillo'},
            {'numero': 14, 'nombre': 'Los Mártires'},
            {'numero': 15, 'nombre': 'Antonio Nariño'},
            {'numero': 16, 'nombre': 'Puente Aranda'},
            {'numero': 17, 'nombre': 'La Candelaria'},
            {'numero': 18, 'nombre': 'Rafael Uribe Uribe'},
            {'numero': 19, 'nombre': 'Ciudad Bolívar'},
            {'numero': 20, 'nombre': 'Sumapaz'},
        ]
        
        created_count = 0
        for loc_data in localidades:
            loc, created = LocalidadBogota.objects.get_or_create(
                numero=loc_data['numero'],
                defaults={'nombre': loc_data['nombre']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ {loc.numero}. {loc.nombre}')
        
        self.stdout.write(self.style.SUCCESS(f'  Localidades creadas: {created_count}/{len(localidades)}'))
