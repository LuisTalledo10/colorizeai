# Guía Rápida: Despliegue GitHub + Render

## 1. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `colorizeai` (o el que prefieras)
3. Descripción: "Sistema de colorización automática de imágenes con Deep Learning"
4. Mantén el repositorio **Público** (para Render Free Tier)
5. NO inicialices con README, .gitignore o licencia (ya los tenemos)
6. Haz clic en "Create repository"

## 2. ✅ COMPLETADO - Repositorio ya está en GitHub

Tu código ya está subido a: **https://github.com/LuisTalledo10/colorizeai**

Los 3 modelos están incluidos en el repositorio (GitHub permite archivos < 100 MB).

Para futuras actualizaciones:

```powershell
cd d:\proyectos\backendbn
git add .
git commit -m "Descripción de los cambios"
git push
```

## 3. ✅ Modelos Incluidos en el Repositorio

Los 3 modelos (Básica: 10.6 MB, Mejorada: 88.4 MB, RMSprop: 59 MB) ya están en GitHub.

**No necesitas configurar `MODEL_BASE_URL`** - los modelos se cargarán automáticamente desde el repositorio.

## 4. Desplegar en Render

1. Ve a https://render.com y crea una cuenta (gratis)

2. En el Dashboard, haz clic en "New +" → "Web Service"

3. Conecta tu repositorio de GitHub:
   - Autoriza a Render para acceder a tu GitHub
   - Selecciona el repositorio **`LuisTalledo10/colorizeai`**

4. Configuración del servicio:
   - **Name**: `colorizeai` (o el que prefieras)
   - **Region**: Oregon (US West) - más cercano
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

5. **NO** necesitas añadir variables de entorno (los modelos ya están en el repo)

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
