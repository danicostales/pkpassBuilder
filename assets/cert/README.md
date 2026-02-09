# 📁 Directorio de Certificados

Este directorio debe contener los certificados necesarios para firmar los pases de Apple Wallet.

## 🔒 Archivos Requeridos

### 1. Passkit.p12
- **Qué es**: Certificado Pass Type ID en formato PKCS#12
- **Cómo obtenerlo**: 
  1. Ve a [Apple Developer Certificates](https://developer.apple.com/account/resources/certificates/list)
  2. Crea un certificado "Pass Type ID Certificate"
  3. Descárgalo y ábrelo en Keychain Access
  4. Exporta como `.p12` con una contraseña segura

### 2. AppleWWDRCAG4.cer
- **Qué es**: Certificado intermedio de Apple (Worldwide Developer Relations)
- **Cómo obtenerlo**: Descárgalo de [Apple Certificate Authority](https://www.apple.com/certificateauthority/)
- **Importante**: Usa el certificado G4 para compatibilidad

## ⚠️ IMPORTANTE

- **NUNCA** subas estos archivos a git
- El `.gitignore` ya está configurado para ignorar:
  - `*.p12`
  - `*.cer`
  - `*.pem`
  - `*.key`
  - Todo el directorio `cert/`
- Guarda una copia de seguridad en un lugar seguro
- No compartas tu P12 ni su contraseña

## 📝 Configuración

Después de colocar tus certificados aquí, configúralos en el archivo `.env`:

```bash
PASSKIT_CERT_P12_PATH=staticfiles/cert/Passkit.p12
PASSKIT_CERT_P12_PASSWORD=tu_password_secreto
PASSKIT_WWDR_CERT_PATH=staticfiles/cert/AppleWWDRCAG4.cer
```

## 🔍 Verificación

Para verificar que tus certificados son correctos:

```bash
# Verificar el P12 (te pedirá la contraseña)
openssl pkcs12 -info -in Passkit.p12 -noout

# Verificar el certificado WWDR
openssl x509 -in AppleWWDRCAG4.cer -inform DER -text -noout
```
