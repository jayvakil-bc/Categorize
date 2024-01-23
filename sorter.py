from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
import threading
from time import sleep
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


source_dir = ""

dest_dir_sfx = ""
dest_dir_music = ""
dest_dir_video = ""
dest_dir_image = ""
dest_dir_documents = ""
dest_dir_code = ""
default_dest_dir = ""


image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]

audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]

document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

code_extensions = [".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".php", ".rb", ".go", ".swift", ".vb", ".sql", ".pl", ".lua", ".sh", ".bat", ".zip", ".h"]

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name

def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)



class MoverHandler(FileSystemEventHandler):
    
    def on_modified(self, event):
        logging.info("On modified event")
        with scandir(source_dir) as entries:
            threads = []
            for entry in entries:
                name = entry.name
                moved = False
                for extension_list, dest_dir in zip([audio_extensions, video_extensions, image_extensions, document_extensions, code_extensions],
                                       [dest_dir_music, dest_dir_video, dest_dir_image, dest_dir_documents, dest_dir_code]):
                    if any(name.endswith(ext) or name.endswith(ext.upper()) for ext in extension_list):
                        self.move_file(entry, name, dest_dir)
                        moved = True
                        break

            if not moved:
                
                self.move_file(entry, name, default_dest_dir)

    def move_file(self, entry, name, dest):
        filename, extension = splitext(name)
        dest_file_path = join(dest, name)
        counter = 1
        while exists(dest_file_path):
            name = f"{filename}({str(counter)}){extension}"
            dest_file_path = join(dest, name)
            counter += 1

        move(entry, dest_file_path)
        logging.info(f"Moved {splitext(name)[1][1:].upper()} file: {name} to {dest}")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()