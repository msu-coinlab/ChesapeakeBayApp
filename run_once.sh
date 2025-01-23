#rabbitmq-plugins enable rabbitmq_management
#rabbitmqctl add_user "${RABBITMQ_DEFAULT_USER}" "${RABBITMQ_DEFAULT_PASS}"
#rabbitmqctl set_permissions -p / "${RABBITMQ_DEFAULT_USER}" ".*" ".*" ".*"

#rabbitmqctl add_user "${AMQP_USERNAME}" "${AMQP_PASSWORD}"
#rabbitmqctl set_permissions -p / "${AMQP_USERNAME}" ".*" ".*" ".*"



#echo "In create DB"
#mysql -e "CREATE DATABASE ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;"
#mysql -e "CREATE USER ${DB_USER}@localhost IDENTIFIED BY '${DB_PASSWD}';"
#mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
#mysql -e "FLUSH PRIVILEGES;"

echo "Apply database migrations"
python manage.py migrate

#echo "Create superuser"
python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"

print_message "yellow" "Applying makemigrations..."
python manage.py makemigrations

print_message "yellow" "Applying database migrations..."
python manage.py migrate

print_message "yellow" "Creating Superuser now..."
python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"

print_message "yellow" "Collecting static files..."
python manage.py collectstatic --noinput

print_message "yellow" "Populating Database..."
python manage.py runscript load_data
python manage.py runscript load_geojsons
#python manage.py runscript load_oxygen

print_message "yellow" "Initializing ETA..."
python init_eta.py

