# [FILE SETTINGS]
SCHEDULE_HEADERS = ["Jour", "Heure", "T", "Numéro", "Joueur/Equipe", "Classement", "Joueur/Equipe", "Classement", "Tableau", "Vainqueur", "Score", "Suivant"]
MATCHS_HEADERS = ["Num", "Joueur1", "Cl", "Joueur2", "Cl", "Tableau", "Vainqueur", "Score", "Suivant"]
PLAYERS_HEADERS = ["Joueur", "Classement", None, "Equipe", "Classement"]
SCHEDULE_COLUMN_WIDTHS = [15, 12, 3, 8, 27, 10, 27, 10, 9, 27, 12, 10]
MATCHS_COLUMN_WIDTHS = [7, 27, 5, 27, 5, 8, 27, 18, 10]
EXCEL_FILENAME = "Tournoi_Royans_Vercors_2024.xlsx"
PLAYERS_COLUMN_WIDTHS = [30, 12, 5, 30, 12]
ERRORS_REPORT_SHEET = "Bilan des erreurs"
MATCHS_REPORT_SHEET = "Bilan des matchs"
SCHEDULE_SHEET_NAME = "Programmation"
PLAYERS_SHEET_NAME = "Inscrits"
REPORT_FILENAME = "Bilan.xlsx"
MATCH_SHEET_NAME = "Matchs"


# [FORMULAS]
MATCHS_FORMULA_COLUMN_C = "=IFERROR(VLOOKUP(BROWNUM,Inscrits!$A$2:$B$200,2,0), IFERROR(VLOOKUP(BROWNUM,Inscrits!$D$2:$E$200,2,0),0))"
MATCHS_FORMULA_COLUMN_E = "=IFERROR(VLOOKUP(DROWNUM,Inscrits!$A$2:$B$200,2,0), IFERROR(VLOOKUP(DROWNUM,Inscrits!$D$2:$E$200,2,0),0))"
SCHEDULE_FORMULA = "=IF(DROWNUM<>0, VLOOKUP(DROWNUM, Matchs!$A$1:$M$199, COLUMN, 0), 0)"
PLAYER_NAME_FORMULA = "=IF(ISBLANK(CASE), \"PLAYER\", CASE)"

# [SETTINGS]
WEEKEND_START_HOUR = "7H30"
WEEK_START_HOUR = "16H30"
MAX_HOUR = "22H30"
