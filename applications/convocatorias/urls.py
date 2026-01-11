from django.urls import path
from . import views

app_name = 'convocatorias'

urlpatterns = [
    path('create/', views.crear_convocatoria, name='create'),
    path('preview/', views.preview_convocatoria, name='preview'),
    path('edit/', views.seleccionar_convocatoria, name='edit'),
    path('edit/<int:id>/', views.editar_convocatoria, name='editar_convocatoria'),
    path('delete/', views.eliminar_convocatoria, name='delete'), 
    path('filtro/', views.filtro, name='filtro'),
    path('tools/', views.tools, name='tools'),
    
    # Rutas para PDF
    path('pdf/seleccionar/', views.seleccionar_pdf, name='seleccionar_pdf'),
    path('pdf/generar/<int:id>/', views.generar_pdf_convocatoria, name='generar_pdf'),
]
