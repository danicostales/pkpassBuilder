# Guía de Contribución

Gracias por tu interés en contribuir a este proyecto. Esta guía explica cómo colaborar y enviar cambios de forma clara y segura.

## Código de Conducta

Este proyecto sigue los principios de respeto, inclusión y colaboración. Por favor:
- Sé respetuoso con otros colaboradores
- Acepta críticas constructivas
- Enfócate en lo mejor para la comunidad
- Muestra empatía hacia otros miembros

## 🚀 Cómo Contribuir

### 1. Reportar Bugs

Si encuentras un bug, por favor:
1. Verifica que no esté ya reportado en [Issues](../../issues)
2. Crea un nuevo issue incluyendo:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs actual
   - Versión de Python y sistema operativo
   - Logs o capturas de pantalla si es posible

### 2. Sugerir Mejoras

Para sugerir nuevas características:
1. Abre un issue con la etiqueta "enhancement"
2. Describe claramente:
   - El problema que resuelve
   - Cómo debería funcionar
   - Posibles alternativas consideradas

### 3. Pull Requests

#### Antes de empezar
1. Fork el repositorio
2. Clona tu fork localmente
3. Crea una nueva rama desde `main`:
   ```bash
   git checkout -b feature/mi-nueva-caracteristica
   ```

#### Durante el desarrollo
1. Escribe código claro y bien documentado
2. Sigue el estilo de código existente
3. Añade comentarios donde sea necesario
4. Mantén los commits atómicos y con mensajes descriptivos

#### Formato de commits
```
tipo: descripción breve (máx 50 caracteres)

Descripción más detallada si es necesario.
Explica qué cambios se hicieron y por qué.

Fixes #123
```

Tipos de commit:
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, sin cambio de código
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Tareas de mantenimiento

#### Antes de hacer el PR
1. Asegúrate de que el código funciona:
   ```bash
   python generar_passkits.py ejemplo_personas.json  # o: python -m pkpass_builder ejemplo_personas.json
   ```
2. Verifica que no hayas incluido:
   - Certificados (`.p12`, `.cer`)
   - Archivos `.env`
   - Passkits generados (`.pkpass`)
   - Datos personales reales

#### Crear el Pull Request
1. Push a tu fork:
   ```bash
   git push origin feature/mi-nueva-caracteristica
   ```
2. Abre un PR en GitHub
3. Describe claramente:
   - Qué cambios introduces
   - Por qué son necesarios
   - Cómo probaste los cambios
   - Screenshots si aplica

## 🎯 Áreas donde Contribuir

### 🐛 Bugs conocidos
Revisa los [issues con etiqueta "bug"](../../labels/bug)

### Características deseadas
- Soporte para diferentes tipos de pases (cupones, tarjetas de embarque)
- Tests automatizados
- Interfaz web para generar pases
- Soporte para actualización de pases remotos
- Integración con servicios de email
- Plantillas predefinidas para diferentes tipos de eventos

### Documentación
- Traducciones del README
- Tutoriales en video
- Guías paso a paso
- Casos de uso reales
- FAQ
- Evita incluir texto generado automáticamente sin revisión; si usas herramientas de asistencia, revísalo y adáptalo para que suene natural y preciso.

## 🧪 Testing

Actualmente no hay tests automatizados, pero puedes probar manualmente:

```bash
# 1. Configurar entorno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Generar pases de prueba
python generar_passkits.py ejemplo_personas.json

# 3. Verificar que se generaron correctamente
ls -la output/
```

## Estilo de código

### Python
- Sigue [PEP 8](https://pep8.org/)
- Usa nombres descriptivos para variables y funciones
- Documenta funciones con docstrings:
  ```python
  def mi_funcion(param: str) -> bool:
      """Descripción breve de qué hace.
      
      Args:
          param: Descripción del parámetro
          
      Returns:
          Descripción de lo que retorna
          
      Raises:
          ValueError: Cuándo se lanza esta excepción
      """
      pass
  ```

### Comentarios
- Escribe comentarios en español
- Explica el "por qué", no el "qué"
- Mantén los comentarios actualizados

## Seguridad

Si encuentras una vulnerabilidad de seguridad:
1. **NO** abras un issue público
2. Envía un email privado a los maintainers
3. Espera confirmación antes de divulgar

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la misma licencia que el proyecto.

## ❓ Preguntas

¿Tienes dudas? Puedes:
- Abrir un issue con la etiqueta "question"
- Contactar a los maintainers
- Revisar issues cerrados para ver si ya se respondió

---

Gracias por contribuir.
