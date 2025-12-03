# Guía Rápida: Despliegue GitHub + Render

## 1. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `colorizeai` (o el que prefieras)
3. Descripción: "Sistema de colorización automática de imágenes con Deep Learning"
4. Mantén el repositorio **Público** (para Render Free Tier)
5. NO inicialices con README, .gitignore o licencia (ya los tenemos)
6. Haz clic en "Create repository"

## 2. Conectar y Subir al Repositorio

Copia la URL de tu repositorio (ejemplo: `https://github.com/tu-usuario/colorizeai.git`)

Ejecuta en PowerShell:

```powershell
cd d:\proyectos\backendbn

# Conectar con tu repositorio de GitHub (reemplaza con tu URL)
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git

# Subir el código
git push -u origin main
```

## 3. Opciones para los Modelos .h5

### Opción A: Incluir modelos en el repositorio (si son < 100 MB cada uno)

Ya están incluidos en el commit. Simplemente verifica que se subieron correctamente.

### Opción B: Usar almacenamiento externo (RECOMENDADO para modelos grandes)

1. Elimina los modelos del repositorio:
   ```powershell
   git rm --cached *.h5
   git commit -m "Remove large model files"
   git push
   ```

2. Sube los modelos a un servicio cloud:
   - **AWS S3**: Crea un bucket público y sube los 3 archivos .h5
   - **Google Cloud Storage**: Similar, bucket público
   - **Alternativa gratuita**: https://www.dropbox.com o Google Drive (asegúrate de obtener enlaces directos)

3. Obtén la URL base de la carpeta (sin incluir el nombre del archivo)
   Ejemplo: `https://mi-bucket.s3.amazonaws.com/models`

## 4. Desplegar en Render

1. Ve a https://render.com y crea una cuenta (gratis)

2. En el Dashboard, haz clic en "New +" → "Web Service"

3. Conecta tu repositorio de GitHub:
   - Autoriza a Render para acceder a tu GitHub
   - Selecciona el repositorio `colorizeai`

4. Configuración del servicio:
   - **Name**: `colorizeai` (o el que prefieras)
   - **Region**: Oregon (US West) - más cercano
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

5. Variables de Entorno (si usaste Opción B para modelos):
   - Haz clic en "Advanced"
   - Añade variable de entorno:
     - **Key**: `MODEL_BASE_URL`
     - **Value**: `https://tu-bucket.s3.amazonaws.com/models` (tu URL)

6. Selecciona el plan **Free**

7. Haz clic en "Create Web Service"

## 5. Esperar el Despliegue

- Render comenzará a construir y desplegar tu aplicación
- El proceso toma entre 5-10 minutos
- Puedes ver los logs en tiempo real
- Una vez completado, obtendrás una URL pública: `https://colorizeai.onrender.com`

## 6. Verificación

1. Abre la URL de tu aplicación
2. Sube una imagen en blanco y negro
3. Selecciona un modelo (RMSprop recomendado)
4. Haz clic en "Colorear Imagen"
5. Verifica que la colorización funcione correctamente

## Solución de Problemas

### Si el despliegue falla:

1. **Error de memoria**: Usa el plan de pago de Render con más RAM
2. **Timeout al cargar modelos**: Asegúrate de que `MODEL_BASE_URL` esté configurado correctamente
3. **Errores de dependencias**: Verifica que `requirements.txt` esté actualizado

### Logs en Render:

- Ve a tu servicio en Render
- Haz clic en "Logs" para ver errores en tiempo real
- Busca líneas que digan "Loaded <modelo> with..."

## Actualizaciones Futuras

Para actualizar tu aplicación después de hacer cambios:

```powershell
cd d:\proyectos\backendbn
git add .
git commit -m "Descripción de los cambios"
git push
```

Render detectará automáticamente los cambios y redesplegará la aplicación.

## Notas Importantes

- **Render Free Tier** se duerme después de 15 minutos de inactividad
- El primer acceso después de dormir tardará ~30 segundos en despertar
- Los modelos se cargan una vez al iniciar (no en cada request)
- Para mejor rendimiento en producción, considera el plan de pago de Render

## Recursos Adicionales

- Documentación Render: https://render.com/docs
- GitHub Desktop (alternativa visual): https://desktop.github.com
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf
