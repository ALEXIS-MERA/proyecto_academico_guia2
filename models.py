from datetime import date

class ModeloBase:
    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        copia = dict(datos)
        identificador = copia.pop("id")
        return cls(identificador, **copia)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"

class Persona(ModeloBase):
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def obtener_nombre_completo(self):
        return self.nombre_completo()

    def a_diccionario(self):
        return {**super().a_diccionario(), "nombre": self.nombre,
                "apellido": self.apellido, "email": self.email}

    def etiqueta(self):
        return self.nombre_completo()

class Estudiante(Persona):
    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        return {**super().a_diccionario(), "carnet": self.carnet,
                "carrera": self.carrera}

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera}"

class Materia(ModeloBase):
    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro, nombre, codigo, creditos=1, cupos=30):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        try:
            n = float(valor)
            return 0 <= n <= 20
        except (ValueError, TypeError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if not self.hay_cupo():
            return False
        self.cupos -= 1
        return True

    def liberar_cupo(self):
        if self.cupos >= self.CUPOS_MAXIMOS:
            return False
        self.cupos += 1
        return True

    def a_diccionario(self):
        return {**super().a_diccionario(), "nombre": self.nombre,
                "codigo": self.codigo, "creditos": self.creditos, "cupos": self.cupos}

    def etiqueta(self):
        return f"{self.nombre} · {self.codigo} · {self.cupos} cupos"

class Matricula(ModeloBase):
    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        return {**super().a_diccionario(), "estudiante_id": self.estudiante_id,
                "materia_id": self.materia_id, "periodo": self.periodo,
                "nota": self.nota, "fecha": self.fecha}

    def etiqueta(self):
        return f"Estudiante {self.estudiante_id} · Materia {self.materia_id} · {self.periodo} · {self.estado()}"
