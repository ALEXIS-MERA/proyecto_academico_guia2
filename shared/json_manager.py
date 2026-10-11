import json
import os


class GestorJSON:
    def __init__(self, ruta):
        self.ruta = ruta
        self.danado = False
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def leer(self):
        if not os.path.exists(self.ruta):
            self.danado = False
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.danado = not isinstance(datos, list)
            return [] if self.danado else datos
        except (json.JSONDecodeError, OSError):
            self.danado = True
            return []

    def guardar(self, datos):
        if self.danado:
            return False
        temporal = self.ruta + ".tmp"
        try:
            with open(temporal, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            os.replace(temporal, self.ruta)
            return True
        except (TypeError, OSError):
            return False
