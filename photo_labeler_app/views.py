import os
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import UploadExcelForm, UploadImagesForm
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF  # en fpdf2 sigue igual, pero es otro paquete instalado

# Guardar datos en memoria
excel_data = []
image_files = []
assigned_labels = {}
cover_image = None

def clear_tmp(exclude_files=None):
    tmp_folder = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'tmp')
    if not os.path.exists(tmp_folder):
        return
    if exclude_files is None:
        exclude_files = []

    for filename in os.listdir(tmp_folder):
        file_path = os.path.join(tmp_folder, filename)
        try:
            if os.path.isfile(file_path) and filename not in exclude_files:
                os.remove(file_path)
        except Exception as e:
            print(f"Error borrando {file_path}: {e}")

def home(request):
    return redirect('upload_excel')

def upload_excel(request):
    global excel_data
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['file']
            df = pd.read_excel(excel_file)
            excel_data = df.apply(lambda row: f"{row[0]} - {row[1]}", axis=1).tolist()
            return redirect('upload_images')
    else:
        form = UploadExcelForm()
    return render(request, 'upload_excel.html', {'form': form})

from django.core.files.storage import FileSystemStorage

def upload_images(request):
    global image_files
    if request.method == 'POST':
        form = UploadImagesForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'tmp'))
            for img in request.FILES.getlist('images'):
                filename = fs.save(img.name, img)  # Guarda la imagen en /static/tmp/
                image_files.append(filename)       # Guarda el nombre del archivo
            return redirect('assign_labels')
    else:
        form = UploadImagesForm()
    return render(request, 'upload_images.html', {'form': form})

#===========================================================================
# VERSION MAS SEGURA PERO NO TAN PROLIJA
# def agregar_label(imagen_path, texto, output_path):
#     from PIL import Image, ImageDraw, ImageFont
#     import os
#     from django.conf import settings
#     import textwrap

#     img = Image.open(imagen_path)
#     draw = ImageDraw.Draw(img)
#     width, height = img.size

#     font_path = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'fonts', 'tnr.ttf')
#     base_font_size = int(height * 0.05)
#     min_font_size = int(height * 0.025)

#     if '-' in texto:
#         numero_articulo, nombre_articulo = [part.strip() for part in texto.split('-', 1)]
#     else:
#         partes = texto.split(maxsplit=1)
#         numero_articulo = partes[0]
#         nombre_articulo = partes[1] if len(partes) > 1 else ""

#     art_line = f"Art. {numero_articulo}"
#     nombre_articulo = nombre_articulo.replace('-', '').strip()
#     reached_min_font = False

#     font_size = base_font_size

#     while font_size >= min_font_size:
#         font = ImageFont.truetype(font_path, font_size)
#         max_line_length = max(20, int(width / (font_size * 0.4)))

#         name_lines = textwrap.wrap(nombre_articulo, width=max_line_length) if nombre_articulo else []
#         all_lines = [art_line] + name_lines

#         line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in all_lines]
#         line_widths = [bbox[2] - bbox[0] for bbox in line_bboxes]
#         line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]

#         padding_x = int(font_size * 0.4)
#         padding_y = int(font_size * 0.3)
#         interline_spacing = int(font_size * 0.1)

#         rect_heights = [h + padding_y * 2 for h in line_heights]
#         rect_widths = [w + padding_x * 2 for w in line_widths]

#         total_height = sum(rect_heights) + interline_spacing * (len(all_lines) - 1)
#         max_rect_width = max(rect_widths) if rect_widths else 0

#         if total_height <= height and max_rect_width <= width:
#             break

#         font_size -= 2
#         if font_size < min_font_size:
#             reached_min_font = True
#             break

#     if reached_min_font:
#         print(f"[WARNING] Texto demasiado largo para {imagen_path}, mostrando al mínimo legible")

#     font = ImageFont.truetype(font_path, font_size)
#     max_line_length = max(20, int(width / (font_size * 0.4)))
#     name_lines = textwrap.wrap(nombre_articulo, width=max_line_length) if nombre_articulo else []
#     all_lines = [art_line] + name_lines
#     line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in all_lines]
#     line_widths = [bbox[2] - bbox[0] for bbox in line_bboxes]
#     line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]
#     padding_x = int(font_size * 0.4)
#     padding_y = int(font_size * 0.3)
#     interline_spacing = int(font_size * 0.1)
#     rect_heights = [h + padding_y * 2 for h in line_heights]

#     total_height = sum(rect_heights) + interline_spacing * (len(all_lines) - 1)
#     bottom_padding = int(height * 0.02)  # ← nuevo margen inferior

#     current_y = height - total_height - bottom_padding

#     for i, line in enumerate(all_lines):
#         bbox = line_bboxes[i]
#         line_width = bbox[2] - bbox[0]
#         line_height = bbox[3] - bbox[1]

#         rect_left = (width - line_width) / 2 - padding_x
#         rect_right = (width + line_width) / 2 + padding_x
#         rect_top = current_y
#         rect_bottom = current_y + line_height + padding_y * 2

#         draw.rectangle([(rect_left, rect_top), (rect_right, rect_bottom)], fill=(64, 224, 208))

#         text_x = (width - line_width) / 2
#         text_y = rect_top + padding_y - bbox[1]
#         draw.text((text_x, text_y), line, fill="white", font=font)

#         current_y = rect_bottom + interline_spacing

#     img.save(output_path)
#===========================================================================

def agregar_label(imagen_path, texto, output_path):
    from PIL import Image, ImageDraw, ImageFont
    import os
    from django.conf import settings
    import textwrap

    img = Image.open(imagen_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_path = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'fonts', 'tnr.ttf')
    base_font_size = int(height * 0.05)
    min_font_size = int(height * 0.025)

    if '-' in texto:
        numero_articulo, nombre_articulo = [part.strip() for part in texto.split('-', 1)]
    else:
        partes = texto.split(maxsplit=1)
        numero_articulo = partes[0]
        nombre_articulo = partes[1] if len(partes) > 1 else ""

    art_line = f"Art. {numero_articulo}"
    nombre_articulo = nombre_articulo.replace('-', '').strip()
    font_size = base_font_size
    reached_min_font = False

    # Bucle robusto: controlamos ancho y alto al mismo tiempo
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        max_line_length = max(10, int(width / (font_size * 0.4)))

        name_lines = textwrap.wrap(nombre_articulo, width=max_line_length) if nombre_articulo else []
        all_lines = [art_line] + name_lines

        line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in all_lines]
        line_widths = [bbox[2] - bbox[0] for bbox in line_bboxes]
        line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]

        padding_x = int(font_size * 0.4)
        padding_y = int(font_size * 0.3)
        interline_spacing = int(font_size * 0.1)

        rect_heights = [h + padding_y * 2 for h in line_heights]
        rect_widths = [w + padding_x * 2 for w in line_widths]

        total_height = sum(rect_heights) + interline_spacing * (len(all_lines) - 1)
        max_rect_width = max(rect_widths) if rect_widths else 0

        if total_height <= height and max_rect_width <= width:
            break

        font_size -= 2
        if font_size < min_font_size:
            reached_min_font = True
            break

    if reached_min_font:
        print(f"[WARNING] Texto demasiado largo para {imagen_path}, mostrando al mínimo legible")

    # Recalcula final
    font = ImageFont.truetype(font_path, font_size)
    max_line_length = max(10, int(width / (font_size * 0.4)))
    name_lines = textwrap.wrap(nombre_articulo, width=max_line_length) if nombre_articulo else []
    all_lines = [art_line] + name_lines
    line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in all_lines]
    line_widths = [bbox[2] - bbox[0] for bbox in line_bboxes]
    line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]
    padding_x = int(font_size * 0.4)
    padding_y = int(font_size * 0.3)
    interline_spacing = int(font_size * 0.1)
    rect_heights = [h + padding_y * 2 for h in line_heights]

    total_height = sum(rect_heights) + interline_spacing * (len(all_lines) - 1)
    bottom_padding = int(height * 0.02)

    current_y = height - total_height - bottom_padding

    for i, line in enumerate(all_lines):
        bbox = line_bboxes[i]
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        rect_left = (width - line_width) / 2 - padding_x
        rect_right = (width + line_width) / 2 + padding_x
        rect_top = current_y
        rect_bottom = current_y + line_height + padding_y * 2

        draw.rectangle([(rect_left, rect_top), (rect_right, rect_bottom)], fill=(64, 224, 208))

        text_x = (width - line_width) / 2
        text_y = rect_top + padding_y - bbox[1]
        draw.text((text_x, text_y), line, fill="white", font=font)

        current_y = rect_bottom + interline_spacing

    img.save(output_path)



def assign_labels(request):
    import traceback
    global assigned_labels

    if request.method == 'POST':
        all_assigned = True
        for img in image_files:
            selected_label = request.POST.get(f"label_{img}")
            if selected_label:
                assigned_labels[img] = selected_label
            else:
                all_assigned = False
                break

        if not all_assigned:
            error_message = "Please assign a label to every image before continuing."
            return render(request, 'assign_labels.html', {
                'images': image_files,
                'labels': excel_data,
                'error_message': error_message
            })

        request.session['assigned_labels'] = assigned_labels

        # === BLOQUE PARA AGREGAR LABELS CON RUTA ABSOLUTA ===
        tmp_dir = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        for img in image_files:
            try:
                original_path = os.path.join(tmp_dir, img)
                output_path = os.path.join(tmp_dir, f"labeled_{img}")
                label_text = assigned_labels[img]

                if not os.path.exists(original_path):
                    print(f"[ADVERTENCIA] Archivo no encontrado: {original_path}")
                    continue

                agregar_label(original_path, label_text, output_path)
                print(f"[OK] Imagen guardada con label: {output_path}")

            except Exception as e:
                print(f"[ERROR] Falló al procesar {img}: {e}")
                traceback.print_exc()
        # ====================================================

        return redirect('upload_cover')

    return render(request, 'assign_labels.html', {'images': image_files, 'labels': excel_data})


def upload_cover(request):
    if request.method == 'POST':
        cover = request.FILES['cover']
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'photo_labeler_app/static/tmp'))
        cover_filename = fs.save(cover.name, cover)
        request.session['cover_image'] = cover_filename  # ← guarda solo el nombre, no la ruta completa
        return redirect('generate_pdf')
    return render(request, 'upload_cover.html')


# ESTE MANTIENE BORDES BLANCOS
# def add_image_resized(pdf, image_path):
#     from PIL import Image

#     img = Image.open(image_path)
#     img_width, img_height = img.size
#     img_ratio = img_width / img_height

#     # Área útil completa de la página (sin márgenes)
#     page_width = pdf.w
#     page_height = pdf.h
#     page_ratio = page_width / page_height

#     # Siempre ajustamos al alto
#     new_height = page_height
#     new_width = img_ratio * new_height

#     # Si el nuevo ancho es menor al ancho de página, centramos horizontalmente
#     x = (page_width - new_width) / 2 if new_width < page_width else 0
#     y = 0  # sin margen arriba/abajo

#     pdf.image(image_path, x=x, y=y, w=new_width, h=new_height)

# def generate_pdf(request):
#     from fpdf import FPDF
#     from PIL import Image
#     import os

#     assigned_labels = request.session.get('assigned_labels', {})
#     cover_image = request.session.get('cover_image', '')

#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)

#     tmp_dir = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'tmp')

#     # Portada
#     if cover_image:
#         cover_path = os.path.join(tmp_dir, cover_image)
#         if os.path.exists(cover_path):
#             pdf.add_page()
#             add_image_resized(pdf, cover_path)

#     # Imágenes con labels embebidos
#     for img_name in assigned_labels.keys():
#         labeled_img_path = os.path.join(tmp_dir, f"labeled_{img_name}")
#         if os.path.exists(labeled_img_path):
#             with Image.open(labeled_img_path) as img:
#                 width, height = img.size
#                 width_mm = width * 0.264583  # px → mm
#                 height_mm = height * 0.264583
#                 pdf.add_page()
#                 add_image_resized(pdf, labeled_img_path)

#     # Generar PDF final
#     output_path = os.path.join(tmp_dir, 'final_catalog.pdf')
#     pdf.output(output_path)

#     pdf_url = '/static/tmp/final_catalog.pdf'

#     # Limpiar archivos temporales EXCEPTO el PDF final
#     for filename in os.listdir(tmp_dir):
#         file_path = os.path.join(tmp_dir, filename)
#         if filename != 'final_catalog.pdf':
#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#             except Exception as e:
#                 print(f"Error borrando {file_path}: {e}")

#     return render(request, 'generate_pdf.html', {'pdf_url': pdf_url})

def add_image_fullpage(pdf, image_path):
    from PIL import Image

    img = Image.open(image_path)
    img_width, img_height = img.size

    # Convertir píxeles a milímetros
    width_mm = img_width * 0.264583
    height_mm = img_height * 0.264583

    # Agregar página del tamaño exacto de la imagen
    pdf.add_page(format=(width_mm, height_mm))
    # Insertar imagen ocupando todo
    pdf.image(image_path, x=0, y=0, w=width_mm, h=height_mm)

def generate_pdf(request):
    from fpdf import FPDF
    from PIL import Image
    import os

    assigned_labels = request.session.get('assigned_labels', {})
    cover_image = request.session.get('cover_image', '')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)  # sin saltos automáticos
    pdf.set_margins(0, 0, 0)  # sin márgenes

    tmp_dir = os.path.join(settings.BASE_DIR, 'photo_labeler_app', 'static', 'tmp')

    # Portada
    if cover_image:
        cover_path = os.path.join(tmp_dir, cover_image)
        if os.path.exists(cover_path):
            add_image_fullpage(pdf, cover_path)

    # Imágenes con labels embebidos
    for img_name in assigned_labels.keys():
        labeled_img_path = os.path.join(tmp_dir, f"labeled_{img_name}")
        if os.path.exists(labeled_img_path):
            add_image_fullpage(pdf, labeled_img_path)

    # Generar PDF final
    output_path = os.path.join(tmp_dir, 'final_catalog.pdf')
    pdf.output(output_path)

    pdf_url = '/static/tmp/final_catalog.pdf'

    # Limpiar archivos temporales EXCEPTO el PDF final
    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        if filename != 'final_catalog.pdf':
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error borrando {file_path}: {e}")

    return render(request, 'generate_pdf.html', {'pdf_url': pdf_url})
