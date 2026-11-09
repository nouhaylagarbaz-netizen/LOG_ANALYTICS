import gzip
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def toRows(path) -> list[str]:
    """
    Lit tous les fichiers d'un répertoire (.gz inclus).

    in  : path (répertoire)
    out : liste de lignes
    """
    data_dir = Path(path)
    rows = []

    try:
        files = sorted(data_dir.iterdir())
    except OSError:
        logger.exception("Impossible de lire le répertoire %s", path)
        raise

    for file_path in files:
        if not file_path.is_file():
            continue

        opener = gzip.open if file_path.suffix == '.gz' else open
        try:
            with opener(file_path, mode='rt', encoding='utf-8', errors='replace') as f:
                rows.extend(f.readlines())
        except (OSError, EOFError):
            logger.exception("Impossible de lire le fichier %s", file_path)
            raise

    return rows


if __name__ == '__main__':
    data = toRows('./data')
    if data:
        print(data[:10])
