#!/bin/bash

# Apply database migrations
#sleep 600
#export $(cat /root/variables.env | xargs)
#FILE=/root/run_once.sh
#if [ -f "$FILE" ]; then
#   echo "Execute file ${FILE}"
#   bash "${FILE}"
#   echo "Delete file ${FILE}"
#   rm "${FILE}"
#fi


# Start celery services 
echo "Starting celery services"
systemctl --type=service --state=running
#celery -A api4opt worker --loglevel=info
#celery -A api4opt beat  --loglevel=info
#celery -A api4opt worker --logfile=/tmp/celery-worker.log --loglevel=error --detach
#celery -A api4opt beat  --logfile=/tmp/celery-beat.log --loglevel=error --detach
# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000

