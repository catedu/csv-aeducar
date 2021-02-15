# csv-aeducar

## Web que genera CSVs listos para subir a Moodle.

Para probarlo en local:

```bash
docker build -t csv-aeducar .
docker run --rm -p 8501:8501 -v "$PWD"/src:/usr/src/app/src csv-aeducar
```
