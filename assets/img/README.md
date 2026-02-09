# Directorio de imágenes

Este directorio contiene los assets visuales para los pases de Apple Wallet.

## 📐 Archivos Recomendados

### icon.png / icon@2x.png
- **Dimensiones**: 29x29 px (1x), 58x58 px (2x)
- **Formato**: PNG con transparencia (RGBA)
- **Uso**: Icono pequeño que aparece en la lista de pases
- **Nota**: El script aplica automáticamente la forma "squircle" de Apple

### logo.png / logo@2x.png
- **Dimensiones**: 160x50 px (1x), 320x100 px (2x)
- **Formato**: PNG con transparencia (RGBA)
- **Uso**: Logo que aparece en la parte superior del pase
- **Tip**: Usa fondo transparente para mejor integración

### strip.png / strip@2x.png (opcional)
- **Dimensiones**: 375x123 px (1x), 1125x369 px (2x)
- **Formato**: PNG con o sin transparencia
- **Uso**: Banner superior en pases de tipo "event ticket"
- **Nota**: No uses strip si quieres que primary fields sea más prominente

## Consejos de diseño

1. **Iconos**: 
   - Usa colores sólidos y formas simples
   - Evita texto muy pequeño
   - El script soporta SVG y los convierte automáticamente

2. **Logos**:
   - Debe ser legible en tamaño pequeño
   - Usa alto contraste con el fondo del pase
   - Centra el logo horizontalmente

3. **Strip**:
   - Usa imágenes de alta calidad
   - El script recorta y centra automáticamente
   - Evita texto importante en los bordes

## Configuración

En `generar_passkits.py`, configura las rutas:

```python
PASSKIT_STYLE = {
    "ICON": "https://ejemplo.com/icon.svg",  # URL o ruta local
    "LOGO": BASE_DIR / "staticfiles/img/logo_w@2x.png",
    "STRIP": BASE_DIR / "staticfiles/img/strip.png",  # Opcional
}
```

## Procesamiento automático

El script incluye procesamiento automático de imágenes:
- Redimensionamiento inteligente con upscaling
- Aplicación de máscara squircle para iconos
- Conversión de SVG a PNG
- Generación de versiones @2x y 1x
- Optimización de calidad

## Fallbacks

Si no se encuentran imágenes, el script:
1. Busca `icon.png`, `logo.png` en este directorio
2. Genera placeholders si es necesario
3. Usa el icono como logo si no hay logo disponible
