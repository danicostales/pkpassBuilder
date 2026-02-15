# 🚀 Inicio Rápido

Esta guía te ayudará a generar tu primer Apple Wallet Pass en menos de 10 minutos.

## ⚡ Requisitos Mínimos

- Python 3.8 o superior
- Cuenta de Apple Developer (99€/año)
- macOS, Linux o Windows con OpenSSL

## Pasos

### 1️⃣ Instalar Dependencias (2 min)

```bash
# Clonar el repositorio
git clone <tu-repo>
cd pkpassBuilder

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Obtener Certificados (5 min)

#### Pass Type ID Certificate (.p12)
1. Ve a https://developer.apple.com/account/resources/certificates/list
2. Click en "+" → Selecciona "Pass Type ID Certificate"
3. Sigue el asistente y descarga el certificado
4. Abre el `.cer` en Keychain Access (Mac) o importa en tu sistema
5. Exporta como `.p12` con una contraseña

#### WWDR Certificate (.cer)
1. Descarga de https://www.apple.com/certificateauthority/
2. Busca "Worldwide Developer Relations - G4"
3. Guarda el archivo `.cer`

#### Pass Type ID
1. Ve a https://developer.apple.com/account/resources/identifiers/list/passTypeId
2. Click en "+" → Registra un nuevo Pass Type ID
3. Formato: `pass.com.tuorganizacion.nombre`
4. Anota tu Team ID (aparece en la esquina superior derecha)

### 3️⃣ Configurar el Proyecto (2 min)

```bash
# Crear directorio para certificados
mkdir -p staticfiles/cert

# Copiar certificados
cp /ruta/a/tu/Passkit.p12 staticfiles/cert/
cp /ruta/a/AppleWWDRCAG4.cer staticfiles/cert/

# Configurar variables de entorno
cp .env.example .env
nano .env  # o usa tu editor favorito
```

Edita `.env` con tus valores:
```bash
PASSKIT_TEAM_ID=ABC1234XYZ
PASSKIT_PASS_TYPE_ID=pass.com.tuorganizacion.evento
PASSKIT_CERT_P12_PATH=staticfiles/cert/Passkit.p12
PASSKIT_CERT_P12_PASSWORD=tu_password
PASSKIT_WWDR_CERT_PATH=staticfiles/cert/AppleWWDRCAG4.cer
```

### 4️⃣ Generar tu Primer Pase (1 min)

```bash
# Usar el archivo de ejemplo (modo entradas — usa el email como identificador)
python generar_passkits.py ejemplo_personas.json  # o: python -m pkpass_builder ejemplo_personas.json

# Usar el modo acreditación (genera solo badges para personas con `acreditacion`)
python -m pkpass_builder --use-acreditacion ejemplo_personas.json

# Generar entradas (modo por defecto) — genera `entradas` para todas las personas
python -m pkpass_builder ejemplo_personas.json

# Generar ambos (entradas + badges)
python -m pkpass_builder --both ejemplo_personas.json

# Verificar que se generó
ls -la output/
ls -la output/pass/entradas
ls -la output/pass/badges
```

¡Listo! Los archivos `.pkpass` están en `output/pass/entradas` o `output/pass/badges` según el modo. QR files en `output/qr/entradas` y `output/qr/badges`.

### 5️⃣ Probar en iPhone

Hay varias formas:

**Opción A: Email**
```bash
# Envía el .pkpass por email
echo "Tu pase adjunto" | mail -s "Tu Pase" -a output/usuario1_example_com.pkpass tu@email.com
```

**Opción B: AirDrop**
- Abre la carpeta `output/` en Finder
- Click derecho en un `.pkpass`
- Compartir → AirDrop → Tu iPhone

**Opción C: Servidor local**
```bash
# Servir los archivos localmente
python3 -m http.server 8000 --directory output

# Abre en tu iPhone: http://tu-ip:8000/usuario1_example_com.pkpass
```

## Personalizar el diseño

Edita `generar_passkits.py`:

```python
# Cambia los colores
PASSKIT_STYLE = {
    "FG_COLOR": "rgb(255, 255, 255)",  # Texto blanco
    "BG_COLOR": "rgb(0, 122, 255)",    # Fondo azul Apple
    "LABEL_COLOR": "rgb(200, 200, 200)",  # Etiquetas gris claro
}

# Cambia la información del evento
PASSKIT_EVENT = {
    "ORG": "Tu Organización",
    "NAME": "Tu Evento 2026",
    "DESC": "Pase de acceso",
    "DATE": datetime(2026, 3, 15, 10, 0),  # 15 marzo 2026, 10:00
}
```

## 🎯 Crear tu Lista de Participantes

Crea un archivo `mis_participantes.json`:

```json
[
    {
        "correo": "ana@ejemplo.com",
        "nombre": "Ana García",
        "acreditacion": "VIP001",
        "token": "ana_vip001",
        "rol": "Speaker"
    },
    {
        "correo": "pedro@ejemplo.com",
        "nombre": "Pedro López",
        "acreditacion": "ATT002",
        "rol": "Asistente"
    }
]
```

Genera los pases:
```bash
python generar_passkits.py mis_participantes.json

# Generar usando el campo `acreditacion` como identificador (serial/QR/fichero)
python -m pkpass_builder --use-acreditacion mis_participantes.json
```

## ❓ Problemas Comunes

### "Certificado P12 no configurado"
- Verifica que la ruta en `.env` sea correcta
- Usa rutas absolutas si tienes problemas con rutas relativas

### "Error al extraer certificados"
- Verifica la contraseña del P12
- Intenta exportar el P12 de nuevo desde Keychain

### "El pase no se abre en iPhone"
- Asegúrate de que el Team ID y Pass Type ID sean correctos
- Verifica que el certificado no haya expirado
- Comprueba que el WWDR sea el G4 (no G3)

### "ModuleNotFoundError: wallet"
```bash
pip install wallet-py3k
```

## Siguiente paso

- Lee el [README.md](README.md) completo para más opciones
- Consulta [CONTRIBUTING.md](CONTRIBUTING.md) si quieres contribuir
- Revisa la [documentación de Apple Wallet](https://developer.apple.com/wallet/)

## 💡 Consejos

- Añade tus propios logos e iconos en `staticfiles/img/`
- 📍 Configura geolocalización para notificaciones automáticas
- ⏰ Los pases aparecen automáticamente en la fecha del evento
- 🔄 Puedes actualizar pases remotamente (requiere servidor web)

---

¿Necesitas ayuda? [Abre un issue](../../issues) →
