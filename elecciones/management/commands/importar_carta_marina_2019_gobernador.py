from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from csv import DictReader
from elecciones.models import Seccion, Circuito, LugarVotacion, Mesa, Categoria
import datetime

CSV = Path(settings.BASE_DIR) / 'elecciones/data/escuelas-elecciones.2019-cordoba-gobernador.csv'

def to_float(val):
    try:
        return float(val.replace(',', '.'))
    except:
        return None


class BaseCommand(BaseCommand):

    def success(self, msg, ending='\n'):
        self.stdout.write(self.style.SUCCESS(msg), ending=ending)

    def warning(self, msg, ending='\n'):
        self.stdout.write(self.style.WARNING(msg), ending=ending)

    def log(self, object, created=True, ending='\n'):
        if created:
            self.success(f'creado {object}', ending=ending)
        else:
            self.warning(f'{object} ya existe', ending=ending)


class Command(BaseCommand):
    help = "Importar carta marina"

    def handle(self, *args, **options):
        reader = DictReader(CSV.open())

        fecha = datetime.datetime(2019, 5, 12, 8, 0)
        categoria_gobernador_cordoba, created = Categoria.objects.get_or_create(slug='gobernador-cordoba-2019', nombre='Gobernador Córdoba 2019', fecha=fecha)
        categoria_intendente_cordoba, created = Categoria.objects.get_or_create(slug='intendente-cordoba-2019', nombre='Intendente Córdoba 2019', fecha=fecha)
        categoria_legisladores_distrito_unico, created = Categoria.objects.get_or_create(slug='legisladores-dist-unico-cordoba-2019', nombre='Legisladores Distrito Único Córdoba 2019', fecha=fecha)
        # categoria_tribunal_de_cuentas_provincial, created = Categoria.objects.get_or_create(slug='tribunal-cuentas-prov-cordoba-2019', nombre='Tribunal de Cuentas Provincia de Córdoba 2019', fecha=fecha, activa=False)

        for c, row in enumerate(reader, 1):
            depto = row['Nombre Seccion']
            numero_de_seccion = int(row['Seccion'])
            seccion, created = Seccion.objects.get_or_create(nombre=depto, numero=numero_de_seccion)

            slg = f'legisladores-departamento-{depto}-2019'
            nombre = f'Legisladores Depto {depto} Córdoba 2019'

            # las departamentales no están activas por defecto
            # POR AHORA NO LAS USAMOS (inactivas)
            categoria_legislador_departamental, created = Categoria.objects.get_or_create(slug=slg,
                                                                                        nombre=nombre,
                                                                                        activa=False,
                                                                                        fecha=fecha)

            self.log(seccion, created)
            circuito, created = Circuito.objects.get_or_create(
                nombre=row['Nombre Circuito'], numero=row['Circuito'], seccion=seccion
            )

            """
            # no sabemos que ciudadnes eligen intendente
            # no estan en la base registrado que circuitos son ciudades en si misma y cuales son parte de una ciudad

            nombre_circuito = row['Nombre Seccion']
            slg = f'intendente-ciudad-{nombre_circuito}-2019'
            nombre = f'Intendente Ciudad {nombre_circuito} Córdoba 2019'
            categoria_intendente_municipal, created = Categoria.objects.get_or_create(slug=slg, nombre=nombre, fecha=fecha)
            """
            self.log(circuito, created)

            coordenadas = [to_float(row['Longitud']), to_float(row['Latitud'])]
            if coordenadas[0] and coordenadas[1]:
                geom = {'type': 'Point', 'coordinates': coordenadas}
                if row['Estado Geolocalizacion'] == 'Match':
                    estado_geolocalizacion = 9
                elif row['Estado Geolocalizacion'] == 'Partial Match':
                    estado_geolocalizacion = 5
            else:
                geom = None
                estado_geolocalizacion = 0

            escuela, created = LugarVotacion.objects.get_or_create(
                circuito=circuito,
                nombre=row['Establecimiento'],
                direccion=row['Direccion'],
                ciudad=row['Ciudad'] or '',
                barrio=row['Barrio'] or ''
                )

            escuela.electores = int(row['electores'])
            escuela.geom = geom
            escuela.estado_geolocalizacion = estado_geolocalizacion
            escuela.save()

            self.log(escuela, created)

            for mesa_nro in range(int(row['Mesa desde']), int(row['Mesa Hasta']) + 1):

                mesa, created = Mesa.objects.get_or_create(numero=mesa_nro)  # EVITAR duplicados en limpiezas de escuelas y otros
                mesa.lugar_votacion=escuela
                mesa.circuito=circuito
                mesa.save()

                if categoria_gobernador_cordoba not in mesa.categoria.all():
                    mesa.categoria_add(categoria_gobernador_cordoba)
                    self.success('Se agregó la mesa a la categoria a gobernador')
                if categoria_legisladores_distrito_unico not in mesa.categoria.all():
                    mesa.categoria_add(categoria_legisladores_distrito_unico)
                    self.success('Se agregó la mesa a la categoria a legislador dist unico')
                #if categoria_tribunal_de_cuentas_provincial not in mesa.categoria.all():
                #    mesa.categoria.add(categoria_tribunal_de_cuentas_provincial)
                #    self.success('Se agregó la mesa a la categoria a trib de cuentas provincial')



                # agregar la categoria a legislador departamental
                if categoria_legislador_departamental not in mesa.categoria.all():
                    mesa.categoria_add(categoria_legislador_departamental)
                    self.success('Se agregó la mesa a la categoria {}'.format(categoria_legislador_departamental.nombre))

                # si es de capital entonces vota a intendente
                if numero_de_seccion == 1:
                    # capital se pondera por circuitos
                    seccion.proyeccion_ponderada = True
                    seccion.save(update_fields=['proyeccion_ponderada'])
                    mesa.categoria_add(categoria_intendente_cordoba)
                    self.success('Se agregó la mesa a la categoria a intendente')

                mesa.save()

                self.log(mesa, created)


        """ hay 3 mesas que son de una escuela y no son nros consecutivos
            Se requiere copiar la mesa 1 3 veces antes de tirar este comando para que no falten esos tres datos

        """
        mesa_8651 = Mesa.objects.get(numero=1)
        mesa_8651.pk = None
        mesa_8651.numero = 8651
        mesa_8651.save()

        mesa_8652 = Mesa.objects.get(numero=1)
        mesa_8652.pk = None
        mesa_8652.numero = 8652
        mesa_8652.save()

        mesa_8653 = Mesa.objects.get(numero=1)
        mesa_8653.pk = None
        mesa_8653.numero = 8653
        mesa_8653.save()

