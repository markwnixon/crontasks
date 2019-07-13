#!/bin/bash
echo "Syncing Pythonanywhere data to local machine"
echo "Local Machine = ubuntu1700"

backup="felbackup$(date +%s).sql"
echo "Backup mysql dump is: $backup"

excom="mysqldump -u mnixon -h mnixon.mysql.pythonanywhere-services.com 'mnixon\$fel'  > $backup"
pass='Birdie$10'

ssh mnixon@ssh.pythonanywhere.com $excom
echo "mysql dump has been created at python anywhere home directory"

scp mnixon@ssh.pythonanywhere.com:/home/mnixon/$backup /home/mark/databases
echo "mysql dump $backup has been downloaded to /home/mark/databases"

mysql -h localhost -u root -p$pass fel < /home/mark/databases/$backup
echo "local database has been restored to $backup"

echo "Now sync the data files that are excluded from github from pythonanywhere to local machine"

rsync -avzhe ssh "mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/data" "/home/mark/flask/felrun/tmp"
rsync -avzhe ssh "mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/processing" "/home/mark/flask/felrun/tmp"
echo "All necessary files have been synced"


