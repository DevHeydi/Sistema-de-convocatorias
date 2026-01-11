from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from datetime import date


class Convocatoria(models.Model):
    # Imágenes
    logo_ayuntamiento = models.ImageField(
        upload_to='convocatorias/logos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        help_text="Logo del ayuntamiento (parte superior). Tamaño recomendado: 300x150px"
    )
    
    imagen_fondo = models.ImageField(
        upload_to='convocatorias/fondos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        help_text="Imagen de fondo de la convocatoria"
    )
    
    # Información básica
    nombre = models.CharField(max_length=200, help_text="Nombre de la liga/torneo")
    deporte = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    # Fechas
    fecha_inicio_torneo = models.DateField(
    help_text="Fecha de inicio del torneo",
    default=date.today  # <-- valor por defecto
    )

    fecha_limite_inscripcion = models.DateField(
    help_text="Fecha límite para inscripciones",
    default=date.today  # <-- valor por defecto
    )
    fecha_reunion_previa = models.DateField(blank=True, null=True, help_text="Fecha de reunión previa")
    hora_reunion_previa = models.TimeField(blank=True, null=True)
    
    # Categorías y Rama
    CATEGORIAS = [
        ('Libre', 'Libre'),
        ('Juvenil', 'Juvenil'),
        ('Veteranos', 'Veteranos'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    
    RAMAS = [
        ('Femenil', 'Femenil'),
        ('Varonil', 'Varonil'),
        ('Mixta', 'Mixta'),
    ]
    rama = models.CharField(max_length=10, choices=RAMAS)
    
    # Estado de la convocatoria
    ESTADOS = [
        ('Abierta', 'Abierta'),
        ('Cerrada', 'Cerrada'),
        ('En curso', 'En curso'),
        ('Finalizada', 'Finalizada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierta')
    
    # Comité Organizador
    comite_organizador = models.CharField(max_length=300, blank=True, null=True)
    
    # Sistema de Competencia
    sistema_competencia = models.TextField(blank=True, null=True, help_text="Formato del torneo (round-robin, eliminatoria, etc.)")
    fase_final = models.TextField(blank=True, null=True, help_text="Descripción de la fase final")
    
    # Inscripciones
    costo_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Costo en pesos")
    forma_pago = models.TextField(blank=True, null=True, help_text="Descripción de formas de pago")
    lugar_inscripcion = models.CharField(max_length=300, blank=True, null=True)
    
    # Requisitos
    requisitos = models.TextField(blank=True, null=True, help_text="Requisitos para participar")
    documentos_requeridos = models.TextField(blank=True, null=True, help_text="Lista de documentos necesarios")
    
    # Normatividad
    normatividad_aplicable = models.TextField(blank=True, null=True, help_text="Reglamentos aplicables")
    
    # Premiación
    premiacion_primero = models.CharField(max_length=200, blank=True, null=True)
    premiacion_segundo = models.CharField(max_length=200, blank=True, null=True)
    premiacion_tercero = models.CharField(max_length=200, blank=True, null=True)
    premiacion_adicional = models.TextField(blank=True, null=True, help_text="Otros premios")
    
    # Arbitraje
    arbitraje = models.TextField(blank=True, null=True, help_text="Información sobre árbitros")
    costo_arbitraje = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Junta Previa
    junta_previa_descripcion = models.TextField(blank=True, null=True)
    junta_previa_fecha = models.DateField(blank=True, null=True)
    junta_previa_hora = models.TimeField(blank=True, null=True)
    
    # Transitorios
    transitorios = models.TextField(blank=True, null=True, help_text="Disposiciones transitorias")
    
    # Información de contacto y ubicación
    institucion_responsable = models.CharField(max_length=300, default="Instituto Municipal de Cultura Física y Deporte")
    direccion = models.CharField(max_length=400, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Convocatoria"
        verbose_name_plural = "Convocatorias"
        ordering = ['-fecha_inicio_torneo']
    
    def __str__(self):
        return f"{self.nombre} - {self.deporte} ({self.categoria} - {self.rama})"
    
    def esta_abierta(self):
        """Verifica si la convocatoria está en periodo de inscripción"""
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.estado == 'Abierta' and hoy <= self.fecha_limite_inscripcion