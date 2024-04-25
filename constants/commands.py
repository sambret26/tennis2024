REVERT_CMD = "mv DB_backup.db DB.db.tmp && mv DB.db DB_backup.db && mv DB.db.tmp DB.db"
SAVE_OLD_DB_CMD = "mv DB.db FILENAME"
BACKUP_CMD = "cp DB.db DB_backup.db"
RESTORE_CMD = "cp FILENAME DB.db"
