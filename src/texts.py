TEXTS = {
    "intro": """
### **¡ATENCIÓN!** No editéis los datos descargados de GIR o SIGAD antes de subirlos a esta aplicación. Podéis editar posteriormente el archivo resultante que esta aplicación os dará.

Esta aplicación sube los datos a un servidor propiedad del Gobierno de Aragón, para su tramiento y devolución al usuario.

Una vez devuelto el .csv, no se conserva ningún dato en el servidor.

*Más instrucciones desplegando el menú de la izquierda*
""",
    "alumnado": """## Descarga tu .xls del SIGAD

En Utilidades -> Informes -> ALUM -> descarga Listado completo de alumnos con todos sus datos.

Campos mínimos requeridos en el archivo .xls:
* N_GIR
* EMAIL (aunque haya registros vacíos)
* NOMBRE
* APELLIDO1
* APELLIDO2

Campos opcionales:
* EMAIL_PADRE
* EMAIL_MADRE

""",
    "profesorado": """## Descarga tu .xls del SIGAD

### Sería necesario añadir el campo mail. Si alguien sabe cómo sacar estos datos del SIGAD incluyendo el mail del profesorado, que envíe un correro a asesor@catedu.es para que actualice el funcionamiento de esta aplicación, indicándome cómo ha obtenido estos datos y un .xls de prueba aunque sea con sólo un registro y datos falsos. De momento todos los registros tendrán el mismo mail. El profesorado podrá acceder a su perfil y modificarlo ya en su moodle.

En Personal -> Búsqueda -> Exportar -> descarga Listado completo de profesores con todos sus datos.

Campos mínimos requeridos en el archivo .xls:
* Nombre
* Apellido 1
* Apellido 2
* Nº documento

Puedes probar el funcionamiento descargando [este archivo para tests](https://github.com/catedu/csv-aeducar/raw/master/src/prueba-profesorado.xls).
""",
    "en_progreso": """## Servicio no disponbile.

Este servicio estará disponible durante la semana del 14 al 18 de Septiembre

    """,
    "alumnado_GIR": """## Descarga tu .xls del GIR

Campos mínimos requeridos en el archivo .xls:
* Nº Alumno GIR
* Nombre
* Apellidos
* Grupo

### Si en tu centro habéis cambiado los nombres cortos de los cursos, los alumnos se crearán en la plataforma, pero no se matricularán en los cursos.
""",
    "maestros_GIR": """## Descarga tu .xls del GIR

Campos mínimos requeridos en el archivo .xls:
* Nº Documento
* Nombre
* Apellidos

Campos opcionales:
* grupo

De momento todos los registros tendrán el mismo mail. Los maestros podrán acceder a su perfil y modificarlo ya en su moodle.

Para que las tutoras se matriculen en sus cursos, cada centro debe haber asignado a cada tutora su grupo en GIR.

""",
}


columns_to_add = [
    "course1",
    "group1",
    "role1",
    "course2",
    "group2",
    "role2",
    "course3",
    "group3",
    "role3",
    "course4",
    "group4",
    "role4",
    "course5",
    "group5",
    "role5",
    "course6",
    "group6",
    "role6",
    "course7",
    "group7",
    "role7",
    "course8",
    "group8",
    "role8",
    "course9",
    "group9",
    "role9",
    "course10",
    "group10",
    "role10",
    "course11",
    "group11",
    "role11",
    "course12",
    "group12",
    "role12",
    "course13",
    "group13",
    "role13",
]

text2num = {
    "1": "primero",
    "2": "segundo",
    "3": "tercero",
    "4": "cuarto",
    "5": "quinto",
    "6": "sexto",
}

cursos_inf = [
    "proyecto6",
    "proyecto4",
    "proyecto3",
    "proyecto2",
    "proyecto1",
    "english",
    "proyecto5",
]

cursos_prim = [
    "lengua",
    "sociales",
    "matematicas",
    "ingles",
    "edfisica",
    "artistica",
    "ciencias",
]
