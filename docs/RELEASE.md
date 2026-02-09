Checklist de publicación

1. Actualizar `CHANGELOG.md` con los cambios desde `[Unreleased]`.
2. Aumentar versión en la etiqueta de release (git tag).
3. Verificar que `LICENSE` es la deseada.
4. Revisar `README.md`, `CONTRIBUTING.md` y `AUTHORS`.
5. Crear release en GitHub con notas claras.
6. Publicar anuncio (si procede).

Notas:
- No subir certificados ni archivos sensibles.
- Asegúrate de que CI pasa antes de publicar.

Nota adicional: Este repositorio se ha reorganizado para publicarse como `pkpassBuilder`. Si vas a subir a un nuevo remoto, crea un repositorio vacío en el servicio elegido y empuja esta rama como `main`.