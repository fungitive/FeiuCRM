from django.urls import path
from .views import index


app_name = 'crm'

urlpatterns = [

    path('', index, name='index'),
]