from django import forms
from .models import Convocatoria

class ConvocatoriaForm(forms.ModelForm):
    class Meta:
        model = Convocatoria
        fields = '__all__'  # O selecciona los campos específicos
        widgets = {
            'fecha_inicio_torneo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite_inscripcion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_reunion_previa': forms.DateInput(attrs={'type': 'date'}),
            'junta_previa_fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_reunion_previa': forms.TimeInput(attrs={'type': 'time'}),
            'junta_previa_hora': forms.TimeInput(attrs={'type': 'time'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'sistema_competencia': forms.Textarea(attrs={'rows': 3}),
            'requisitos': forms.Textarea(attrs={'rows': 3}),
            'normatividad_aplicable': forms.Textarea(attrs={'rows': 3}),
            'premiacion_adicional': forms.Textarea(attrs={'rows': 3}),
            'arbitraje': forms.Textarea(attrs={'rows': 3}),
            'junta_previa_descripcion': forms.Textarea(attrs={'rows': 3}),
            'transitorios': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre de la convocatoria',
            'deporte': 'Deporte',
            'descripcion': 'Descripción',
            # Agrega más labels personalizados si necesitas
        }

class ConvocatoriaEditForm(forms.ModelForm):
    class Meta:
        model = Convocatoria
        exclude = ['created_at', 'updated_at']  # Excluir campos automáticos
        widgets = {
            'fecha_inicio_torneo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite_inscripcion': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }