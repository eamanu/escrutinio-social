# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import path
from . import views, data_views, api
from fancy_cache import cache_page
from django.contrib.auth.decorators import login_required

cached = cache_page(300)


urlpatterns = [
    url('^escuelas.geojson$', cached(views.LugaresVotacionGeoJSON.as_view()), name='geojson'),
    url('^escuelas/(?P<pk>\d+)$', views.EscuelaDetailView.as_view(), name='detalle_escuela'),
    url('^mapa/$', login_required(cached(views.Mapa.as_view())), name='mapa'),
    url('^resultados/(?P<pk>\d+)?$', login_required(cached(views.ResultadosCategoria.as_view())),
        name='resultados-categoria'),
    url(r'^resultados-parciales-(?P<slug_categoria>[\w-]+).(?P<filetype>csv|xls)$', data_views.resultado_parcial_categoria, name='resultado-parcial-categoria'),

    path('alive/', api.Alive.as_view(), name="alive")
    # url(r'^fiscal_mesa/', views.fiscal_mesa, name='fiscal_mesa'),
]
