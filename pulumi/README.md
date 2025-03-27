# Arquitectura del Proyecto SparkProcessNLP

Este documento describe la arquitectura y componentes principales del proyecto SparkProcessNLP, una aplicación para búsqueda y procesamiento de tweets.

![architecture_project](architecture_project.png)

## Estructura del Proyecto

```
SparkProcessNLP/
├── frontend/            # Interfaz de usuario en Streamlit
│   ├── app.py             # Aplicación principal de Streamlit
│   ├── Dockerfile         # Configuración de Docker para el frontend
│   └── .env              # Variables de entorno del frontend
└── pulumi/                # Infraestructura como código con Pulumi
    ├── index.ts           # Configuración principal de Pulumi
    ├── package.json       # Dependencias de Pulumi
    └── .env              # Variables de entorno de Pulumi
```

## Componentes Principales

### 1. Frontend (Streamlit)

La interfaz de usuario está construida con Streamlit y proporciona:
- Formulario interactivo para búsqueda de tweets
- Visualización de resultados
- Filtros y opciones de búsqueda

**Variables de Entorno:**
- `BACKEND_URL`: URL del servicio backend

**Características:**
- Interfaz intuitiva y responsiva
- Visualización de datos en tablas
- Filtros dinámicos
- Manejo de errores y estados de carga

### 2. Infraestructura (Pulumi)

La infraestructura está definida como código usando Pulumi y desplegada en Google Cloud Platform:

**Componentes:**
- Google Container Registry (GCR) para almacenamiento de imágenes Docker
- Cloud Run para ejecución de servicios
- Configuración de IAM y permisos

**Variables de Entorno:**
- `apifyToken`: Token secreto de Apify (configurado en Pulumi)
- `backendUrl`: URL del servicio backend (configurado en Pulumi)
- `GCP_SERVICE_ACCOUNT_KEY`: Credenciales de GCP

## Flujo de Datos

1. El usuario interactúa con la interfaz de Streamlit
2. El frontend recibe los párametros de busqueda, procesa la solicitud usando la API de Apify y consume el backend para hacer la inferencia.
4. Los resultados se envían de vuelta al frontend
5. El frontend visualiza los resultados

## Despliegue

### Requisitos Previos
- Cuenta de Google Cloud Platform
- Cuenta de Apify
- Pulumi CLI instalado
- Docker instalado

### Pasos de Despliegue

1. **Configurar Variables de Entorno:**
   - Crea un archivo .env basandote en el arhivo .env_example
   - Llena los valores de las variables

2. **Desplegar Infraestructura:**
   ```bash
   cd pulumi
   pulumi up
   ```

3. **Verificar Despliegue:**
   - Acceder a la URL del frontend proporcionada por Pulumi
   - Verificar que los servicios estén funcionando correctamente

## Seguridad

- Las variables de entorno sensibles se manejan como secretos en Pulumi
- Los servicios de Cloud Run tienen configurados los permisos IAM necesarios
- Las credenciales de GCP se manejan de forma segura
- Las imágenes Docker se almacenan en GCR

## Mantenimiento

### Actualización de Servicios
1. Modificar el código en el servicio correspondiente
2. Reconstruir la imagen Docker
3. Desplegar con `pulumi up`

### Monitoreo
- Utilizar Google Cloud Monitoring para supervisar los servicios
- Revisar logs en Cloud Logging
- Monitorear costos en Google Cloud Billing

## Consideraciones de Escalabilidad

- Cloud Run escala automáticamente según la demanda
- Los servicios están diseñados para ser stateless
- Las imágenes Docker están optimizadas para tamaño y rendimiento
- Se utiliza caching cuando es apropiado

## Solución de Problemas

### Problemas Comunes
1. **Error de Conexión al Backend:**
   - Verificar la URL del backend en las variables de entorno
   - Comprobar que el servicio esté funcionando

2. **Error de Autenticación con Apify:**
   - Verificar el token en las variables de entorno
   - Comprobar la validez del token

3. **Problemas de Despliegue:**
   - Revisar logs de Pulumi
   - Verificar permisos de GCP
   - Comprobar configuración de Docker
