"""Servicio de notificaciones. Correo de suscripción/estado en modo simulado:
registra el envío en consola y devuelve el contenido (sin credenciales reales)."""
import logging

log = logging.getLogger("ferremas.notificaciones")
logging.basicConfig(level=logging.INFO)

_BANDEJA = []  # historial en memoria (para pruebas)


def enviar_correo(destinatario, asunto, cuerpo):
    mensaje = {"para": destinatario, "asunto": asunto, "cuerpo": cuerpo}
    _BANDEJA.append(mensaje)
    log.info("[CORREO SIMULADO] -> %s | %s", destinatario, asunto)
    return mensaje


def correo_bienvenida(correo):
    return enviar_correo(
        correo, "¡Bienvenido a FERREMAS!",
        "¡Felicitaciones! Te suscribiste a las novedades y ofertas de FERREMAS. "
        "Recibirás descuentos especiales en compras de más de 4 artículos.",
    )


def bandeja():
    return list(_BANDEJA)
