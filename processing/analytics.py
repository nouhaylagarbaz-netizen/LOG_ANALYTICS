"""Agrégation des trois indicateurs demandés."""
import logging

logger = logging.getLogger(__name__)


def aggregate(records, countries):
    failed_countries = {}
    successful_users = {}
    invalid_users = {}
    for record in records:
        if record['service'] != 'sshd':
            continue
        if record['status'] == 'Accepted':
            user = record['user']
            successful_users[user] = successful_users.get(user, 0) + 1
        elif record['status'] == 'Failed':
            country = countries.get(record['ip'], 'Inconnu')
            failed_countries[country] = failed_countries.get(country, 0) + 1
            if record['invalid_user']:
                user = record['user']
                invalid_users[user] = invalid_users.get(user, 0) + 1
    logger.info('Agrégation terminée : %s enregistrements', len(records))
    return {'failed_countries': failed_countries,
            'successful_users': successful_users, 'invalid_users': invalid_users}
