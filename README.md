# ColorizeAI - Deep Learning Image Colorization

Sistema profesional de colorización automática de imágenes en blanco y negro utilizando arquitecturas U-Net con Deep Learning.

## Descripción del Proyecto

ColorizeAI es una aplicación web que implementa modelos de redes neuronales convolucionales profundas para restaurar automáticamente el color en fotografías históricas y antiguas. El proyecto utiliza el dataset CelebA para entrenar tres variantes de arquitectura U-Net optimizadas para la colorización de rostros.

### Características Principales

- **3 Modelos Deep Learning**: U-Net Básica, U-Net Mejorada y U-Net RMSprop (recomendado)
- **Interfaz Web Profesional**: Landing page moderna con diseño responsivo
- **Procesamiento en Tiempo Real**: Colorización instantánea de imágenes
- **Arquitectura Monolítica**: Frontend y backend integrados para despliegue simple
- **Optimizado para Rostros**: Entrenado con 202,599+ imágenes del dataset CelebA

### Tecnologías Utilizadas

- **Backend**: Flask + TensorFlow/Keras 3.8
- **Frontend**: HTML5 + CSS3 + JavaScript vanilla
- **Modelos**: U-Net con skip connections
- **Datasets**: CelebA (img_align_celeba) + rostros complementarios

## Instalación Local

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Archivos de modelos `.h5` en la raíz del proyecto

### Windows (PowerShell)

```powershell
# Clonar el repositorio
git clone <tu-repo-url>
cd backendbn

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

### Linux/Mac

```bash
# Clonar el repositorio
git clone <tu-repo-url>
cd backendbn

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

Abre tu navegador en `http://localhost:5000`

## Despliegue en Render

### Opción 1: Modelos en el Repositorio (< 100 MB cada uno)

1. Asegúrate de que los archivos `.h5` estén en el repositorio
2. Haz push a GitHub
3. En Render:
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente `render.yaml`
   - Haz clic en "Deploy"

### Opción 2: Modelos en Almacenamiento Externo (Recomendado para archivos grandes)

1. Sube los modelos a un servicio de almacenamiento (AWS S3, Google Cloud Storage, etc.)
2. Obtén la URL pública de la carpeta (ejemplo: `https://mi-bucket.s3.amazonaws.com/models`)
3. En Render Dashboard:
   - Ve a tu servicio
   - Añade variable de entorno: `MODEL_BASE_URL` = `<tu-url-publica>`
4. La aplicación descargará los modelos automáticamente al iniciar

### Configuración de Variables de Entorno en Render

```
MODEL_BASE_URL=https://tu-bucket.s3.amazonaws.com/models
```

## Estructura del Proyecto

```
backendbn/
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias Python
├── render.yaml                     # Configuración Render
├── README.md                       # Este archivo
├── .gitignore                      # Archivos ignorados por Git
├── templates/
│   └── index.html                 # Landing page
├── static/
│   ├── style.css                  # Estilos profesionales
│   └── app.js                     # JavaScript frontend
└── best_model_UNet_*.h5           # Modelos entrenados (3 archivos)
```

## Modelos Disponibles

| Modelo | Descripción | Calidad | Velocidad |
|--------|-------------|---------|-----------|
| **Básica** | U-Net estándar | Media | Rápida |
| **Mejorada** | U-Net con BatchNorm + Dropout | Alta | Media |
| **RMSprop** | U-Net optimizada (recomendado) | Muy Alta | Media |

## Metodología de Entrenamiento

1. **Preprocesamiento**: Imagen RGB → Escala de grises
2. **Arquitectura**: U-Net con skip connections (encoder-decoder)
3. **Función de pérdida**: MSE (Mean Squared Error)
4. **Optimizadores**: Adam, RMSprop
5. **Métricas**: PSNR, SSIM

## Subir a GitHub

```bash
# Inicializar repositorio (si no existe)
git init

# Añadir archivos
git add .

# Primer commit
git commit -m "Initial commit: ColorizeAI proyecto completo"

# Conectar con GitHub (reemplaza con tu URL)
git remote add origin https://github.com/tu-usuario/tu-repo.git

# Push a GitHub
git branch -M main
git push -u origin main
```

## Notas Importantes

### Compatibilidad de Modelos

- Los modelos requieren **Keras 3.8.0** y **Protobuf 3.20.3**
- Si experimentas errores al cargar `.h5`, verifica las versiones instaladas
- La aplicación intenta múltiples estrategias de carga automáticamente

### Producción

Para producción, usa Gunicorn en lugar del servidor Flask de desarrollo:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
```

### Optimización

- Los modelos se cargan una vez al iniciar la aplicación
- Tamaño de entrada fijo: 128x128 píxeles
- Salida RGB: 128x128x3

## Solución de Problemas

### Modelos no cargan

```bash
pip install keras==3.8.0 protobuf==3.20.3
```

### Error de memoria en Render

- Usa el plan de pago de Render con más RAM
- O implementa carga diferida de modelos

### Timeout al iniciar

- Aumenta el timeout en `render.yaml` (actualmente 120s)
- O usa `MODEL_BASE_URL` para descarga paralela

## Licencia

Este proyecto es de código abierto.

## Contacto

Para preguntas o contribuciones, abre un issue en el repositorio de GitHub.