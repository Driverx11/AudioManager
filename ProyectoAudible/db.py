import os

class Books(): 

    def search_books(self):
        folder_path = os.path.join(os.path.expanduser("~"), "OneDrive","Documentos", "Audible")
        if folder_path:
            result = Books.recursive_search(folder_path)
        return result
    
    def search_chapters(self, book, extensions=[".mp3", ".wav", ".ogg"]):
        audio_files = []
        for root, dirs, files in os.walk(book):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    audio_files.append(os.path.join(root, file))
        return audio_files
    

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


    def save_position(self, position, book, chapter):
        with open(os.path.join(os.path.expanduser("~"), "OneDrive","Documentos", "position.csv"), "w") as f:
            f.write(f"{book}, {chapter}, {position}")