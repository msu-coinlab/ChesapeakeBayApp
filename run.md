celery -A cast worker --loglevel=info
celery -A cast beat  --loglevel=info
python manage.py runserver 192.168.1.3:8000       

