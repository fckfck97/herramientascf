import os
import io
import zipfile
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import tempfile
import shutil
from django.conf import settings

class Inicio(View):
    template_name = 'index/template.html'
    
    def get(self, request):
        return render(request,self.template_name)
    
class CambioNombreImagenesView(View):
    template_name = 'cambio/template.html'
        
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        archivos_carpeta = request.FILES.getlist('ruta_carpeta')  # Obtener una lista de archivos
        #por si vienen espacios los eliminamos y colocamos un _
        nombreimg = request.POST.get("nombreimg")
        split_words = nombreimg.split()
        result = "_".join(split_words)
        
        ruta_carpeta = self.guardar_carpeta_temporal(archivos_carpeta)
        zip_file = self.procesar_imagenes(ruta_carpeta,result)
        self.eliminar_carpeta_temporal(ruta_carpeta)  # Eliminar la carpeta temporal
        return self.enviar_archivo_comprimido(zip_file,result)
    
    def guardar_carpeta_temporal(self, archivos_carpeta):
        directorio_temporal = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)  # Crear carpeta temporal dentro de la carpeta MEDIA_ROOT
        # Guardar todas las imágenes en la carpeta temporal
        for archivo in archivos_carpeta:
            ruta_temporal = os.path.join(directorio_temporal, archivo.name)
            with open(ruta_temporal, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)
        return directorio_temporal
    
    def procesar_imagenes(self, ruta_carpeta,nombreimg):
        if ruta_carpeta is None:
            return None
        contador = 1
        in_memory_zip = io.BytesIO()
        ruta_temporal_procesadas = os.path.join(ruta_carpeta, 'procesadas')  # Carpeta para las imágenes procesadas
        os.makedirs(ruta_temporal_procesadas, exist_ok=True)  # Crear la carpeta de imágenes procesadas
        for nombre_archivo in os.listdir(ruta_carpeta):
            ruta_completa_archivo = os.path.join(ruta_carpeta, nombre_archivo)
            if os.path.isfile(ruta_completa_archivo) and nombre_archivo.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                imagen = Image.open(ruta_completa_archivo)
                nuevo_nombre = f"{nombreimg}-{contador}.jpg"
                # Guardar la imagen procesada en la carpeta de imágenes procesadas
                ruta_procesada = os.path.join(ruta_temporal_procesadas, nuevo_nombre)
                imagen.save(ruta_procesada)
                imagen.close()
                contador += 1
        # Crear el archivo ZIP y agregar todas las imágenes procesadas
        with zipfile.ZipFile(in_memory_zip, 'w') as zipf:
            for nombre_archivo in os.listdir(ruta_temporal_procesadas):
                ruta_completa_archivo = os.path.join(ruta_temporal_procesadas, nombre_archivo)
                zipf.write(ruta_completa_archivo, nombre_archivo)
        in_memory_zip.seek(0)
        return in_memory_zip
    
    def enviar_archivo_comprimido(self, zip_file,nombreimg):
        if zip_file is None:
            return None
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="imagenes_renombradas_{nombreimg}.zip"'
        return response
    
    def eliminar_carpeta_temporal(self, ruta_carpeta):
        if ruta_carpeta is not None:
            shutil.rmtree(ruta_carpeta)

class ReductorImagenesView(View):
    template_name = "reductor/template.html"
    
    def get(self, request):
        return render(request,self.template_name)
    
    def post(self, request):
        nuevo_tamano = (800, 600)
        archivos_carpeta = request.FILES.getlist('ruta_carpeta')  # Obtener una lista de archivos        
        ruta_carpeta = self.guardar_carpeta_temporal(archivos_carpeta)
        zip_file = self.procesar_imagenes(ruta_carpeta, nuevo_tamano)
        self.eliminar_carpeta_temporal(ruta_carpeta)  # Eliminar la carpeta temporal
        return self.enviar_archivo_comprimido(zip_file)
    
    def guardar_carpeta_temporal(self, archivos_carpeta):
        directorio_temporal = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)  # Crear carpeta temporal dentro de la carpeta MEDIA_ROOT
        # Guardar todas las imágenes en la carpeta temporal
        for archivo in archivos_carpeta:
            ruta_temporal = os.path.join(directorio_temporal, archivo.name)
            with open(ruta_temporal, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)
        return directorio_temporal
    
    def procesar_imagenes(self, ruta_carpeta, nuevo_tamano):
        in_memory_zip = io.BytesIO()
        # Iterar a través de las imágenes en la ruta
        for imagen_nombre in os.listdir(ruta_carpeta):
            # Comprobar si el nombre de la imagen contiene la cadena "reduccion"
            if "reduccion" not in imagen_nombre:
                # Abrir la imagen usando PIL
                imagen = Image.open(os.path.join(ruta_carpeta, imagen_nombre))
                # Reducir el tamaño de la imagen mientras se mantiene la relación de aspecto
                imagen.thumbnail(nuevo_tamano, Image.ANTIALIAS)
                # Guardar la imagen en la misma ruta con un nuevo nombre
                imagen_guardar = os.path.splitext(imagen_nombre)[0] + 'reduccion' + os.path.splitext(imagen_nombre)[1]
                imagen.save(os.path.join(ruta_carpeta, imagen_guardar), optimize=True, quality=95)
                # Eliminar la imagen original que no tiene la reducción en su nombre
                os.remove(os.path.join(ruta_carpeta, imagen_nombre))
        # Crear el archivo ZIP y agregar todas las imágenes procesadas
        with zipfile.ZipFile(in_memory_zip, 'w') as zipf:
            for nombre_archivo in os.listdir(ruta_carpeta):
                ruta_completa_archivo = os.path.join(ruta_carpeta, nombre_archivo)
                zipf.write(ruta_completa_archivo, nombre_archivo)
        in_memory_zip.seek(0)
        return in_memory_zip
    def enviar_archivo_comprimido(self, zip_file):
        if zip_file is None:
            return None
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="imagenes_reducidas.zip"'
        return response
    
    def eliminar_carpeta_temporal(self, ruta_carpeta):
        if ruta_carpeta is not None:
            shutil.rmtree(ruta_carpeta)