# Configuración de Google Calendar

Esta guía te ayudará a configurar la publicación automática de eventos en Google Calendar.

## Requisitos

1. Cuenta de Google
2. Acceso a Google Cloud Console
3. Python con las dependencias instaladas

## Pasos de Configuración

### 1. Crear un Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el ID del proyecto

### 2. Habilitar Google Calendar API

1. En Google Cloud Console, ve a **APIs & Services** > **Library**
2. Busca "Google Calendar API"
3. Haz clic en **Enable**

### 3. Crear Credenciales OAuth2

1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en **Create Credentials** > **OAuth client ID**
3. Si es la primera vez, configura la pantalla de consentimiento:
   - Tipo de aplicación: **External**
   - Nombre de la app: "Cron-Quiles"
   - Email de soporte: tu email
   - Agrega tu email como usuario de prueba
4. Tipo de aplicación: **Desktop app**
5. Nombre: "Cron-Quiles CLI"
6. Haz clic en **Create**
7. Descarga el archivo JSON de credenciales

### 4. Guardar las Credenciales

1. Renombra el archivo descargado a `credentials.json`
2. Muévelo a la carpeta `config/` del proyecto:
   ```bash
   mv ~/Downloads/credentials.json config/credentials.json
   ```

### 5. Primera Autenticación

La primera vez que ejecutes el script con `--google-calendar`, se abrirá un navegador para autenticarte:

```bash
python main.py --google-calendar
```

1. Se abrirá una ventana del navegador
2. Inicia sesión con tu cuenta de Google
3. Autoriza el acceso a Google Calendar
4. El token se guardará en `config/token.json` para futuras ejecuciones

## Uso

### Publicar eventos en tu calendario principal

```bash
python main.py --google-calendar
```

### Publicar en un calendario específico

Primero, obtén el ID del calendario desde Google Calendar (Settings > Calendars > [Tu calendario] > Calendar ID):

```bash
python main.py --google-calendar --google-calendar-id "tu-calendar-id@group.calendar.google.com"
```

### Simular sin publicar (dry run)

```bash
python main.py --google-calendar --dry-run
```

### Combinar con otras opciones

```bash
python main.py --google-calendar --json --verbose
```

## Seguridad

- **NO** subas `credentials.json` o `token.json` al repositorio
- Ambos archivos están en `.gitignore` por defecto
- El token contiene acceso a tu calendario, mantenlo seguro
- Si comprometes el token, revócalo desde Google Cloud Console

## Troubleshooting

### Error: "Archivo de credenciales no encontrado"

Asegúrate de que `config/credentials.json` existe y tiene el formato correcto.

### Error: "Token expirado"

Elimina `config/token.json` y vuelve a autenticarte:
```bash
rm config/token.json
python main.py --google-calendar
```

### Error: "Insufficient permissions"

Asegúrate de que la API de Google Calendar está habilitada en tu proyecto.

### Límites de la API

Google Calendar API tiene límites de cuota:
- 1,000,000 requests por día (suficiente para uso personal)
- 10 requests por segundo por usuario

Si publicas muchos eventos, el script maneja los límites automáticamente.

## Calendarios Compartidos

Para publicar en un calendario compartido:
1. Asegúrate de tener permisos de escritura
2. Usa el Calendar ID del calendario compartido
3. El formato es: `calendar-id@group.calendar.google.com`
