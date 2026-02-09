# Certificados

Aquí van los certificados para firmar los pases de Apple Wallet.

## Qué necesitas

### 1. Certificado Pass Type ID (archivo `.p12`)

Este es el certificado que firma tus pases. Sin él, no funcionan.

**Cómo conseguirlo:**

1. Entra en tu cuenta de [Apple Developer](https://developer.apple.com/account/resources/certificates/list) (necesitas el programa de pago, 99€/año)

2. Crea un Pass Type ID en [Identifiers](https://developer.apple.com/account/resources/identifiers/list)
   - Algo como `pass.org.gpul.hackudc.ticket`
   - Apúntalo, lo necesitas para el `.env`

3. Ve a [Certificates](https://developer.apple.com/account/resources/certificates/list) y crea un "Pass Type ID Certificate"
   - Asócialo con el identificador que creaste antes
   - Descarga el `.cer`

4. Abre el `.cer` (se abre con Keychain Access en Mac)
   - Busca el certificado en "Mis Certificados"
   - Exporta como `.p12`
   - Ponle una contraseña (guárdala bien)

### 2. Certificado WWDR (archivo `.cer`)

Es el certificado intermedio de Apple. Bájalo de [aquí](https://www.apple.com/certificateauthority/).

Usa el **G4** (funciona en casi todo) o el **G6** (más nuevo).

## Configuración

Pon tus certificados en esta carpeta y configura el `.env` en la raíz:

```bash
PASSKIT_TEAM_ID=ABCDEF1234
PASSKIT_PASS_TYPE_ID=pass.org.gpul.hackudc.ticket
PASSKIT_CERT_P12_PATH=~/passkit/hackackathon/assets/cert/Passkit.p12
PASSKIT_CERT_P12_PASSWORD=tu_contraseña
PASSKIT_WWDR_CERT_PATH=~/passkit/hackackathon/assets/cert/AppleWWDRCAG4.cer
```

Tu `TEAM_ID` lo encuentras en tu [cuenta de developer](https://developer.apple.com/account/).

## Seguridad

**IMPORTANTE**: No subas estos archivos a git. El `.gitignore` ya los ignora, pero ten cuidado.

Los certificados `.p12` tienen tu clave privada. Si alguien los consigue, puede firmar pases en tu nombre.

- Guárdalos en un sitio seguro
- No los compartas
- Los certificados expiran al año, tendrás que renovarlos

## Verificar que funcionan

Comprueba el P12:
```bash
openssl pkcs12 -info -in assets/cert/Passkit.p12 -noout
```

Debe decir "MAC verified OK" si la contraseña es correcta.

Comprueba el WWDR:
```bash
openssl x509 -in assets/cert/AppleWWDRCAG4.cer -inform DER -text -noout
```

## Problemas comunes

**Error con OpenSSL**: Revisa la contraseña del P12 en el `.env`

**No encuentra el certificado**: Comprueba las rutas en el `.env`

**Pass Type ID no coincide**: El del `.env` tiene que ser exactamente el mismo que creaste en Apple Developer

**Certificado expirado**: Genera uno nuevo en Apple Developer y actualiza el P12
