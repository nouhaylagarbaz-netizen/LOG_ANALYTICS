import ipaddress
import json
import logging
from urllib import request, error

logger = logging.getLogger(__name__)


def get_location(ip):
    """Recherche une IP publique avec le service déjà utilisé dans le projet."""
    try:
        address = ipaddress.ip_address(ip)
        if not address.is_global:
            return {'country': 'Adresse non publique'}
        req = request.Request(f'https://ipinfo.io/{address}/json',
                              headers={'User-Agent': 'LOG_ANALYTICS/1.0'})
        with request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        if not isinstance(data, dict) or not data.get('country'):
            logger.warning('Pays absent pour %s', ip)
            return None
        return data
    except (ValueError, TypeError, OSError, error.URLError):
        logger.exception('Erreur de géolocalisation pour %s', ip)
        return None
