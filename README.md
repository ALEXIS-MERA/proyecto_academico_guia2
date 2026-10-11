# Sistema académico - Guía 2

Adaptado del proyecto `Trabajo-pr-ctico-experimental-main`. Se conservan las utilidades originales en `shared/` y el patrón de MVC.

Ejecutar desde esta carpeta: `python main.py`.

Estudiantes, materias y matrículas tienen almacenamiento JSON independiente en `data/`.

**Advertencia:** la inscripción y la liberación de cupo escriben dos archivos JSON diferentes; ante fallos abruptos del sistema no hay transacción atómica entre ambos. No editar manualmente archivos mientras se ejecuta.
