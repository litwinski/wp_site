from django.conf.urls import patterns, url
from searcher import views

urlpatterns = patterns('',
        # view paged results.
        url(r'^[Pp]age/?.+?', views.view_paged), # must come before view_results url.
        # run search query without GET, display results.
        url(r'^/?(?P<_query>.+)$', views.view_results),
        # no query, show search form.
        url(r'^/?$', views.view_index),
        )