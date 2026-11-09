"""Lancement : python storage/main.py [--geolocate]."""
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from ingestion import raw
from processing import extract_transforme, geo_location, analytics
from storage.dashboard import display_dashboard

logger = logging.getLogger(__name__)


def configure_logging():
    log_dir = PROJECT_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    handler = RotatingFileHandler(log_dir / 'application.log', maxBytes=1000000,
                                  backupCount=5, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(message)s'))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def load_countries(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            raise ValueError('Le cache doit associer une IP à un pays')
        return data
    except (OSError, ValueError):
        logger.exception('Cache des pays illisible')
        raise


def main():
    parser = argparse.ArgumentParser(description='Pipeline des logs SSH')
    parser.add_argument('--geolocate', action='store_true',
                        help='Rechercher les pays des IP publiques sur ipinfo.io (accès réseau)')
    args = parser.parse_args()
    configure_logging()
    try:
        logger.info('Démarrage du pipeline')
        rows = raw.toRows(PROJECT_DIR / 'data')
        records = extract_transforme.extract(rows)
        if not records:
            raise ValueError('Aucune ligne de log reconnue')
        output = PROJECT_DIR / 'output'
        output.mkdir(exist_ok=True)
        cache_path = output / 'countries.json'
        countries = load_countries(cache_path)
        if args.geolocate:
            ips = sorted({r['ip'] for r in records if r['status'] == 'Failed' and r['ip']})
            for ip in ips:
                if ip not in countries:
                    location = geo_location.get_location(ip)
                    if location and location.get('country'):
                        countries[ip] = location['country']
            cache_path.write_text(json.dumps(countries, ensure_ascii=False, indent=2), encoding='utf-8')
        summary = analytics.aggregate(records, countries)
        (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info('Pipeline terminé : %s lignes lues, %s analysées', len(rows), len(records))
        print(f'{len(rows)} lignes lues, {len(records)} analysées.')
        display_dashboard(summary, output / 'dashboard.txt')
        print('Rapport enregistré :', output / 'dashboard.txt')
        if not args.geolocate:
            print('Pays : cache local uniquement. Ajouter --geolocate pour rechercher les pays manquants.')
        return 0
    except Exception:
        logger.exception('Échec du pipeline')
        print('Erreur : consulter logs/application.log', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
