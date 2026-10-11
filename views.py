"""Controlador: reglas de negocio, CRUD y almacenamiento sin print/input."""
from pathlib import Path
from datetime import date
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

DATA = Path(__file__).resolve().parent / "data"
gestor_estudiantes = GestorJSON(str(DATA / "estudiantes.json"))
gestor_materias = GestorJSON(str(DATA / "materias.json"))
gestor_matriculas = GestorJSON(str(DATA / "matriculas.json"))
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")  # TUPLA: campos fijos
CAMPOS_MATERIA = ("nombre", "codigo", "creditos", "cupos")

def leer_objetos(gestor, modelo):
    return [modelo.desde_diccionario(d) for d in gestor.leer()]  # LISTA: colección ordenada

def obtener_por_id(gestor, modelo, identificador):
    return next((o for o in leer_objetos(gestor, modelo) if o.id == int(identificador)), None)

def buscar(gestor, modelo, termino, campos):
    t = str(termino).strip().casefold()
    return [o for o in leer_objetos(gestor, modelo)
            if t and any(t in str(getattr(o, campo)).casefold() for campo in campos)]

def siguiente_id(gestor):
    return max((int(d["id"]) for d in gestor.leer()), default=0) + 1

def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    if gestor.danado: return False
    registros.append(objeto.a_diccionario())
    return gestor.guardar(registros)

def reemplazar(gestor, objeto):
    registros = gestor.leer()
    if gestor.danado: return False
    for i, r in enumerate(registros):
        if r["id"] == objeto.id:
            registros[i] = objeto.a_diccionario()
            return gestor.guardar(registros)
    return False

def eliminar(gestor, identificador):
    registros = gestor.leer()
    if gestor.danado: return False
    restantes = [r for r in registros if r["id"] != int(identificador)]
    return len(restantes) != len(registros) and gestor.guardar(restantes)

def ids_registrados(gestor):
    return {r["id"] for r in gestor.leer()}  # CONJUNTO: ids únicos y pertenencia rápida

def indice_por_id(gestor, modelo):
    return {o.id: o for o in leer_objetos(gestor, modelo)}  # DICCIONARIO: índice id -> objeto

def carnets_registrados(excepto_id=None):
    return {str(r["carnet"]).casefold() for r in gestor_estudiantes.leer() if r["id"] != excepto_id}

def validar_estudiante(datos, id_actual=None):
    if any(not str(datos.get(k, "")).strip() for k in ("nombre", "apellido", "email", "carnet")):
        return "Nombre, apellido, email y carnet son obligatorios"
    if not es_email_valido(str(datos["email"])):
        return "Email inválido"
    if str(datos["carnet"]).casefold() in carnets_registrados(id_actual):
        return "Carnet repetido"
    usados = {str(r["email"]).casefold() for r in gestor_estudiantes.leer() if r["id"] != id_actual}
    if str(datos["email"]).casefold() in usados:
        return "Email repetido"
    return None

def crear_estudiante(datos):
    datos = {c: str(datos.get(c, "")).strip() for c in CAMPOS_ESTUDIANTE}
    error = validar_estudiante(datos)
    if error: return False, error
    o = Estudiante(siguiente_id(gestor_estudiantes), **datos)
    return (True, f"Estudiante creado, ID {o.id}") if guardar_nuevo(gestor_estudiantes, o) else (False, "Error al guardar")

def obtener_estudiantes(): return leer_objetos(gestor_estudiantes, Estudiante)
def obtener_estudiante(identificador): return obtener_por_id(gestor_estudiantes, Estudiante, identificador)
def buscar_estudiantes(termino): return buscar(gestor_estudiantes, Estudiante, termino, CAMPOS_ESTUDIANTE)

def actualizar_estudiante(identificador, cambios):
    o = obtener_estudiante(identificador)
    if not o: return False, "Estudiante inexistente"
    if not cambios or set(cambios) - set(CAMPOS_ESTUDIANTE): return False, "Campos inválidos o vacíos"
    datos = o.a_diccionario()
    datos.update({k: str(v).strip() for k, v in cambios.items()})
    error = validar_estudiante(datos, o.id)
    if error: return False, error
    nuevo = Estudiante.desde_diccionario(datos)
    return (True, "Estudiante actualizado") if reemplazar(gestor_estudiantes, nuevo) else (False, "Error al guardar")

def eliminar_estudiante(identificador):
    if any(m.estudiante_id == int(identificador) for m in obtener_matriculas()):
        return False, "Retire primero las matrículas del estudiante"
    return (True, "Estudiante eliminado") if eliminar(gestor_estudiantes, identificador) else (False, "No existe o no se pudo guardar")

def codigos_registrados(excepto_id=None):
    return {str(r["codigo"]).casefold() for r in gestor_materias.leer() if r["id"] != excepto_id}

def validar_materia(datos, id_actual=None):
    if not str(datos.get("nombre", "")).strip() or not str(datos.get("codigo", "")).strip():
        return "Nombre y código son obligatorios"
    if str(datos["codigo"]).casefold() in codigos_registrados(id_actual): return "Código repetido"
    try:
        creditos, cupos = int(datos["creditos"]), int(datos["cupos"])
        if not (1 <= creditos <= 10): return "Créditos entre 1 y 10"
        if not (0 <= cupos <= Materia.CUPOS_MAXIMOS): return "Cupos entre 0 y 30"
    except (ValueError, TypeError, KeyError): return "Créditos y cupos deben ser enteros"
    return None

def crear_materia(datos):
    datos = {c: str(datos.get(c, "")).strip() for c in CAMPOS_MATERIA}
    error = validar_materia(datos)
    if error: return False, error
    o = Materia(siguiente_id(gestor_materias), **datos)
    return (True, f"Materia creada, ID {o.id}") if guardar_nuevo(gestor_materias, o) else (False, "Error al guardar")

def obtener_materias(): return leer_objetos(gestor_materias, Materia)
def obtener_materia(identificador): return obtener_por_id(gestor_materias, Materia, identificador)
def buscar_materias(termino): return buscar(gestor_materias, Materia, termino, ("nombre", "codigo"))
def materias_sin_cupo(): return [m for m in obtener_materias() if not m.hay_cupo()]

def actualizar_materia(identificador, cambios):
    o = obtener_materia(identificador)
    if not o: return False, "Materia inexistente"
    if not cambios or set(cambios) - set(CAMPOS_MATERIA): return False, "Campos inválidos o vacíos"
    datos = o.a_diccionario(); datos.update({k: str(v).strip() for k, v in cambios.items()})
    error = validar_materia(datos, o.id)
    if error: return False, error
    activas = sum(m.materia_id == o.id for m in obtener_matriculas())
    if int(datos["cupos"]) + activas > Materia.CUPOS_MAXIMOS:
        return False, "Cupos libres + estudiantes matriculados superan 30"
    nuevo = Materia.desde_diccionario(datos)
    return (True, "Materia actualizada") if reemplazar(gestor_materias, nuevo) else (False, "Error al guardar")

def eliminar_materia(identificador):
    if any(m.materia_id == int(identificador) for m in obtener_matriculas()):
        return False, "Retire primero las matrículas de la materia"
    return (True, "Materia eliminada") if eliminar(gestor_materias, identificador) else (False, "No existe o no se pudo guardar")

def obtener_matriculas(): return leer_objetos(gestor_matriculas, Matricula)
def obtener_matricula(identificador): return obtener_por_id(gestor_matriculas, Matricula, identificador)

def crear_matricula(datos):
    try:
        eid, mid = int(datos["estudiante_id"]), int(datos["materia_id"])
        periodo = str(datos["periodo"]).strip()
        if not periodo: return False, "Período obligatorio"
        if not obtener_estudiante(eid): return False, "Estudiante inexistente"
        materia = obtener_materia(mid)
        if not materia: return False, "Materia inexistente"
        if not materia.hay_cupo(): return False, "No quedan cupos"
        if any(m.estudiante_id == eid and m.materia_id == mid and m.periodo.casefold() == periodo.casefold()
               for m in obtener_matriculas()):
            return False, "Matrícula duplicada para estudiante, materia y período"
        nota = float(str(datos.get("nota", 0)).replace(",", "."))
        if not Materia.es_nota_valida(nota): return False, "Nota fuera de 0 a 20"
        registro = Matricula(siguiente_id(gestor_matriculas), eid, mid, periodo,
                             nota, str(datos.get("fecha", "") or date.today().isoformat()))
        # Guardar matrícula y descontar cupo; si la segunda escritura falla, revertimos la primera.
        if not guardar_nuevo(gestor_matriculas, registro): return False, "Error al guardar matrícula"
        materia.ocupar_cupo()
        if not reemplazar(gestor_materias, materia):
            eliminar(gestor_matriculas, registro.id)
            return False, "Error al guardar cupos"
        return True, f"Matrícula creada, ID {registro.id}"
    except (KeyError, TypeError, ValueError): return False, "IDs o nota no válidos"

def registrar_nota(identificador, nota):
    m = obtener_matricula(identificador)
    if not m: return False, "Matrícula inexistente"
    try: valor = float(str(nota).replace(",", "."))
    except (ValueError, TypeError): return False, "Nota inválida"
    if not Materia.es_nota_valida(valor): return False, "Nota fuera de 0 a 20"
    m.nota = valor
    return (True, "Nota registrada") if reemplazar(gestor_matriculas, m) else (False, "Error al guardar")

def retirar_matricula(identificador):
    m = obtener_matricula(identificador)
    if not m: return False, "Matrícula inexistente"
    materia = obtener_materia(m.materia_id)
    if not materia: return False, "La materia ya no existe"
    if not eliminar(gestor_matriculas, m.id): return False, "Error al retirar"
    materia.liberar_cupo()
    if not reemplazar(gestor_materias, materia):
        guardar_nuevo(gestor_matriculas, m)
        return False, "Error al devolver cupo"
    return True, "Matrícula retirada y cupo liberado"

def matriculas_por_estudiante():
    grupos = {}  # DICCIONARIO DE LISTAS: agrupa por id, setdefault evita comprobaciones adicionales
    for m in obtener_matriculas(): grupos.setdefault(m.estudiante_id, []).append(m)
    return grupos

def promedio_de_estudiante(identificador):
    notas = [m.nota for m in matriculas_por_estudiante().get(int(identificador), [])]
    return round(sum(notas) / len(notas), 2) if notas else 0

def certificado(identificador):
    m = obtener_matricula(identificador)
    if not m: return None
    alumnos = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    e, a = alumnos.get(m.estudiante_id), materias.get(m.materia_id)
    if not e or not a: return None
    return (f"CERTIFICADO #{m.id}   periodo: {m.periodo}\n"
            f"Estudiante: {e.nombre_completo()} ({e.carnet})\n"
            f"Materia   : {a.nombre} ({a.codigo}) · {a.creditos} créditos\n"
            f"------------------------------------------\n"
            f"Nota      : {m.nota:g}\nEstado    : {m.estado()}")

def resumen():
    alumnos = obtener_estudiantes()
    return {"estudiantes": len(alumnos),
            "carreras": sorted({e.carrera for e in alumnos if e.carrera}),
            "sin_cupo": materias_sin_cupo(),
            "aprobadas": sum(m.esta_aprobada() for m in obtener_matriculas())}
