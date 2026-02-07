"""Limitador de tasa por dominio con backoff exponencial para enriquecimiento paralelo."""

import logging
import threading
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """Limitador de tasa que serializa peticiones con un intervalo mínimo entre ellas."""

    def __init__(self, min_interval: float = 0.3):
        self._lock = threading.Lock()
        self._last_request = 0.0
        self._min_interval = min_interval

    def acquire(self):
        """Espera el tiempo necesario para respetar el intervalo mínimo."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request = time.monotonic()


def enrich_with_backoff(event, enrich_fn, rate_limiter: RateLimiter, max_retries: int = 3):
    """
    Ejecuta una función de enriquecimiento con rate limiting y backoff exponencial.

    Args:
        event: Evento a enriquecer.
        enrich_fn: Callable que realiza el enriquecimiento.
        rate_limiter: Instancia de RateLimiter compartida.
        max_retries: Número máximo de reintentos.
    """
    for attempt in range(max_retries):
        rate_limiter.acquire()
        try:
            enrich_fn(event)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.debug(f"Reintentando enriquecimiento (intento {attempt + 1}): {e}")
                time.sleep(wait)
            else:
                logger.warning(f"Error enriqueciendo después de {max_retries} intentos: {e}")
