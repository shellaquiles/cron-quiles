# Probar el sitio localmente

## Opción 1: Servidor Python (Recomendado)

```bash
cd gh-pages
python3 serve.py
```

Luego abre en tu navegador: http://localhost:8000/index.html

## Opción 2: Servidor HTTP simple

```bash $ ./proximos-eventos.sh
cd gh-pages
python3 -m http.server 8000
```

Luego abre en tu navegador: http://localhost:8000/index.html

## Opción 3: Generar archivos antes de probar

Si los archivos `cronquiles.ics` y `cronquiles.json` no existen, genera primero:

```bash
# Desde la raíz del proyecto
python main.py --json --output gh-pages/cronquiles.ics --json-output gh-pages/cronquiles.json
```

## Nota importante

No puedes abrir `index.html` directamente en el navegador (file://) porque el navegador bloquea las peticiones fetch por seguridad (CORS). Necesitas usar un servidor HTTP.
