#!/usr/bin/env python
"""Core CLI for pkpassBuilder (migrated from generar_passkits.py).

This module contains the main logic to generate `.pkpass` files and QR images.
"""

import sys
import json
import os
import subprocess
import tempfile
import io
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv()
    logging.getLogger(__name__).info("Variables de entorno cargadas desde .env")
except Exception:
    logging.getLogger(__name__).info(
        "python-dotenv no disponible; usando variables de entorno del sistema"
    )

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Directorio base del proyecto (dos niveles arriba de este archivo => repo root)
BASE_DIR = Path(__file__).resolve().parents[2].resolve()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# --- Certificates (Environment) ---
_p12_path = os.getenv("PASSKIT_CERT_P12_PATH", "")
_wwdr_path = os.getenv("PASSKIT_WWDR_CERT_PATH", "")

PASSKIT_AUTH = {
    "TEAM_ID": os.getenv("PASSKIT_TEAM_ID"),
    "PASS_TYPE_ID": os.getenv("PASSKIT_PASS_TYPE_ID"),
    "P12_PATH": str(Path(_p12_path).expanduser().resolve()) if _p12_path else "",
    "P12_PASSWORD": os.getenv("PASSKIT_CERT_P12_PASSWORD", ""),
    "WWDR_CERT": str(Path(_wwdr_path).expanduser().resolve()) if _wwdr_path else "",
}

# --- Event Info ---
PASSKIT_EVENT = {
    "ORG": "GPUL - HackUDC",
    "NAME": "HackUDC 2026",
    "DESC": "Pase de acceso a HackUDC 2026",
    "DATE": datetime(2026, 2, 27, 17, 00),
    "LOCATION": {
        "latitude": 43.3332,
        "longitude": -8.4115,
        "relevantText": "Presenta este pase en la entrada del evento.",
    },
}

# Sobrescribir con fecha de .env si existe
_fecha_evento = os.getenv("FECHA_INICIO_EVENTO")
if _fecha_evento:
    try:
        PASSKIT_EVENT["DATE"] = datetime.fromisoformat(_fecha_evento)
        logger.info(f"Fecha cargada desde .env: {PASSKIT_EVENT['DATE']}")
    except Exception as e:
        logger.warning(f"Error cargando fecha desde .env: {e}")

# --- Visuals ---
PASSKIT_STYLE = {
    "FG_COLOR": "rgb(255, 255, 255)",
    "BG_COLOR": "rgb(40, 40, 40)",
    "LABEL_COLOR": "rgb(255, 180, 0)",  # Ámbar
    "ICON": BASE_DIR / "assets" / "img" / "icon.png",
    "LOGO": BASE_DIR / "assets" / "img" / "logo_w@2x.png",
    "STRIP": BASE_DIR / "assets" / "img" / "strip.png",
}

# --- Pass Fields Structure ---
PASSKIT_FIELDS = {
    "header": [
        {"key": "spacer", "label": "", "value": ""},
        {
            "key": "when",
            "label": "{hora}",
            "value": "{fecha_corta}",
            "textAlignment": "PKTextAlignmentRight",
        },
    ],
    "primary": [],
    "secondary": [
        {"key": "name", "label": "Nombre", "value": "{nombre}"},
        {"key": "role", "label": "Rol", "value": "{rol}"},
    ],
    "auxiliary": [{"key": "email", "label": "Correo", "value": "{correo}"}],
    "back": [
        {"key": "event_info", "label": "Evento", "value": PASSKIT_EVENT["NAME"]},
        {
            "key": "loc",
            "label": "Ubicación",
            "value": "Facultade de Informática, UDC, A Coruña",
        },
        {
            "key": "entry_info",
            "label": "Información de Entrada",
            "value": "Presenta este pase cuando hagas el check-in.",
        },
        {
            "key": "web",
            "label": "Horario, retos y más",
            "value": "https://live.hackudc.gpul.org",
        },
        {
            "key": "web",
            "label": "Términos y Condiciones",
            "value": "https://hackudc.gpul.org/terms",
        },
        {
            "key": "web",
            "label": "Política de Privacidad",
            "value": "https://hackudc.gpul.org/privacy",
        },
        {
            "key": "web",
            "label": "Código de Conducta",
            "value": "https://hackudc.gpul.org/conduct",
        },
        {"key": "org", "label": "Organizado por", "value": "GPUL"},
    ],
}

# --- Assets & Output ---
PASSKIT_ASSETS_DIR = str(BASE_DIR / "assets" / "img")
OUTPUT_DIR = BASE_DIR / "output"

# ============================================================================
# DATACLASSES
# ============================================================================


@dataclass
class Persona:
    """Clase simple para representar una persona."""

    correo: str
    nombre: str
    acreditacion: str = None
    token: str = None
    rol: str = "Hacker"
    dni: str = ""
    mentor: bool = False
    patrocinador: bool = False


@dataclass
class PassResult:
    """Resultado de la generación de un pase."""

    pkpass: bytes
    qr_png: bytes
    acreditacion: str = ""


def build_substitution_context(persona: Persona) -> dict:
    """Construye el diccionario de sustituciones para los campos del pase."""
    role = persona.rol if persona.rol else "Hacker"

    # Formatear fecha del evento
    date_values = {"hora": "", "fecha_corta": ""}
    if PASSKIT_EVENT.get("DATE"):
        date = PASSKIT_EVENT["DATE"]
        meses_abrev = [
            "",
            "ene",
            "feb",
            "mar",
            "abr",
            "may",
            "jun",
            "jul",
            "ago",
            "sept",
            "oct",
            "nov",
            "dic",
        ]
        date_values = {
            "hora": date.strftime("%H:%M"),
            "fecha_corta": f"{date.day:02d} {meses_abrev[date.month]}, {date.year}",
        }

    return {
        "{nombre}": persona.nombre,
        "{correo}": persona.correo,
        "{acreditacion}": persona.acreditacion or "",
        "{token}": persona.token or "",
        "{dni}": persona.dni or "",
        "{rol}": role,
        "{hora}": date_values["hora"],
        "{fecha_corta}": date_values["fecha_corta"],
    }


def process_fields(fields_list: list, context: dict, area: str = "") -> list:
    """Procesa los campos del pase reemplazando los placeholders."""
    processed = []
    for field in fields_list:
        item = dict(field)
        for key in ["value", "label"]:
            value = str(item.get(key, ""))
            for placeholder, real_value in context.items():
                value = value.replace(placeholder, str(real_value))
            item[key] = value
        if area == "back" and item.get("value", "").startswith("http"):
            item["is_link"] = True
        processed.append(item)
    return processed


def cargar_personas(json_file: str) -> list[Persona]:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    personas = []
    for item in data:
        personas.append(
            Persona(
                correo=item.get("correo"),
                nombre=item.get("nombre"),
                acreditacion=item.get("acreditacion"),
                token=item.get("token"),
                rol=item.get("rol", "Hacker"),
                dni=item.get("dni", ""),
                mentor=item.get("mentor", False),
                patrocinador=item.get("patrocinador", False),
            )
        )
    return personas


def should_process_persona(persona: Persona, use_acreditacion: bool) -> bool:
    """Decide si debemos procesar una persona en el modo exclusivo.

    - Si use_acreditacion == True -> generar SOLO badges (personas con `acreditacion`).
    - Si use_acreditacion == False -> modo 'entradas' -> procesar TODAS las personas
      (las entradas se generan para todos; las acreditaciones se ignoran).
    """
    if use_acreditacion:
        return bool(persona.acreditacion)
    return True


def extract_p12_certificates(
    p12_path: str | Path, password: str, tmp_dir: Path
) -> tuple[str, str]:
    """Extrae certificado y clave privada de un P12 a archivos PEM usando openssl.

    Args:
        p12_path: Ruta al archivo P12
        password: Contraseña del P12
        tmp_dir: Directorio temporal para guardar los PEM

    Returns:
        Tupla (ruta_certificado_pem, ruta_clave_privada_pem)
    """
    p12_path = Path(p12_path)
    if not p12_path.exists():
        raise FileNotFoundError(f"Archivo P12 no encontrado: {p12_path}")

    cert_pem = tmp_dir / "cert.pem"
    key_pem = tmp_dir / "key.pem"
    pass_arg = f"pass:{password or ''}"

    cmd_base = ["openssl", "pkcs12", "-in", str(p12_path), "-passin", pass_arg]

    try:
        subprocess.run(
            cmd_base + ["-clcerts", "-nokeys", "-out", str(cert_pem)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            cmd_base + ["-nocerts", "-nodes", "-out", str(key_pem)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        # Reintento con -legacy para versiones antiguas de OpenSSL
        try:
            subprocess.run(
                cmd_base + ["-legacy", "-clcerts", "-nokeys", "-out", str(cert_pem)],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                cmd_base + ["-legacy", "-nocerts", "-nodes", "-out", str(key_pem)],
                check=True,
                capture_output=True,
            )
            logger.warning("Certificado extraído usando el flag -legacy de OpenSSL")
        except subprocess.CalledProcessError as e_legacy:
            logger.error(f"Error OpenSSL: {e_legacy.stderr.decode()}")
            raise RuntimeError(
                "No se pudieron extraer los certificados del P12. Revisa la contraseña."
            ) from e_legacy

    return str(cert_pem), str(key_pem)


def ensure_wwdr_pem(wwdr_path: str | Path, tmp_dir: Path) -> str:
    """Asegura que el certificado WWDR esté en formato PEM.

    Args:
        wwdr_path: Ruta al certificado WWDR (PEM o DER)
        tmp_dir: Directorio temporal

    Returns:
        Ruta al certificado WWDR en formato PEM
    """
    wwdr_path = Path(wwdr_path)
    if not wwdr_path.exists():
        raise FileNotFoundError(f"Certificado WWDR no encontrado: {wwdr_path}")

    # Si ya es PEM, retornar directamente
    with open(wwdr_path, "rb") as f:
        if b"BEGIN CERTIFICATE" in f.read(100):
            return str(wwdr_path)

    # Convertir de DER a PEM
    pem_path = tmp_dir / "wwdr.pem"
    try:
        subprocess.run(
            [
                "openssl",
                "x509",
                "-inform",
                "DER",
                "-in",
                str(wwdr_path),
                "-out",
                str(pem_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return str(pem_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error OpenSSL al convertir WWDR: {e.stderr}")
        raise RuntimeError("No se pudo convertir el certificado WWDR a PEM") from e


# Helpers de imágenes

def _resize_with_upscaling(img, target_size: int, sharpen: bool = True):
    from PIL import Image, ImageFilter, ImageOps

    max_src = max(img.size)
    upscale_factor = 4 if max_src < target_size * 2 else 2
    intermediate_size = (target_size * upscale_factor, target_size * upscale_factor)

    img_high = ImageOps.fit(
        img, intermediate_size, Image.Resampling.LANCZOS, centering=(0.5, 0.5)
    )
    img_out = img_high.resize((target_size, target_size), Image.Resampling.LANCZOS)

    if sharpen:
        img_out = img_out.filter(
            ImageFilter.UnsharpMask(radius=0.5, percent=80, threshold=1)
        )

    return img_out


def _make_squircle_mask(size: int, n: float = 3.8):
    from PIL import Image

    mask = Image.new("L", (size, size), 0)
    pixels = mask.load()

    for y in range(size):
        v = (2.0 * y) / (size - 1) - 1.0
        for x in range(size):
            u = (2.0 * x) / (size - 1) - 1.0
            if (abs(u) ** n + abs(v) ** n) <= 1.0:
                pixels[x, y] = 255

    return mask


def _apply_squircle(img, size: int, n: float = 3.8):
    from PIL import Image

    mask = _make_squircle_mask(size, n)
    resized = img.resize((size, size), Image.Resampling.LANCZOS)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(resized, (0, 0), mask)
    return out


def _load_image_from_source(source: str | Path, fallback_dir: Path = None):
    from PIL import Image

    if isinstance(source, str) and source.startswith("http"):
        try:
            import urllib.request

            resp = urllib.request.urlopen(source, timeout=10)
            data = resp.read()

            if b"<svg" in data or source.lower().endswith(".svg"):
                try:
                    import cairosvg

                    png_bytes = cairosvg.svg2png(bytestring=data)
                    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
                except Exception:
                    logger.exception(f"Error convirtiendo SVG a PNG desde {source}")
                    return None
            else:
                return Image.open(io.BytesIO(data)).convert("RGBA")
        except Exception as e:
            logger.exception(f"Error descargando imagen de {source}: {e}")
            return None

    source_path = Path(source) if source else None
    if source_path and source_path.exists():
        try:
            return Image.open(source_path).convert("RGBA")
        except Exception as e:
            logger.exception(f"Error abriendo imagen local {source_path}: {e}")
            return None

    return None


def _find_fallback(filename: str, search_dir: Path) -> str | None:
    candidates = [
        search_dir / filename,
        search_dir / "gpul.png",
        search_dir / "pkpassbuilder.png",
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def _save_icon(icon_img, tmp_dir: Path):
    from PIL import Image

    assets_dir = Path(PASSKIT_ASSETS_DIR)

    if icon_img is None:
        icon_img = _load_image_from_source(_find_fallback("icon.png", assets_dir))

    if icon_img is None:
        placeholder = Image.new("RGBA", (58, 58), (40, 40, 40, 255))
        placeholder = _apply_squircle(placeholder, 58, n=3.8)
        placeholder.save(tmp_dir / "icon@2x.png")
        placeholder.resize((29, 29), Image.Resampling.LANCZOS).save(
            tmp_dir / "icon.png"
        )
        logger.warning("Se generó icono placeholder")
        return

    icon_2x = _resize_with_upscaling(icon_img, 58, sharpen=False)
    icon_2x = _apply_squircle(icon_2x, 58, n=3.8)
    icon_2x.save(tmp_dir / "icon@2x.png")

    icon_1x = _resize_with_upscaling(icon_img, 29, sharpen=True)
    icon_1x = _apply_squircle(icon_1x, 29, n=3.8)
    icon_1x.save(tmp_dir / "icon.png")


def _save_logo(logo_img, tmp_dir: Path):
    from PIL import Image

    assets_dir = Path(PASSKIT_ASSETS_DIR)

    if logo_img is None:
        logo_img = _load_image_from_source(_find_fallback("logo.png", assets_dir))

    if logo_img is None:
        logger.warning("No se encontró logo, usando icono como fallback")
        return

    canvas_2x = Image.new("RGBA", (320, 100), (0, 0, 0, 0))
    logo_scaled = logo_img.copy()
    logo_scaled.thumbnail((300, 85), Image.Resampling.LANCZOS)

    y_offset = (100 - logo_scaled.height) // 2
    canvas_2x.paste(logo_scaled, (0, y_offset), logo_scaled)
    canvas_2x.save(tmp_dir / "logo@2x.png")
    canvas_2x.resize((160, 50), Image.Resampling.LANCZOS).save(tmp_dir / "logo.png")


def _save_strip(strip_path: str | Path, tmp_dir: Path):
    from PIL import Image

    strip_path = Path(strip_path)
    if not strip_path.exists():
        logger.warning(f"Strip no encontrado en {strip_path}")
        return

    try:
        img = Image.open(strip_path).convert("RGBA")

        target_w, target_h = 1125, 369
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h

        if img_ratio > target_ratio:
            new_h = target_h
            new_w = int(target_h * img_ratio)
        else:
            new_w = target_w
            new_h = int(target_w / img_ratio)

        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        left = (new_w - target_w) / 2
        top = (new_h - target_h) / 2
        right = (new_w + target_w) / 2
        bottom = (new_h + target_h) / 2

        strip_final = img_resized.crop((left, top, right, bottom))

        strip_final.save(tmp_dir / "strip@2x.png")
        strip_final.resize((375, 123), Image.Resampling.LANCZOS).save(
            tmp_dir / "strip.png"
        )
    except Exception as e:
        logger.exception(f"Error procesando strip: {e}")


def generate_pass_assets(tmp_dir: Path):
    assets_dir = Path(PASSKIT_ASSETS_DIR)

    icon_source = PASSKIT_STYLE.get("ICON")
    icon_img = _load_image_from_source(icon_source, assets_dir)
    _save_icon(icon_img, tmp_dir)

    logo_source = PASSKIT_STYLE.get("LOGO")
    logo_img = _load_image_from_source(logo_source, assets_dir)
    _save_logo(logo_img, tmp_dir)

    strip_path = PASSKIT_STYLE.get("STRIP", assets_dir / "strip.png")
    if strip_path:
        _save_strip(strip_path, tmp_dir)


def generate_pass(persona: Persona, use_acreditacion: bool = False) -> PassResult:
    """Genera el archivo .pkpass y el QR para una Persona.

    Args:
        persona: Instancia de Persona para la cual generar el pase
        use_acreditacion: Si es True, usa `persona.acreditacion` como identificador
            (serialNumber, barcode, QR y nombre de fichero). Si no existe,
            cae al `correo`.

    Returns:
        PassResult con pkpass (bytes), qr_png (bytes) y acreditacion (str)

    Raises:
        RuntimeError: Si wallet no está instalado o hay error de certificados
    """
    try:
        from wallet.models import Pass, Barcode, BarcodeFormat, EventTicket
    except ImportError:
        raise RuntimeError(
            "La librería 'wallet-py3k' no está instalada. Instala con: pip install wallet-py3k"
        )

    import qrcode
    from PIL import Image

    acreditacion = persona.acreditacion or ""

    # Identificador que se usará para QR, serialNumber y nombre de fichero
    id_value = persona.acreditacion if (use_acreditacion and persona.acreditacion) else persona.correo

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)

        # Generar assets (icono, logo, strip)
        generate_pass_assets(tmp_dir)

        # Generar QR (usa id_value en lugar de correo cuando corresponda)
        qr_buffer = io.BytesIO()
        qrcode.make(id_value).save(qr_buffer, format="PNG")
        qr_bytes = qr_buffer.getvalue()

        # Construir el pase
        ticket = EventTicket()
        context = build_substitution_context(persona)

        # Preparar campos (posible inyección del campo 'acreditacion' cuando se use acreditación)
        from copy import deepcopy

        fields_to_use = deepcopy(PASSKIT_FIELDS)
        if use_acreditacion and persona.acreditacion:
            aux = fields_to_use.get("auxiliary", [])
            if not any(f.get("key") == "acreditacion" for f in aux):
                aux.append({"key": "acreditacion", "label": "Acreditación", "value": "{acreditacion}"})
                fields_to_use["auxiliary"] = aux

        # Añadir campos procesados
        for area, campos_config in fields_to_use.items():
            method_name = f"add{area.capitalize()}Field"
            if hasattr(ticket, method_name):
                method = getattr(ticket, method_name)
                processed = process_fields(campos_config, context, area)
                if (
                    area == "primary"
                    and not processed
                    and not PASSKIT_STYLE.get("STRIP")
                ):
                    method("placeholder", "", "")
                for field in processed:
                    method(field["key"], field["value"], field["label"])
        # Configuración del pase
        pass_obj = Pass(
            ticket,
            passTypeIdentifier=PASSKIT_AUTH["PASS_TYPE_ID"],
            organizationName=PASSKIT_EVENT["ORG"],
            teamIdentifier=PASSKIT_AUTH["TEAM_ID"],
        )

        # usar id_value como serial y código de barras
        pass_obj.serialNumber = id_value
        pass_obj.description = PASSKIT_EVENT["DESC"]
        pass_obj.foregroundColor = PASSKIT_STYLE["FG_COLOR"]
        pass_obj.backgroundColor = PASSKIT_STYLE["BG_COLOR"]
        pass_obj.labelColor = PASSKIT_STYLE["LABEL_COLOR"]
        pass_obj.barcode = Barcode(message=id_value, format=BarcodeFormat.QR)

        # Fecha y localización para que aparezca en pantalla de inicio
        if PASSKIT_EVENT.get("DATE"):
            from datetime import timezone, timedelta

            tz = timezone(timedelta(hours=1))
            date_with_tz = PASSKIT_EVENT["DATE"].replace(tzinfo=tz)
            pass_obj.relevantDate = date_with_tz.isoformat()

        if PASSKIT_EVENT.get("LOCATION"):
            pass_obj.locations = [PASSKIT_EVENT["LOCATION"]]

        # Añadir imágenes
        for img_file in tmp_dir.glob("*.png"):
            with open(img_file, "rb") as f:
                pass_obj.addFile(img_file.name, f)

        # Firmar el pase
        cert_pem, key_pem = extract_p12_certificates(
            PASSKIT_AUTH["P12_PATH"], PASSKIT_AUTH["P12_PASSWORD"], tmp_dir
        )
        wwdr_pem = ensure_wwdr_pem(PASSKIT_AUTH["WWDR_CERT"], tmp_dir)

        pkpass_buffer = io.BytesIO()
        pass_obj.create(cert_pem, key_pem, wwdr_pem, "", zip_file=pkpass_buffer)
        pkpass_bytes = pkpass_buffer.getvalue()

        if len(pkpass_bytes) == 0:
            raise RuntimeError("El archivo .pkpass generado está vacío")

    return PassResult(pkpass=pkpass_bytes, qr_png=qr_bytes, acreditacion=acreditacion)


def main():
    logger.info("pkpassBuilder - ejecución local")

    # CLI: aceptar flag --use-acreditacion para usar el campo `acreditacion`
    import argparse

    parser = argparse.ArgumentParser(
        prog="pkpass_builder",
        description="Genera .pkpass y códigos QR desde un JSON de personas",
    )
    parser.add_argument("json_file", help="Fichero JSON con las personas")

    # flags mutuamente excluyentes: --use-acreditacion o --both
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-a",
        "--use-acreditacion",
        action="store_true",
        help="Usar el campo 'acreditacion' como identificador (serial/QR/fichero) en lugar del correo",
    )
    group.add_argument(
        "-b",
        "--both",
        action="store_true",
        help="Generar BOTH: entradas (email) y badges (acreditación) en la misma ejecución",
    )

    args = parser.parse_args()

    json_file = args.json_file
    use_acreditacion = args.use_acreditacion
    both_mode = args.both

    # Verificar configuración mínima
    if not PASSKIT_AUTH["P12_PATH"] or not Path(PASSKIT_AUTH["P12_PATH"]).exists():
        logger.error("Error: certificado P12 no configurado o no existe")
        logger.error(f"Ruta configurada: {PASSKIT_AUTH['P12_PATH']}")
        sys.exit(1)

    if not PASSKIT_AUTH["WWDR_CERT"] or not Path(PASSKIT_AUTH["WWDR_CERT"]).exists():
        logger.error("Error: certificado WWDR no configurado o no existe")
        logger.error(f"Ruta configurada: {PASSKIT_AUTH['WWDR_CERT']}")
        sys.exit(1)

    logger.info("Certificados verificados")

    logger.info(f"Cargando personas desde {json_file}...")
    personas = cargar_personas(json_file)
    logger.info(f"Cargadas {len(personas)} personas")

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Crear subcarpetas separadas para entradas (email) y badges (acreditación)
    (output_dir / "qr").mkdir(exist_ok=True)
    (output_dir / "qr" / "entradas").mkdir(exist_ok=True)
    (output_dir / "qr" / "badges").mkdir(exist_ok=True)

    (output_dir / "pass").mkdir(exist_ok=True)
    (output_dir / "pass" / "entradas").mkdir(exist_ok=True)
    (output_dir / "pass" / "badges").mkdir(exist_ok=True)

    exitosos = 0
    fallidos = 0




    for i, persona in enumerate(personas, 1):
        # Modo BOTH: generar badge (si tiene acreditación) y/o entrada (si no tiene acreditación)
        if both_mode:
            # badges: solo si persona tiene acreditacion
            if persona.acreditacion:
                id_used = persona.acreditacion
                logger.info(f"[{i}/{len(personas)}] {persona.nombre} (badge: {id_used})...")
                try:
                    result = generate_pass(persona, use_acreditacion=True)
                    file_base = (
                        str(persona.token) if persona.token else str(id_used)
                    )
                    file_base = file_base.replace("@", "_").replace(".", "_").replace("/", "_").replace(" ", "_")
                    pkpass_path = output_dir / "pass" / "badges" / f"{file_base}.pkpass"
                    pkpass_path.write_bytes(result.pkpass)
                    qr_path = output_dir / "qr" / "badges" / f"{file_base}.png"
                    qr_path.write_bytes(result.qr_png)
                    logger.info("Generado badge — fichero: %s", pkpass_path.name)
                    exitosos += 1
                except Exception:
                    logger.exception("Error generando badge para %s", id_used)
                    fallidos += 1

            # entradas: generar siempre (también para personas con acreditacion)
            id_used = persona.correo
            logger.info(f"[{i}/{len(personas)}] {persona.nombre} (entrada: {id_used})...")
            try:
                result = generate_pass(persona, use_acreditacion=False)
                file_base = (
                    str(persona.token) if persona.token else str(id_used)
                )
                file_base = file_base.replace("@", "_").replace(".", "_").replace("/", "_").replace(" ", "_")
                pkpass_path = output_dir / "pass" / "entradas" / f"{file_base}.pkpass"
                pkpass_path.write_bytes(result.pkpass)
                qr_path = output_dir / "qr" / "entradas" / f"{file_base}.png"
                qr_path.write_bytes(result.qr_png)
                logger.info("Generado entrada — fichero: %s", pkpass_path.name)
                exitosos += 1
            except Exception:
                logger.exception("Error generando entrada para %s", id_used)
                fallidos += 1

            # continuar al siguiente persona
            continue

        # Modo exclusivo (como antes)
        if not should_process_persona(persona, use_acreditacion):
            logger.info(
                "[SKIP] %s — modo: %s — (acreditacion: %s)",
                persona.nombre,
                "acreditacion" if use_acreditacion else "entrada",
                persona.acreditacion,
            )
            continue

        id_used = persona.acreditacion if (use_acreditacion and persona.acreditacion) else persona.correo
        logger.info(f"[{i}/{len(personas)}] {persona.nombre} ({id_used})...")
        try:
            result = generate_pass(persona, use_acreditacion=use_acreditacion)

            # Si el JSON incluye `token`, usarlo como nombre base del fichero (sanitizado)
            if persona.token:
                file_base = (
                    str(persona.token).replace("@", "_").replace("/", "_").replace(" ", "_")
                )
            else:
                file_base = (
                    str(id_used).replace("@", "_").replace(".", "_").replace(" ", "_")
                )

            # Guardar en subcarpeta correspondiente
            subfolder = "badges" if use_acreditacion else "entradas"
            pkpass_path = output_dir / "pass" / subfolder / f"{file_base}.pkpass"
            pkpass_path.write_bytes(result.pkpass)
            qr_path = output_dir / "qr" / subfolder / f"{file_base}.png"
            qr_path.write_bytes(result.qr_png)
            logger.info("Generado — fichero: %s", pkpass_path.name)
            exitosos += 1
        except Exception:
            logger.exception("Error generando pase para %s", id_used)
            fallidos += 1

    logger.info("=" * 50)
    logger.info(f"Exitosos: {exitosos}")
    logger.info(f"Fallidos: {fallidos}")
    logger.info(f"Passkits guardados en: {output_dir.absolute()}")
    logger.info(f"QR codes guardados en: {(output_dir / 'qr').absolute()}")
