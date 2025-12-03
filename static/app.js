const fileInput = document.getElementById('fileInput')
const goBtn = document.getElementById('goBtn')
const orig = document.getElementById('orig')
const result = document.getElementById('result')

fileInput.addEventListener('change', e => {
  const f = e.target.files[0]
  if (!f) return
  orig.src = URL.createObjectURL(f)
  result.src = ''
  
  // Update file label
  const label = document.querySelector('.file-label')
  if (label) {
    label.textContent = f.name
  }
})

goBtn.addEventListener('click', async () => {
  const f = fileInput.files[0]
  if (!f) {
    alert('Por favor selecciona una imagen primero')
    return
  }
  
  const modelRadio = document.querySelector('input[name=model]:checked')
  if (!modelRadio) {
    alert('Por favor selecciona un modelo de colorización')
    return
  }
  
  const model = modelRadio.value
  goBtn.disabled = true
  goBtn.textContent = 'Procesando imagen...'

  const fd = new FormData()
  fd.append('image', f)
  fd.append('model', model)

  try {
    const res = await fetch('/colorize', { method: 'POST', body: fd })
    const data = await res.json()
    
    if (res.ok) {
      result.src = data.image
    } else {
      alert('Error: ' + (data.error || 'No se pudo procesar la imagen'))
    }
  } catch (err) {
    alert('Error de conexión: ' + err.message)
  } finally {
    goBtn.disabled = false
    goBtn.textContent = 'Procesar Imagen'
  }
})

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute('href'))
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
})
