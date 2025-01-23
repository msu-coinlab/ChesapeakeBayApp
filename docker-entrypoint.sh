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

# Determine the service type via an environment variable
case "$SERVICE_TYPE" in
    "web")
        print_message "green" "Starting Web Service..."

        print_message "yellow" "Runing init_script.sh..."

        if [ "$RUN_INIT_SCRIPT" = "True" ]; then
            bash init_script.sh
        fi

        print_message "yellow" "Starting server..."
        python manage.py runserver 0.0.0.0:8000
        ;;

    "alfred_retrieve")
        print_message "green" "Starting Alfred Retrieve..."
        ;;

    "alfred_send")
        print_message "green" "Starting Alfred Send..."
        ;;
    "celery")
        print_message "green" "Starting Celery Worker..."
        ;;

    "celery-beat")
        print_message "green" "Starting Celery Beat..."
        ;;

    "flower")
        print_message "green" "Starting Flower..."
        ;;

    *)
        print_message "red" "Error: SERVICE_TYPE is not set correctly."
        exit 1
        ;;
esac

# Execute the main process
exec "$@"

