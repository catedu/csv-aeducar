# csv-aeducar

## Web que genera CSVs listos para subir a Moodle.

### Instrucciones para centros de secundaria

Campos requeridos en el archivo .xls o .csv de entrada (respetando mayúsculas):
* N_GIR
* EMAIL
* NOMBRE
* APELLIDO1
* APELLIDO2
* DNI_ALUMNO o DNI en el caso de profesores

Campos opcionales:
* EMAIL_PADRE
* EMAIL_MADRE

### Instrucciones para centros de infantil y primaria

A final del día 10 de Septiembre de 2020.


```
docker-compose build
docker-compose up -d
```

Then open localhost:8501 in your browser.
