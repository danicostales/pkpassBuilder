# pkpassBuilder — Generador de Apple Wallet Passes

Generador de passkits (.pkpass) para eventos, compatible con Apple Wallet. Permite crear pases personalizados con códigos QR, información del evento y diseño configurable.

## Características principales

- Diseño personalizable (colores, iconos, logos y banners)
- Compatible con Apple Wallet (.pkpass)
- Firma con certificados de Apple Developer
- Soporte de geolocalización y fechas de evento
- Generación de códigos QR por participante
- Conversión opcional de SVG a PNG (requiere cairosvg)

## Requisitos previos

### 1. Cuenta de Apple Developer
Necesitas una cuenta de Apple Developer (99€/año o gratis en determinados casos [ver fee waivers](https://developer.apple.com/help/account/membership/fee-waivers/)) para obtener los certificados necesarios.

### 2. Certificados requeridos

#### a) Pass Type ID Certificate (`.p12`)
1. Ve a [Apple Developer Certificates](https://developer.apple.com/account/resources/certificates/list)
2. Crea un nuevo certificado de tipo "Pass Type ID Certificate"
3. Descarga el certificado y ábrelo en Keychain Access
4. Exporta como `.p12` con contraseña

#### b) WWDR Certificate (`.cer`)
- Descarga el [Apple Worldwide Developer Relations (WWDR) Certificate](https://www.apple.com/certificateauthority/)
- Usa el certificado G4: `AppleWWDRCAG4.cer`

### 3. Pass Type Identifier
1. Ve a [Identifiers](https://developer.apple.com/account/resources/identifiers/list/passTypeId)
2. Crea un nuevo Pass Type ID (ej: `pass.com.tuorganizacion.evento`)
3. Anota el Team ID (aparece en tu cuenta de desarrollador)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd pkpassBuilder
```

### 2. Crear entorno virtual (recomendado)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar certificados
```bash
# Copiar tus certificados
cp /ruta/a/tu/Passkit.p12 assets/cert/
cp /ruta/a/AppleWWDRCAG4.cer assets/cert/
```

### 5. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
nano .env
```

Configuración del `.env`:
```bash
# Apple Developer Account
PASSKIT_TEAM_ID=TU_TEAM_ID
PASSKIT_PASS_TYPE_ID=pass.com.tuorganizacion.evento

# Certificados (rutas relativas al proyecto)
PASSKIT_CERT_P12_PATH=assets/cert/Passkit.p12
PASSKIT_CERT_P12_PASSWORD=tu_password_del_p12
PASSKIT_WWDR_CERT_PATH=assets/cert/AppleWWDRCAG4.cer
```

## Uso

### 1. Preparar datos de participantes
Crea un archivo JSON con la información de los participantes:

```json
[
    {
        "correo": "usuario@example.com",
        "nombre": "Juan Pérez",
        "acreditacion": "ABC123",
        "rol": "Hacker"
    },
    {
        "correo": "maria@example.com",
        "nombre": "María García",
        "acreditacion": "XYZ789",
        "rol": "Mentor"
    }
]
```

### 2. Ejecutar el generador
```bash
# Opción 1 (compatibilidad):
python generar_passkits.py personas.json

# Opción 2 (módulo):
python -m pkpass_builder personas.json
```

### 3. Resultado
Los archivos generados estarán en:
- `output/*.pkpass` - Archivos de pases para Apple Wallet
- `output/qr/*.png` - Códigos QR individuales

## ⚙️ Configuración del Evento

Edita el archivo `generar_passkits.py` para personalizar tu evento:

### Información del Evento
```python
PASSKIT_EVENT = {
    "ORG": "Tu Organización",
    "NAME": "Nombre del Evento",
    "DESC": "Descripción del pase",
    "DATE": datetime(2026, 2, 27, 17, 30),  # Fecha del evento
    "LOCATION": {
        "latitude": 43.3332,
        "longitude": -8.4115,
        "relevantText": "Presenta este pase en la entrada."
    }
}
```

### Diseño Visual
```python
PASSKIT_STYLE = {
    "FG_COLOR": "rgb(255, 255, 255)",      # Color del texto
    "BG_COLOR": "rgb(40, 40, 40)",         # Color de fondo
    "LABEL_COLOR": "rgb(255, 255, 255)",   # Color de las etiquetas
    "ICON": "ruta/al/icono.png",           # Icono (PNG o URL a SVG)
    "LOGO": "ruta/al/logo.png",            # Logo
    "STRIP": "ruta/al/banner.png",         # Banner (opcional)
}
```

### Campos del Pase
```python
PASSKIT_FIELDS = {
    "header": [{"key": "hour", "label": "Hora", "value": "{hora}"}],
    "primary": [],  # Campo principal grande
    "secondary": [
        {"key": "name", "label": "Nombre", "value": "{nombre}"},
        {"key": "role", "label": "Rol", "value": "{rol}"},
    ],
    "auxiliary": [
        {"key": "email", "label": "Correo", "value": "{correo}"}
    ],
    "back": [  # Información en la parte trasera
        {"key": "web", "label": "Web", "value": "https://tuevento.com"}
    ]
}
```

#### Placeholders disponibles:
- `{nombre}` - Nombre del participante
- `{correo}` - Correo electrónico
- `{rol}` - Rol (Hacker, Mentor, etc.)
- `{dni}` - DNI (si está disponible)
- `{fecha}` - Fecha del evento (DD-MM-YYYY)
- `{hora}` - Hora del evento (HH:MM)
- `{fecha_completa}` - Fecha completa formateada

## Dimensiones de imágenes

Para mejores resultados, usa estas dimensiones:

| Asset | Dimensión @2x | Dimensión @1x | Formato |
|-------|---------------|---------------|---------|
| Icon  | 58x58 px      | 29x29 px      | PNG     |
| Logo  | 320x100 px    | 160x50 px     | PNG     |
| Strip | 1125x369 px   | 375x123 px    | PNG     |

**Nota**: El script redimensiona automáticamente las imágenes, pero usar las dimensiones correctas mejora la calidad.

## Solución de problemas

### Error: "Certificado P12 no configurado"
- Verifica que la ruta en `.env` sea correcta
- Asegúrate de que el archivo `.p12` exista en la ruta especificada

### Error: "No se pudieron extraer los certificados del P12"
- Verifica que la contraseña del P12 sea correcta
- Intenta exportar el certificado de nuevo desde Keychain Access

### Error al cargar SVG
- Asegúrate de tener instalado `cairosvg`: `pip install cairosvg`
- O usa imágenes PNG en lugar de SVG

### Los pases no se abren en iPhone
- Verifica que el `Pass Type ID` y `Team ID` sean correctos
- Asegúrate de que los certificados no hayan expirado
- Verifica que el certificado WWDR sea el correcto (G4)

## Estructura del proyecto

```
pkpassBuilder/
├── pyproject.toml           # Configuración del proyecto
├── src/
│   └── pkpass_builder/      # Código fuente del paquete
│       ├── __init__.py
│       └── generate.py
├── examples/                # Ejemplos de entrada
│   └── ejemplo_personas.json
├── staticfiles/             # Assets, imágenes y certificados
│   ├── cert/                # Certificados (no incluir en git)
│   └── img/                 # Imágenes (logo, icono, banner)
├── tests/                   # Tests automatizados
│   └── test_import.py
├── output/                  # Passkits generados (no incluir en git)
└── README.md
```
    └── qr/*.png
```

## Seguridad

**IMPORTANTE**: Nunca subas a git:
- Archivos `.p12` (certificados)
- Archivos `.cer` (certificados WWDR)
- Archivo `.env` (contraseñas y credenciales)
- Carpeta `output/` (datos de participantes)

El `.gitignore` ya está configurado para proteger estos archivos.

## Licencia

Este proyecto está bajo la licencia especificada en el archivo [LICENSE](LICENSE).

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🙏 Créditos

- Desarrollado por GPUL (ejemplo)
- Usa [wallet-py3k](https://github.com/devartis/passbook) para la generación de passes
- Documentación de Apple: [Wallet Developer Guide](https://developer.apple.com/wallet/)

## Soporte

Si tienes problemas o preguntas:
- Abre un [Issue](../../issues) en GitHub
- Consulta la [documentación oficial de Apple Wallet](https://developer.apple.com/documentation/walletpasses)
- Para asuntos de seguridad, revisa `SECURITY.md`.

---

## Mantenimiento y contacto

Mantenido por: Dani Callero <hola@danicallero.es>. Para preguntas generales o PRs, usa Issues; para reportes de seguridad, usa el canal indicado en `SECURITY.md`.

**Nota**: Este proyecto es independiente y no está afiliado con Apple Inc.
