from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .models import LugarVotacion, Circuito

class Alive(APIView):
    """Alive
    """
    def get(self, request):
        response = Response({"message":"hello world"}, status=status.HTTP_200_OK)
        return response

class Resultados(APIView):
    """Api que realiza el cálculo de resultados
    """

    def get(self, request):
        self.request = request
        # TODO: extraer por el request la categoría

        pk = 1
        if pk == 1:
            pk == Categoria.objecs.first().id
        categoria = get_object_or_404(Categoria, id=pk)
        resultados = self.get_resultados(categoria)
        return 404
        
    def filtros(self, request):
        """
        A partir de los argumentos de urls, devuelve
        listas de seccion / circuito etc. para filtrar
        """
        if 'seccion' in request.GET:
            return Seccion.objects.filter(id__in=request.GET.getlist('seccion'))
        elif 'circuito' in request.GET:
            return Circuito.objects.filter(id__in=request.GET.getlist('circuito'))
        elif 'lugarvotacion' in request.GET:
            return LugarVotacion.objects.filter(id__in=request.GET.getlist('lugarvotacion'))
        elif 'mesa' in request.GET:
            return Mesa.objects.filter(id__in=request.GET.getlist('mesa'))
        return None

    def get_resultados(self, categoria):
        """
        Realiza la contabilidad para la categoria, invocando al método
        ``calcular``.

        Si el se pasa el parámetro proyectado, se incluye un diccionario
        extra con la ponderación, invocando a ``calcular``para obtener los
        resultados parciales de cada subdistrito para luego realizar la ponderación
        """
        lookups = Q()
        lookups2 = Q()
        resultados = {}
        proyectado = 'proyectado' in self.request.GET and not self.filtros

        if self.filtros:
            if 'seccion' in self.request.GET:
                lookups = Q(mesa__lugar_votacion__circuito__seccion__in=self.filtros)
                lookups2 = Q(lugar_votacion__circuito__seccion__in=self.filtros)

            elif 'circuito' in self.request.GET:
                lookups = Q(mesa__lugar_votacion__circuito__in=self.filtros)
                lookups2 = Q(lugar_votacion__circuito__in=self.filtros)

            elif 'lugarvotacion' in self.request.GET:
                lookups = Q(mesa__lugar_votacion__in=self.filtros)
                lookups2 = Q(lugar_votacion__in=self.filtros)

            elif 'mesa' in self.request.GET:
                lookups = Q(mesa__id__in=self.filtros)
                lookups2 = Q(id__in=self.filtros)

        mesas = self.mesas(categoria)

        c = self.calcular(categoria, mesas)

        proyeccion_incompleta = []
        if proyectado:
            # La proyeccion se calcula sólo cuando no hay filtros (es decir, para provincia)
            # ponderando por secciones (o circuitos para secciones de "proyeccion ponderada")

            agrupaciones = list(itertools.chain(  # cast para reusar
                Circuito.objects.filter(seccion__proyeccion_ponderada=True),
                Seccion.objects.filter(proyeccion_ponderada=False)
            ))
            datos_ponderacion = {}

            electores_pond = 0
            for ag in agrupaciones:
                mesas = ag.mesas(categoria)
                datos_ponderacion[ag] = self.calcular(categoria, mesas)

                if not datos_ponderacion[ag]["escrutados"]:
                    proyeccion_incompleta.append(ag)
                else:
                    electores_pond += datos_ponderacion[ag]["electores"]

        expanded_result = {}
        for k, v in c.votos.items():
            porcentaje_total = f'{v*100/c.total:.2f}' if c.total else '-'
            porcentaje_positivos = f'{v*100/c.positivos:.2f}' if c.positivos and isinstance(k, Partido) else '-'
            expanded_result[k] = {
                "votos": v,
                "porcentajeTotal": porcentaje_total,
                "porcentajePositivos": porcentaje_positivos
            }
            if proyectado:
                acumulador_positivos = 0
                for ag in agrupaciones:
                    data = datos_ponderacion[ag]
                    if k in data["votos"] and data["positivos"]:
                        acumulador_positivos += data["electores"]*data["votos"][k]/data["positivos"]

                expanded_result[k]["proyeccion"] = f'{acumulador_positivos*100/electores_pond:.2f}'

        # TODO permitir opciones positivas no asociadas a partido.
        tabla_positivos = OrderedDict(
            sorted(
                [(k, v) for k, v in expanded_result.items() if isinstance(k, Partido)],
                key=lambda x: float(x[1]["proyeccion" if proyectado else "votos"]), reverse=True
            )
        )

        tabla_no_positivos = {k: v for k, v in c.votos.items() if not isinstance(k, Partido)}
        tabla_no_positivos["Positivos"] = {
            "votos": c.positivos,
            "porcentajeTotal": f'{c.positivos*100/c.total:.2f}' if c.total else '-'
        }
        result_piechart = None
        if settings.SHOW_PLOT:
            result_piechart = [{
                'key': str(k),
                'y': v["votos"],
                'color': k.color if not isinstance(k, str) else '#CCCCCC'
            } for k, v in tabla_positivos.items()]
        resultados = {
            'tabla_positivos': tabla_positivos,
            'tabla_no_positivos': tabla_no_positivos,
            'result_piechart': result_piechart,

            'electores': c.electores,
            'positivos': c.positivos,
            'escrutados': c.escrutados,
            'votantes': c.total,

            'proyectado': proyectado,
            'proyeccion_incompleta': proyeccion_incompleta,
            'porcentaje_mesas_escrutadas': c.porcentaje_mesas_escrutadas,
            'porcentaje_escrutado': f'{c.escrutados*100/c.electores:.2f}' if c.electores else '-',
            'porcentaje_participacion': f'{c.total*100/c.escrutados:.2f}' if c.escrutados else '-',
            'total_mesas_escrutadas': c.total_mesas_escrutadas,
            'total_mesas': c.total_mesas
        }
        return resultados

    def calcular(self, categoria, mesas):
        """
        Implementa los cómputos escenciales de la categoria para las mesas dadas.
        Se invoca una vez para el cálculo de resultados y N veces para los proyectados.

        Devuelve

            electores: cantidad de electores en las mesas válidas en la categoria
            escrutados: cantidad de electores en las mesas que efectivamente fueron escrutadas   # TODO revisar!
            porcentaje_mesas_escrutadas:
            votos: diccionario con resultados de votos por partido y opcion (positivos y no positivos)
            total: total votos (positivos + no positivos)
            positivos: total votos positivos
        """
        electores = mesas.filter(categoria=categoria).aggregate(v=Sum('electores'))['v'] or 0
        sum_por_partido, otras_opciones = ResultadosCategoria.agregaciones_por_partido(categoria)

        # primero para partidos

        reportados = VotoMesaReportado.objects.filter(
            carga__categoria=categoria, carga__mesa__in=Subquery(mesas.values('id'))
        )
        mesas_escrutadas = mesas.filter(carga__votomesareportado__isnull=False).distinct()
        escrutados = mesas_escrutadas.aggregate(v=Sum('electores'))['v']
        if escrutados is None:
            escrutados = 0

        total_mesas_escrutadas = mesas_escrutadas.count()
        total_mesas = mesas.count()
        if total_mesas == 0:
            total_mesas = 1
        porcentaje_mesas_escrutadas = f'{total_mesas_escrutadas*100/total_mesas:.2f}'

        result = reportados.aggregate(
            **sum_por_partido
        )

        result = {Partido.objects.get(id=k): v for k, v in result.items() if v is not None}

        # no positivos
        result_opc = reportados.aggregate(
           **otras_opciones
        )
        result_opc = {k: v for k, v in result_opc.items() if v is not None}

        # calculamos el total como la suma de todos los positivos y los
        # validos no positivos.
        positivos = sum(result.values())
        total = positivos + sum(v for k, v in result_opc.items() if Opcion.objects.filter(nombre=k, es_contable=False, es_metadata=False).exists())
        result.update(result_opc)

        return AttrDict({
            "electores": electores,
            "escrutados": escrutados,
            "porcentaje_mesas_escrutadas": porcentaje_mesas_escrutadas,
            "votos": result,
            "total": total,
            "positivos": positivos,
            "total_mesas_escrutadas": total_mesas_escrutadas,
            "total_mesas": total_mesas
        })
