Pour ce projet, je suis partie d’un programme qui permettait déjà de lire des logs et d’en extraire certaines informations. Mon travail a été de le compléter pour analyser les tentatives de connexion SSH et obtenir les trois résultats demandés : les échecs par pays, les connexions réussies par utilisateur et les échecs liés à des utilisateurs invalides.

J’ai organisé le traitement en plusieurs étapes. Le programme commence par lire les fichiers, puis il récupère les informations utiles dans chaque ligne. Ensuite, il fait les calculs et affiche les résultats. C’est cet enchaînement qui forme le pipeline.

Dans `ingestion/raw.py`, j’ai conservé la lecture des fichiers du dossier `data`, avec la prise en charge des fichiers texte et des fichiers compressés `.gz`. Pour ces derniers, le programme utilise le module `gzip`. J’ai aussi ajouté la gestion des erreurs de lecture. Si un fichier ne peut pas être ouvert, le problème est enregistré dans les journaux et le traitement s’arrête. Cela évite d’afficher des résultats qui semblent complets alors qu’une partie des fichiers n’a pas été analysée.

La partie extraction se trouve dans `processing/extract_transforme.py`. Elle repose sur des expressions régulières, avec le module `re`. Elles servent à repérer les différentes informations présentes dans une ligne : la date, l’heure, le service, le message et l’adresse IP. J’ai dû corriger l’expression utilisée pour qu’elle accepte notamment les noms de serveurs contenant un tiret et reconnaisse correctement le numéro du processus entre crochets. Les lignes qui ne correspondent pas au format attendu sont signalées dans les journaux.

J’ai ensuite ajouté la récupération du nom d’utilisateur et du résultat de la tentative. Le programme distingue les messages `Accepted`, qui indiquent une connexion réussie, des messages `Failed`, qui indiquent un échec. Il vérifie aussi si le message contient `invalid user`. Par exemple, avec la ligne `Failed password for invalid user test from 8.8.8.8`, il reconnaît une tentative échouée pour l’utilisateur invalide `test`.

Pour les calculs, j’ai créé `processing/analytics.py`. J’y utilise des boucles et des dictionnaires pour parcourir les événements et compter ceux qui correspondent à chaque indicateur.

Le point auquel il fallait faire attention était le double comptage. Une même tentative peut produire plusieurs messages dans les logs. J’ai donc choisi de compter uniquement les lignes SSH reconnues dont le message commence par `Accepted` ou `Failed`. Les messages PAM et les lignes `Invalid user` isolées ne sont pas ajoutés au total.

En revanche, une tentative échouée avec un utilisateur invalide apparaît bien dans deux tableaux : celui des échecs par pays et celui des utilisateurs invalides. Ce n’est pas une erreur : on regarde simplement la même tentative selon deux critères différents. Il ne faut donc pas additionner les totaux de ces tableaux.

Pour la géolocalisation, j’ai adapté `processing/geo_location.py`. J’ai retiré `requests` pour utiliser uniquement des modules disponibles avec Python : `urllib`, `json` et `ipaddress`. Le programme peut demander à `ipinfo.io` le pays d’une adresse IP publique, puis conserver la réponse dans `output/countries.json`. Cela évite de refaire la même recherche à chaque lancement.

Cette recherche reste facultative. Elle se lance avec `--geolocate`. Sans cette option, le programme utilise les pays déjà enregistrés. Si une adresse n’a pas de pays connu, elle est classée dans la catégorie `Inconnu`.

Cette partie a pris du temps, car les premières recherches se faisaient une par une. Un script temporaire a ensuite servi à lancer plusieurs recherches en parallèle et à enregistrer les réponses progressivement. Il a permis d’obtenir le pays de **778 adresses IP**, réparties dans **52 pays**, avant que le service renvoie une erreur `429`. La limite de requêtes avait été atteinte. Les résultats par pays sont donc encore partiels.

Pour l’affichage, j’avais d’abord prévu une page HTML. Je l’ai finalement remplacée par des tableaux dans le terminal pour rester plus proche de ce qui avait été étudié en cours. Le fichier `storage/dashboard.py` prépare les tableaux et les affiche avec `print()`. Il en sauvegarde aussi une copie dans `output/dashboard.txt`, ce qui est plus pratique pour relire les résultats quand le terminal contient beaucoup de lignes.

Le fichier `storage/main.py` rassemble toutes les étapes. C’est lui qui lance la lecture, l’extraction, le chargement des pays, les calculs et l’affichage. Il enregistre également les indicateurs dans `output/summary.json`.

J’ai utilisé `logging` pour garder une trace de l’exécution et des erreurs dans `logs/application.log`. Ce fichier aide à comprendre ce qui s’est passé lorsqu’un problème survient. J’ai aussi limité la taille des journaux avec `RotatingFileHandler` : lorsqu’un fichier atteint environ 1 Mo, une sauvegarde est créée, avec un maximum de cinq sauvegardes.

Sur les fichiers fournis, le programme a lu **65 565 lignes**. Parmi elles, **65 555 ont été reconnues** et **10 ne correspondaient pas au format attendu**. L’analyse a donné **9 090 tentatives échouées**, **une connexion réussie** et **3 251 échecs avec utilisateur invalide**. Les vérifications ont aussi porté sur de petits exemples pour contrôler la lecture des fichiers `.gz`, l’extraction des utilisateurs et le comptage des tentatives.

Enfin, j’ai ajouté un `.gitignore` pour éviter d’inclure les fichiers générés, les journaux et les caches Python dans le dépôt. Le README explique comment lancer le programme et lire les résultats. La partie Git reste à terminer, puisqu’aucun dépôt n’était configuré dans le dossier de travail.

Le projet utilise maintenant uniquement la bibliothèque standard Python. Il reste surtout à confirmer avec le professeur que l’affichage dans le terminal convient pour le dashboard demandé et que les modules employés respectent les consignes du cours.