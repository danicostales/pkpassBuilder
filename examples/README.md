# Ejemplos

Ejemplos funcionales de cómo usar `pkpass_builder`.

## Archivos incluidos

- **`ejemplo_personas.json`**: Datos de ejemplo para generar pases
- **`generar_passkits.py`**: Script de demostración que muestra cómo generar pases

## Uso rápido

### 1. Preparar datos
Edita `ejemplo_personas.json` con tus datos:

```json
[
  {
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "numero": "001"
  }
]
```

### 2. Ejecutar ejemplo

```bash
# Desde la raíz del proyecto
python examples/generar_passkits.py
```

## Notas

Los pases generados se guardan en `output/`

Para configurar certificados y credenciales, consulta el `.env.example` en la raíz del proyecto.
