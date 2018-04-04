from django.conf.urls import url
from . import views

app_name = 'processor'

urlpatterns = [

	url(r'^$', views.index, name='index'),
	url(r'^initialize/$', views.initialize, name='initialize'),
	url(r'^reginput/$', views.regInput, name='regInput'),
	url(r'^meminput/$', views.memInput, name='memInput'),
]