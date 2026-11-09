"""Affichage des indicateurs dans le terminal avec du Python."""
import logging

logger = logging.getLogger(__name__)


def display_dashboard(summary, destination):
    sections = [
        ('TENTATIVES ECHOUEES PAR PAYS', 'Pays', 'failed_countries'),
        ('TENTATIVES REUSSIES PAR UTILISATEUR', 'Utilisateur', 'successful_users'),
        ('ECHECS AVEC INVALID USER', 'Utilisateur invalide', 'invalid_users'),
    ]
    lines = ['TABLEAU DE BORD - LOG ANALYSER']
    for title, label, key in sections:
        lines.append('')
        lines.append(title)
        lines.append('-' * 65)
        lines.append(f'{label:<45} | Nombre')
        lines.append('-' * 65)
        total = 0
        for name, count in sorted(summary[key].items()):
            lines.append(f'{name:<45} | {count}')
            total += count
        if not summary[key]:
            lines.append('Aucune tentative')
        lines.append(f'Total : {total}')
    lines.append('')
    lines.append('Inconnu : pays absent du cache de geolocalisation.')
    report = '\n'.join(lines)
    print(report)
    try:
        destination.write_text(report + '\n', encoding='utf-8')
        logger.info('Rapport texte enregistré : %s', destination)
    except OSError:
        logger.exception('Impossible de créer le rapport %s', destination)
        raise
