# [SUCCESS]
DELETE_CALENDAR = "Suppression des evenements\nAttention, le traitement peut être long, et mettre en pause le reste des opérations"
UPDATE_CALENDAR = "Mise à jour du calendrier\nAttention, le traitement peut être long, et mettre en pause le reste des opérations"
UPDATE_PLAYERS_KO = "/!\ La liste des joueurs n'a pas été mise à jour correctement (Code d'erreur CODE)"
UPDATE_MATCHS_KO = "/!\ La liste des matchs n'a pas été mise à jour correctement (Code d'erreur CODE)"
UPDATE_COURTS_KO = "/!\ La liste des courts n'a pas été mise à jour correctement (Code d'erreur CODE)"
DB_BACKUP = "L'ancienne base de données à été sauvegardée dans le fichier FILENAME"
BDD_RESTAURED = "La base de données à été restaurée à partir du fichier FILENAME"
NB_INSCRITS_BY_CAT = "Nombre d'inscrits par classement pour chaque catégorie :"
COURT_UPDATE = "Le match MATCH_NAME à été déplacé sur le court COURT"
RESULT_UPDATE = "Le résultat du match MATCH_NAME a été mis à jour"
STARTED_APPLICATION = "L'application a (re)démarré avec succès"
UPDATE_PLAYERS_OK = "La liste des joueurs a été mise à jour"
CAL_UNSET = "L'état du calendrier à bien été réinitialisé"
UPDATE_MATCHS_OK = "La liste des matchs a été mise à jour"
UPDATE_COURTS_OK = "La liste des courts a été mise à jour"
CALENDAR_UPDATED = "Fin de la mise à jour du calendrier"
CALENDAR_DELETED = "Suppression des evenements terminé"
REVERT = "Vous êtes revenus à une version précedente"
CAL_UNSYNC = "Le calendrier a bien été désynchronisé"
NB_INSCIRTS = "Nombre d'inscrits par classements :"
CAL_SYNC = "Le calendrier a bien été synchronisé"
MATCH_WINNER = "Le vainqueur du match MATCH_NAME"
DB_SAVE = "Le fichier FILENAME a été enregistré"
DB_FILLED = "La base de données à été remplie"
MOJA_UNSYNC = "MOJA a bien été désynchronisé"
NO_PG = "Aucune programmation prévue le DATE"
MOJA_SYNC = "MOJA a bien été synchronisé"
PG = "Voici la programmation du DATE:\n"
INCOMING_QUALIFIED = "Qualifié entrant"
TOTAL = "Total"

# [QUESTIONS]
WINNER_AND_SCORE_ALREADY_EXISTS = "Le vainqueur et le score de ce match sont déjà renseignés\nVoulez-vous renseigner de nouveaux résultats ?"
WINNER_ALREADY_EXISTS = "Le vainqueur de ce match est déjà renseigné\nVoulez-vous renseigner un nouveau vainqueur ?"
WHICH_UPDATE_LIST = [("Les joueurs", "1", "green"), ("Les Matchs", "2", "blue"), ("Les Courts", "3", "red")]
WHICH_EXPORT_LIST = [("Le tableur excel", "1", "green"), ("La base de données", "2", "blue")]
SYNC_LIST = [("Synchronier", "1", "Green"), ("Désynchroniser", "0", "Red")]
WHICH_FILE = "A quelle date voulez vous restaurer la base de données?"
HOW_CAL_SYNC = "Comment voulez-vous synchroniser le calendrier ?"
WHICH_COURT = "Sur quel court voulez vous déplacer ce match ?"
ASK_FOR_DETAILS = "Afficher les détails des classements ?"
HOW_MOJA_SYNC = "Comment voulez-vous synchroniser MOJA ?"
YES_OR_NO = [("Oui", "1", "Green"), ("Non", "0", "Red")]
SET_3_RESULT = "Quel est le résultat du troisième set ?"
SET_2_RESULT = "Quel est le résultat du deuxième set ?"
SET_1_RESULT = "Quel est le résultat du premier set ?"
WHICH_PLAYER_WON = "Quel joueur a gagné le match ?"
QUESTION_MORE = ("Afficher plus", "Next", "Blue")
WHICH_UPDATE = "Que voulez-vous mettre à jour?"
WHICH_EXPORT = "Que voulez-vous exporter?"

# [ERROR]
EXTENSION_NOT_FOUND = "L'extension du fichier n'est pas reconnue. Seules les extensions .db et .xlsx sont acceptées."
MODIF_COURT_UNVALID_PARAMETERS = "La commande $modifCourt doit être suivi du nom d'un match (ex : $modifCourt SM27)"
UPDATE_PG_UNVALID_PARAMETERS = "Veuillez entrer en paramètre un match, un jour au format dd/mm et une heure"
UNKNOWN_COMMAND = "La commande COMMAND n'existe pas, pour lister les commandes disponibles, tapez $cmd"
RESULT_UNVALID_PARAMETERS = "La commande $result doit être suivi du nom d'un match (ex : $result SM27)"
UPDATE_DAY_UNVALID_PARAMETERS = "Veuillez entrer en paramètre un match et un jour au format dd/mm"
NO_BACKUP_FILES = "Aucune sauvegarde n'a été trouvée, impossible de restaurer la base de données"
UPDATE_PLAYERS_UNVALID_PARAMETERS = "Veuillez entrer en paramètre un match, un nom, un prénom"
CALENDAR_ALREADY_RUNNING = "Impossible de mettre à jour le calendrier pour le moment"
UPDATE_HOUR_UNVALID_PARAMETERS = "Veuillez entrer en paramètre un match et une heure"
FORBIDDEN = "Tu ne disposes pas des droits necessaires pour cette action..."
NO_MATCH = "Le match MATCH_NAME n'a pas été trouvé en base de données"
DAY_NOT_IN_TOURNAMENT = "Le jour indiqué DAY est hors du tournoi"
UNVALID_TEAM_NAME = "Format de nom d'équipe invalide : TEAMNAME"
NO_MATCH_INFO = "Aucune info trouvée pour le match MATCH_NAME"
SHEET_NOT_FOUND = "La feuille SHEET n'a pas été trouvée"
UNVALID_DAY = "Veuillez rentrer un jour au format dd/mm"
UNVALID_HOUR = "L'heure entrée n'est pas correcte"
PLAYER_NOT_FOUND = "Joueur non trouvé : "
UNKNOWN_PLAYER = "Joueur inconnu"

# [COMMANDS LIST]
COMMAND_LIST = "Voici la liste des commandes disponibles : \n \
$maj : Permet de mettre à jour les matchs, les joueurs ou les courts depuis MOJA \n \
$majMatchs : Permet de mettre à jour les matchs depuis MOJA \n \
$majJoueurs : Permet de mettre à jour les joueurs depuis MOJA \n \
$majCourts : Permet de mettre à jour les courts depuis MOJA \n \
$nb : Permet d'afficher le nombre d'inscrits dans une catégorie ou dans le tournois \n \
$infos : Permet d'obtenir des informations sur un match à partir de son identifiant (alias : $info)\n \
$resultat : Permet de définir le résultat d'un match à partir de son identifiant (alias : $result) \n \
$modifCourt : Permet d'ajouter/modifier le court associé à un match à partir de son identifiant (alias : $mc)\n \
$modifJoueur1 : Permet d'ajouter/modifier le joueur 1 associé à un match à partir de son identifiant (alias : $mj1)\n \
$modifJoueur2 : Permet d'ajouter/modifier le joueur 2 associé à un match à partir de son identifiant (alias : $mj2)\n \
$modifJour : Permet d'ajouter/modifier le jour d'un match à partir de son identifiant (alias : $mj)\n \
$modifHeure : Permet d'ajouter/modifier l'horaire d'un match à partir de son identifiant (alias : $mh)\n \
$modifPg : Permet d'ajouter/modifier la programmation (jour et heure) d'un match à partir de son identifiant (alias : $mpg)\n \
$programmation : Permet d'obtenir la programmation d'une journée (alias : $program/$pg)\n \
$pgw : Permet de générer un message destiné à whats'app, à propos de la programmation du jour \n"
COMMAND_LIST_2 = "$revert : Permet de supprimer la dernière modification /!\ : MOJA/CAL OUT \n \
$export : Permet d'exporter la base de données ou le tableur excel associé \n \
$db : Permet d'exporter la base de données \n \
$excel : Permet de générer un tableur excel à partir de la base de données \n \
$restore : Permet de restaurer une ancienne version de la base de données /!\ : MOJA/CAL OUT \n \
$updateCalendar : Permet de mettre à jour le calendrier (alias : $updateCal/$uc)\n \
$deleteCalendar : Permet de supprimer les évènements du calendrier (alias : $deleteCal/$dc)\n \
$moja : Permet de synchroniser/désynchroniser MOJA \n \
$cal : Permet de synchroniser/désynchroniser le calendrier \n \
$clear : Permet de supprimer les derniers messages d'un channel (100 par défaut) \n \n \
Certaines commandes peuvent être soumises à une vérification des droits \n \n \
Pour plus d'informations sur l'utilisation d'une commande, lancez-la \n\n \
La commande $majJoueurs est executée automatiquement toutes les minutes\n \
La commande $pgw est executée automatiquement tous les jours à 8h58\n \
La commande $updateCalendar est executée automatiquement tous les jours à 6h \
"
