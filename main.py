from shared.herramientas import imprimir_titulo, imprimir_error, imprimir_exito, imprimir_info, confirmar
import views as v

def pausa():
    input("\nPresione Enter para continuar...")

def mostrar_lista(objetos):
    if not objetos: return imprimir_info("No hay registros")
    for o in objetos: print(o)  

def mostrar_detalle(objeto):
    if objeto is None: return imprimir_error("Registro inexistente")
    for campo, valor in objeto.a_diccionario().items(): print(f"  {campo}: {valor}")

def numero(pregunta):
    try: return int(input(pregunta).strip())
    except ValueError:
        imprimir_error("Debe escribir un número entero")
        return None

def ejecutar(resultado):
    ok, mensaje = resultado
    (imprimir_exito if ok else imprimir_error)(mensaje)

def menu_crud(nombre, campos, crear, todos, uno, buscar, actualizar, borrar):
    while True:
        imprimir_titulo(f"GESTIÓN DE {nombre.upper()}")
        print("1. Crear\n2. Ver todos\n3. Buscar\n4. Ver por ID\n5. Actualizar\n6. Eliminar\n0. Volver")
        op = input("Opción: ").strip()
        if op == "0": return
        if op == "1":
            datos = {c: input(f"{c.capitalize()}: ").strip() for c in campos}
            ejecutar(crear(datos))
        elif op == "2": mostrar_lista(todos())
        elif op == "3": mostrar_lista(buscar(input("Término: ")))
        elif op == "4":
            i = numero("ID: ")
            if i is not None: mostrar_detalle(uno(i))
        elif op == "5":
            i = numero("ID a actualizar: ")
            if i is not None:
                objeto = uno(i)
                if not objeto: imprimir_error("No existe")
                else:
                    print("Deje vacío para mantener el valor actual")
                    cambios = {}
                    for c in campos:
                        valor = input(f"{c} [{getattr(objeto,c)}]: ").strip()
                        if valor: cambios[c] = valor
                    ejecutar(actualizar(i, cambios))
        elif op == "6":
            i = numero("ID a eliminar: ")
            if i is not None and confirmar("¿Eliminar este registro?"): ejecutar(borrar(i))
        else: imprimir_error("Opción inválida")
        pausa()

def menu_matriculas():
    while True:
        imprimir_titulo("MATRÍCULAS")
        print("1. Matricular\n2. Ver todas\n3. Registrar nota\n4. Ver certificado\n5. Retirar matrícula\n0. Volver")
        op = input("Opción: ").strip()
        if op == "0": return
        if op == "1":
            datos = {campo: input(f"{campo}: ").strip()
                     for campo in ("estudiante_id", "materia_id", "periodo")}
            ejecutar(v.crear_matricula(datos))
        elif op == "2": mostrar_lista(v.obtener_matriculas())
        elif op == "3":
            i = numero("ID de matrícula: ")
            if i is not None: ejecutar(v.registrar_nota(i, input("Nota 0-20: ")))
        elif op == "4":
            i = numero("ID de matrícula: ")
            if i is not None: print(v.certificado(i) or "Certificado no encontrado")
        elif op == "5":
            i = numero("ID de matrícula: ")
            if i is not None and confirmar("¿Retirar matrícula?"): ejecutar(v.retirar_matricula(i))
        else: imprimir_error("Opción inválida")
        pausa()

def mostrar_resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    r = v.resumen()
    print("Estudiantes:", r["estudiantes"])
    print("Carreras:", ", ".join(r["carreras"]) or "Ninguna")
    print("Materias sin cupo:", len(r["sin_cupo"]))
    print("Matrículas aprobadas:", r["aprobadas"])
    pausa()

def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO · GUÍA 2")
        print("1. Estudiantes\n2. Materias\n3. Matrículas\n4. Resumen\n0. Salir")
        op = input("Seleccione una opción: ").strip()
        if op == "0": break
        elif op == "1": menu_crud("Estudiantes", v.CAMPOS_ESTUDIANTE, v.crear_estudiante,
                                  v.obtener_estudiantes, v.obtener_estudiante, v.buscar_estudiantes,
                                  v.actualizar_estudiante, v.eliminar_estudiante)
        elif op == "2": menu_crud("Materias", v.CAMPOS_MATERIA, v.crear_materia,
                                  v.obtener_materias, v.obtener_materia, v.buscar_materias,
                                  v.actualizar_materia, v.eliminar_materia)
        elif op == "3": menu_matriculas()
        elif op == "4": mostrar_resumen()
        else: imprimir_error("Opción inválida")

if __name__ == "__main__":
    try: main()
    except (KeyboardInterrupt, EOFError): print("\nPrograma interrumpido")
