# Control Logístico de Equipos

## Descripción
Aplicación para gestionar el control logístico de equipos, permitiendo registrar, actualizar y monitorear el inventario de equipos.

## Requisitos
- Python 3.x
- Flask (o framework web utilizado)
- Google Sheets

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Características

- Registro de equipos
- Actualización de estado
- Búsqueda y filtrado
- Reportes de inventario
- Gestión de usuarios
- Auditoría de cambios

## Estructura del Proyecto

```
Control Logístico de Equipos/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos (CSS, JS)
└── database/              # Configuración de base de datos
```

## API Endpoints

### Equipos
- `GET /api/equipos` - Listar todos los equipos
- `POST /api/equipos` - Crear nuevo equipo
- `GET /api/equipos/<id>` - Obtener detalles de equipo
- `PUT /api/equipos/<id>` - Actualizar equipo
- `DELETE /api/equipos/<id>` - Eliminar equipo

## Configuración

Editar las variables de entorno en `app.py` o crear un archivo `.env`:

```env
DEBUG=True
DATABASE_URL=sqlite:///equipos.db
SECRET_KEY=tu-clave-secreta
```

## Contribución

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo licencia MIT.

## Soporte

Para reportar problemas o sugerencias, crear un issue en el repositorio.
<img width="1880" height="851" alt="image" src="https://github.com/user-attachments/assets/b6c8bdec-c82c-4739-a725-ed8f9d4390fe" />

