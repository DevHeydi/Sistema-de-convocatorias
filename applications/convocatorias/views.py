#views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib import messages
from django.http import HttpResponse
from .models import Convocatoria
from .forms import ConvocatoriaForm

# Importaciones para PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
import os

# ==================== CREAR ====================
def crear_convocatoria(request):
    if request.method == "POST":
        form = ConvocatoriaForm(request.POST, request.FILES)
        
        if "preview" in request.POST:
            if form.is_valid():
                convocatoria_preview = form.cleaned_data
                return render(request, 'preview.html', {
                    'convocatoria': convocatoria_preview,
                    'accion': 'Vista Previa'
                })
        else:
            if form.is_valid():
                form.save()
                return render(request, 'preview.html', {'accion': 'Crear'})
    else:
        form = ConvocatoriaForm()
    
    return render(request, 'create.html', {'form': form, 'accion': 'Crear'})

# ==================== VISTA PREVIA ================== #
def preview_convocatoria(request):
    if request.method != 'POST':
        return redirect('convocatorias:create')

    form = ConvocatoriaForm(request.POST, request.FILES)

    if not form.is_valid():
        return render(request, 'create.html', {
            'form': form,
            'accion': 'Crear'
        })

    return render(request, 'preview.html', {
        'convocatoria': form.cleaned_data
    })

# ==================== EDITAR ====================
def seleccionar_convocatoria(request):
    convocatorias = Convocatoria.objects.filter(activa=True)
    return render(request, 'edit.html', {
        'convocatorias': convocatorias
    })

def editar_convocatoria(request, id):
    convocatoria = get_object_or_404(Convocatoria, id=id)

    if request.method == 'POST':
        form = ConvocatoriaForm(request.POST, request.FILES, instance=convocatoria)

        if 'guardar' in request.POST and form.is_valid():
            form.save()
            return redirect('convocatorias:edit')

    else:
        form = ConvocatoriaForm(instance=convocatoria)

    return render(request, 'create.html', {
        'form': form,
        'accion': 'Editar'
    })


# ==================== ELIMINAR ====================
def eliminar_convocatoria(request):
    context = {}

    if request.method == 'POST':
        kword = request.POST.get('kword', '').strip()

        if kword:
            try:
                convocatoria = Convocatoria.objects.get(nombre__iexact=kword)
                convocatoria.delete()
                context['mensaje'] = f"Convocatoria '{kword}' eliminada correctamente."
            except Convocatoria.DoesNotExist:
                context['error'] = f"No se encontró la convocatoria '{kword}'."
            except Convocatoria.MultipleObjectsReturned:
                context['error'] = "Hay varias convocatorias con ese nombre."

    return render(request, 'delete.html', context)

# ==================== FILTRO/BUSCAR ====================
def filtro(request):
    query = request.GET.get('kword', '')
    deporte = request.GET.get('deporte', '')
    categoria = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    
    convocatorias = Convocatoria.objects.filter(activa=True)
    
    if query:
        convocatorias = convocatorias.filter(
            Q(nombre__icontains=query) |
            Q(deporte__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if deporte:
        convocatorias = convocatorias.filter(deporte__iexact=deporte)
    
    if categoria:
        convocatorias = convocatorias.filter(categoria__iexact=categoria)
    
    if estado:
        convocatorias = convocatorias.filter(estado__iexact=estado)
    
    deportes = Convocatoria.objects.filter(activa=True).values_list('deporte', flat=True).distinct()
    categorias = Convocatoria.objects.filter(activa=True).values_list('categoria', flat=True).distinct()
    estados = Convocatoria.objects.filter(activa=True).values_list('estado', flat=True).distinct()
    
    return render(request, 'filtro.html', {
        'convocatorias': convocatorias,
        'deportes': deportes,
        'categorias': categorias,
        'estados': estados,
        'query': query,
        'deporte_selected': deporte,
        'categoria_selected': categoria,
        'estado_selected': estado,
    })

# ==================== HERRAMIENTAS ====================
def tools(request):
    return render(request,'tools.html')

# ==================== GENERAR PDF ====================
def generar_pdf_convocatoria(request, id):
    """
    Genera un PDF con el formato oficial de la convocatoria
    """
    convocatoria = get_object_or_404(Convocatoria, id=id)
    
    # Crear el objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="convocatoria_{convocatoria.nombre}.pdf"'
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Contenedor de elementos
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a5490'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=10
    )
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    # Logo del ayuntamiento (si existe)
    if convocatoria.logo_ayuntamiento:
        try:
            logo_path = convocatoria.logo_ayuntamiento.path
            img = Image(logo_path, width=2*inch, height=1*inch)
            img.hAlign = 'CENTER'
            elementos.append(img)
            elementos.append(Spacer(1, 0.2*inch))
        except:
            pass
    
    # Título principal
    titulo = Paragraph(f"<b>CONVOCATORIA</b><br/>{convocatoria.nombre.upper()}", style_title)
    elementos.append(titulo)
    elementos.append(Spacer(1, 0.2*inch))
    
    # Institución responsable
    institucion = Paragraph(f"<b>{convocatoria.institucion_responsable}</b>", style_normal)
    institucion.hAlign = 'CENTER'
    elementos.append(institucion)
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información básica en tabla
    info_data = [
        ['Deporte:', convocatoria.deporte],
        ['Categoría:', convocatoria.categoria],
        ['Rama:', convocatoria.rama],
        ['Fecha de Inicio:', convocatoria.fecha_inicio_torneo.strftime('%d/%m/%Y')],
        ['Fecha Límite Inscripción:', convocatoria.fecha_limite_inscripcion.strftime('%d/%m/%Y')],
        ['Estado:', convocatoria.estado],
    ]
    
    tabla_info = Table(info_data, colWidths=[2.5*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elementos.append(tabla_info)
    elementos.append(Spacer(1, 0.2*inch))
    
    # Descripción
    if convocatoria.descripcion:
        elementos.append(Paragraph("<b>DESCRIPCIÓN</b>", style_subtitle))
        elementos.append(Paragraph(convocatoria.descripcion, style_normal))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Sistema de competencia
    if convocatoria.sistema_competencia:
        elementos.append(Paragraph("<b>SISTEMA DE COMPETENCIA</b>", style_subtitle))
        elementos.append(Paragraph(convocatoria.sistema_competencia, style_normal))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Requisitos
    if convocatoria.requisitos:
        elementos.append(Paragraph("<b>REQUISITOS</b>", style_subtitle))
        elementos.append(Paragraph(convocatoria.requisitos, style_normal))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Inscripciones
    elementos.append(Paragraph("<b>INSCRIPCIONES</b>", style_subtitle))
    inscripcion_data = [
        ['Costo:', f"${convocatoria.costo_inscripcion}"],
    ]
    if convocatoria.lugar_inscripcion:
        inscripcion_data.append(['Lugar:', convocatoria.lugar_inscripcion])
    if convocatoria.forma_pago:
        inscripcion_data.append(['Forma de pago:', convocatoria.forma_pago])
    
    tabla_inscripcion = Table(inscripcion_data, colWidths=[2*inch, 4.5*inch])
    tabla_inscripcion.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_inscripcion)
    elementos.append(Spacer(1, 0.15*inch))
    
    # Premiación
    if convocatoria.premiacion_primero:
        elementos.append(Paragraph("<b>PREMIACIÓN</b>", style_subtitle))
        premiacion_items = []
        if convocatoria.premiacion_primero:
            premiacion_items.append(f"🥇 <b>1er Lugar:</b> {convocatoria.premiacion_primero}")
        if convocatoria.premiacion_segundo:
            premiacion_items.append(f"🥈 <b>2do Lugar:</b> {convocatoria.premiacion_segundo}")
        if convocatoria.premiacion_tercero:
            premiacion_items.append(f"🥉 <b>3er Lugar:</b> {convocatoria.premiacion_tercero}")
        
        for item in premiacion_items:
            elementos.append(Paragraph(item, style_normal))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Comité organizador
    if convocatoria.comite_organizador:
        elementos.append(Paragraph("<b>COMITÉ ORGANIZADOR</b>", style_subtitle))
        elementos.append(Paragraph(convocatoria.comite_organizador, style_normal))
        elementos.append(Spacer(1, 0.15*inch))
    
    # Contacto
    elementos.append(Paragraph("<b>INFORMACIÓN DE CONTACTO</b>", style_subtitle))
    contacto_text = ""
    if convocatoria.direccion:
        contacto_text += f"<b>Dirección:</b> {convocatoria.direccion}<br/>"
    if convocatoria.telefono:
        contacto_text += f"<b>Teléfono:</b> {convocatoria.telefono}<br/>"
    if convocatoria.correo:
        contacto_text += f"<b>Correo:</b> {convocatoria.correo}"
    
    elementos.append(Paragraph(contacto_text, style_normal))
    
    # Construir PDF
    doc.build(elementos)
    
    # Obtener el valor del buffer y escribirlo en la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

# ==================== SELECCIONAR CONVOCATORIA PARA PDF ====================
def seleccionar_pdf(request):
    """
    Vista para seleccionar qué convocatoria convertir a PDF
    """
    convocatorias = Convocatoria.objects.filter(activa=True).order_by('-created_at')
    return render(request, 'seleccionar_pdf.html', {
        'convocatorias': convocatorias
    })