# pkpassBuilder

Generador de passkits (.pkpass) para Apple Wallet. Automatiza la creación de entradas digitales con códigos QR a partir de un simple JSON.

## ¿Para qué sirve?

A todo el mundo le gusta la comodidad de las entradas digitales, pero lo que es un dolor de cabeza es el proceso de creación de los mismos. Este proyecto automatiza el flujo:

1. Lee una lista de asistentes desde un JSON
2. Genera un código QR correspondiente a un campo del json (ej. email)
3. Crea un pase de Apple Wallet (.pkpass) con la información personalizada
4. Guarda todos los archovos correctamente firmados y listos para distribuir

Ideal para eventos, conferencias, hackatones...

## Lo que necesitas antes de empezar

### Cuenta de Apple Developer

Necesitas estar suscrito al [Apple Developer Program](https://developer.apple.com/programs/) (99€/año). Sin esto no hay certificados para firmar los pases, y ni Apple Wallet, ni la mayoría de aplicaciones de cartera compatibles con `.pkpass` aceptarán tus pases.

Pro tip: Si tu organización califica, hay [fee waivers](https://developer.apple.com/help/account/membership/fee-waivers/) (ONG, administraciones públicas, centros educativos, etc.).

### Certificados

Vas a necesitar dos archivos:

**1. Pass Type ID Certificate (`.p12`)**
- Tu certificado para firmar los pases
- Lo creas en [Apple Developer](https://developer.apple.com/account/resources/certificates/list)
- Tipo: "Pass Type ID Certificate"
- Lo exportas desde Keychain Access como `.p12` con contraseña

**2. WWDR Certificate (`.cer`)**
- Certificado intermedio de Apple
- Lo bajas de [aquí](https://www.apple.com/certificateauthority/)
- Usa el G4: `AppleWWDRCAG4.cer`

**3. Pass Type Identifier**
- Lo creas en [Identifiers](https://developer.apple.com/account/resources/identifiers/list/passTypeId)
- Algo como `pass.com.tuorg.evento`
- También necesitas tu Team ID (lo ves en tu cuenta)

Más detalles en [assets/cert/README.md](assets/cert/README.md).

## Instalación

```bash
git clone https://github.com/danicallero/pkpassBuilder
cd pkpassBuilder

# Entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt
```

## Configuración

### 1. Certificados

Pon tus certificados en `assets/cert/`

### 2. Variables de entorno

Crea un `.env` en la raíz:

```bash
# Apple Developer
PASSKIT_TEAM_ID=TU_TEAM_ID
PASSKIT_PASS_TYPE_ID=pass.com.tuorg.evento

# Certificados
PASSKIT_CERT_P12_PATH=assets/cert/Passkit.p12
PASSKIT_CERT_P12_PASSWORD=tu_contraseña
PASSKIT_WWDR_CERT_PATH=assets/cert/AppleWWDRCAG4.cer

# Fecha del evento (opcional, se puede cambiar en generate.py)
FECHA_INICIO_EVENTO=2026-02-27T17:30:00
```

### 3. Personalizar el evento

Edita `src/pkpass_builder/generate.py`:

```python
# Información del evento
PASSKIT_EVENT = {
    "ORG": "GPUL - HackUDC",
    "NAME": "HackUDC 2026",
    "DESC": "Pase de acceso a HackUDC 2026",
    "DATE": datetime(2026, 2, 27, 17, 30),
    "LOCATION": {
        "latitude": 43.3332,
        "longitude": -8.4115,
        "relevantText": "Presenta este pase en la entrada del evento.",
    },
}

# Colores y diseño
PASSKIT_STYLE = {
    "FG_COLOR": "rgb(255, 255, 255)",
    "BG_COLOR": "rgb(40, 40, 40)",
    "LABEL_COLOR": "rgb(255, 180, 0)",
    "ICON": BASE_DIR / "assets" / "img" / "icon.png",
    "LOGO": BASE_DIR / "assets" / "img" / "logo_w@2x.png",
    "STRIP": BASE_DIR / "assets" / "img" / "strip.png",
}

# Campos que aparecen en el pase
PASSKIT_FIELDS = {
    "header": [...],
    "secondary": [
        {"key": "name", "label": "Nombre", "value": "{nombre}"},
        {"key": "role", "label": "Rol", "value": "{rol}"},
    ],
    "auxiliary": [...],
    "back": [...]
}
```

Placeholders disponibles: `{nombre}`, `{correo}`, `{acreditacion}`, `{token}`, `{rol}`, `{dni}`, `{hora}`, `{fecha_corta}`

## Uso

### 1. Prepara tus datos

Crea un JSON tipo `personas.json`:

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
        "acreditacion": null,
        "rol": "Mentor"
    }
]
```

### 2. Genera los pases

```bash
python generar_pases.py personas.json
```

o usando el módulo:

```bash
python -m pkpass_builder personas.json

# Usar acreditación como identificador (serial/QR/fichero)
python -m pkpass_builder --use-acreditacion personas.json
```

### 3. Recoge los archivos

Se guardan en:
- `output/*.pkpass` - Los pases
- `output/qr/*.png` - QR codes individuales

## Imágenes

El script redimensiona automáticamente para que las imágenes no aparezcan pixeladas, pero estas son las medidas ideales:

| Asset | @2x | @1x | 
|-------|-----|-----|
| Icon  | 58x58 | 29x29 |
| Logo  | 320x100 | 160x50 |
| Strip | 1125x369 | 375x123 |

Pon tus imágenes en `assets/img/`. Soporta PNG y SVG (este último necesita `cairosvg`).

## Problemas comunes

**Error: "Certificado P12 no configurado"**
→ Revisa la ruta en `.env` y que el archivo exista

**Error: "No se pudieron extraer los certificados"**
→ Contraseña incorrecta o el P12 está corrupto. Expórtalo de nuevo.

**El pase no se abre en el iPhone**
→ Comprueba que el Pass Type ID y Team ID sean correctos, y que los certificados no hayan expirado

**Error con SVG**
→ Instala `pip install cairosvg` o usa PNG directamente

## Estructura

```
pkpassBuilder/
├── generar_pases.py         
├── src/
│   └── pkpass_builder/      # Módulo principal
│       ├── generate.py      # Generador de pases
│       └── __main__.py
├── examples/
│   └── ejemplo_personas.json
├── assets/
│   ├── cert/                # Certificados (NO SUBIR A GIT)
│   └── img/                 # Imágenes (logo, icono, strip)
├── output/                  # Pases generados
│   └── qr/
└── tests/
```

## Seguridad

No subas a git:
- `.p12` / `.cer` (certificados)
- `.env` (contraseñas)
- `output/` (datos de participantes)

El `.gitignore` ya está configurado, pero ojo.

## Contribuir

Si quieres mejorar algo:

1. Fork el repo
2. Crea una rama (`git checkout -b feature/cosa-nueva`)
3. Commitea (`git commit -m 'Añade cosa nueva'`)
4. Push (`git push origin feature/cosa-nueva`)
5. Abre un Pull Request

## Licencia

Ver [LICENSE](LICENSE).

## Créditos

Usa [wallet-py3k](https://github.com/devartis/passbook) para generar los passes.

Docs oficiales: [Apple Wallet Developer Guide](https://developer.apple.com/wallet/)

---

Hecho con ❤️ por [@danicallero](https://github.com/danicallero)

*Este proyecto no está afiliado con Apple Inc.*
