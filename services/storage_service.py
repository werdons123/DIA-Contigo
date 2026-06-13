"""
Servicio de almacenamiento de imágenes — Azure Blob Storage.

Guarda las fotos de comida/menú subidas por el usuario y devuelve la URL para
persistir en `analisis_nutricionales.imagen_url` (ver docs/06_base_de_datos.md).

Modo demo: si `config.STORAGE_DEMO_MODE` es True, las imágenes se guardan en una
carpeta local (`data/uploads/`) y se devuelve una ruta de archivo local — útil
para desarrollo sin una cuenta de Azure Storage.
"""

import os
import uuid

import config

_LOCAL_UPLOADS_DIR = os.path.join("data", "uploads")


def guardar_imagen(imagen_bytes: bytes, usuario_id: str, extension: str = "jpg") -> str:
    """Guarda la imagen y devuelve la URL/ruta para persistir en BD."""
    nombre_archivo = f"{usuario_id}/{uuid.uuid4()}.{extension}"

    if config.STORAGE_DEMO_MODE:
        return _guardar_local(imagen_bytes, nombre_archivo)

    return _guardar_azure(imagen_bytes, nombre_archivo)


def _guardar_azure(imagen_bytes: bytes, nombre_archivo: str) -> str:
    from azure.storage.blob import BlobServiceClient

    client = BlobServiceClient.from_connection_string(
        config.AZURE_STORAGE_CONNECTION_STRING
    )
    container = client.get_container_client(config.AZURE_STORAGE_CONTAINER)

    try:
        container.create_container()
    except Exception:
        pass  # el contenedor ya existe

    blob_client = container.get_blob_client(nombre_archivo)
    blob_client.upload_blob(imagen_bytes, overwrite=True)
    return blob_client.url


def _guardar_local(imagen_bytes: bytes, nombre_archivo: str) -> str:
    ruta_completa = os.path.join(_LOCAL_UPLOADS_DIR, nombre_archivo)
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)

    with open(ruta_completa, "wb") as f:
        f.write(imagen_bytes)

    return ruta_completa
