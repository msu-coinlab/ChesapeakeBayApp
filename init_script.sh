
#!/bin/bash
set -e

# Function to print messages in color
print_message() {
    local COLOR=$1
    local MESSAGE=$2
    case $COLOR in
        "green")
            echo -e "\e[32m$MESSAGE\e[0m"
            ;;
        "yellow")
            echo -e "\e[33m$MESSAGE\e[0m"
            ;;
        "red")
            echo -e "\e[31m$MESSAGE\e[0m"
            ;;
        *)
            echo "$MESSAGE"
            ;;
    esac
}
print_message "green" "Starting Initialization (init_script.sh)!"

print_message "yellow" "Applying makemigrations..."
python manage.py makemigrations

print_message "yellow" "Applying database migrations..."
python manage.py migrate

print_message "yellow" "Creating Superuser now..."

# // TODO - This super user creation should check if the user already exists
# python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
# python manage.py createsuperuser --noinput --first_name Root --last_name Admin --email $DJANGO_SUPERUSER_EMAIL

print_message "yellow" "Collecting static files..."
python manage.py collectstatic --noinput

print_message "yellow" "Populating Database..."
python manage.py runscript load_data
python manage.py runscript load_geojsons
#python manage.py runscript load_oxygen

print_message "yellow" "Initializing ETA..."
python init_eta.py

print_message "green" "Initialization completed successfully!"
