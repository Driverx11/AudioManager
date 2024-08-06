from PyQt5.QtWidgets import QFileDialog
import tkinter as tk
from tkinter import messagebox
from position import *
import os, shutil
import csv

class Books(): 

    file_path = os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "db", "position.csv")
    folder_path = os.path.join(os.path.expanduser("~"), "OneDrive","Documentos", "Audible")

    def search_books(self):
        
        if self.folder_path:
            result = Books.recursive_search(self.folder_path)
        return result
    
    def search_chapters(self, book, extensions=[".mp3", ".wav", ".ogg"]):
        audio_files = []
        for root, dirs, files in os.walk(book):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    audio_files.append(os.path.join(root, file))
        return audio_files
    
    
    def add_book(self):
        #Select and copy the foulder to the audio's foulder destination
        carpeta_seleccionada = QFileDialog.getExistingDirectory(None, "Selecciona una carpeta")
        if carpeta_seleccionada:
            destino = self.folder_path
        
            destino_principal = self.folder_path

            # Obtener el nombre de la carpeta seleccionada
            nombre_carpeta = os.path.basename(carpeta_seleccionada)

            # Definir la ruta completa de destino para la carpeta seleccionada
            destino = os.path.join(destino_principal, nombre_carpeta)

            # Asegurarse de que la carpeta de destino principal existe
            if not os.path.exists(destino_principal):
                os.makedirs(destino_principal)

            # Asegurarse de que la carpeta de destino no existe para evitar errores
            if not os.path.exists(destino):
                os.makedirs(destino)

            # Copiar el contenido de la carpeta seleccionada al destino
            self.copiar_contenido(carpeta_seleccionada, destino)
            print(f'Carpeta copiada de {carpeta_seleccionada} a {destino}')

        else:
            print("No se seleccionó ninguna carpeta")


    def copiar_contenido(self, origen, destino):
        # Recorrer todos los archivos y directorios en el directorio de origen
        for item in os.listdir(origen):
            origen_item = os.path.join(origen, item)
            destino_item = os.path.join(destino, item)

            # Si es un directorio, copiar recursivamente
            if os.path.isdir(origen_item):
                if not os.path.exists(destino_item):
                    os.makedirs(destino_item)
                self.copiar_contenido(origen_item, destino_item)
            else:
                # Si es un archivo, copiarlo al directorio de destino
                shutil.copy2(origen_item, destino_item)


    def delete_book(self, selected_foulder):
        root = tk.Tk()
        root.withdraw()
        # Show dialog box
        respuesta = messagebox.askyesno('Confirmar Eliminación', '¿Estás seguro de eliminar el libro?')
        # if true deleate the book
        if respuesta:
            # Deleate the book
            shutil.rmtree(selected_foulder)

            
    def recursive_search(foulder_path):
        books = []
        # Escanea los contenidos del directorio actual
        for entry in os.scandir(foulder_path):
            if entry.is_dir():
                # Si es un directorio, verifica si contiene archivos
                has_files = False
                for sub_entry in os.scandir(entry.path):
                    if sub_entry.is_file():
                        has_files = True
                        break
                
                if has_files:
                    books.append(entry.path)
                # Llama recursivamente a la función si encuentra subdirectorios
                else:
                    books.extend(Books.recursive_search(entry.path))
        
        return books
    
    def save_position(self, position):
        with open(self.file_path, "w") as f:
            f.write(f"{position.book}, {position.chapter}, {position.milisec}")


    def csv_vacio(self):
        with open(self.file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            # Intenta leer la primera línea
            try:
                first_row = next(csv_reader)
                # Si se puede leer una línea, no está vacío
                return False
            except StopIteration:
                # Si no se puede leer ninguna línea, está vacío
                return True
        

    def obtain_position(self):
        position = Position("book", "chapter", 0)
        if not os.path.exists(self.file_path): 
            with open(self.file_path, "w") as f:
                f.write(f"{position.book}, {position.chapter}, {position.milisec}")
            return position
        else:
            if not self.csv_vacio():
                with open(self.file_path, "r") as f:
                    line = f.read()
                    book, chapter, milisec = line.split(", ")
                    position = Position(book, chapter, int(milisec))
                print(f"SI {position.chapter, position.book, int(position.milisec)}")
                return position
                
            else:
                with open(self.file_path, "w") as f:
                    f.write(f"{position.book}, {position.chapter}, {position.milisec}")
                return position
            
            


                    