docker cp backup_db_container.sh ratecompany_db_1:/backup_db_container.sh
docker exec -it ratecompany_db_1 bash "./backup_db_container.sh"
docker cp ratecompany_db_1:/jobguydb_backup.sql jobguydb_backup.sql
zip jobguydb_backup.sql.zip jobguydb_backup.sql
# /home/ubuntu/go/bin/gdrive upload /home/ubuntu/sync/kikparts.sql.zip