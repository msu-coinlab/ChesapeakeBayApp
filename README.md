# Language Learning Assistant

## Introduction
Language Learning Assistant is a Django-based web application designed to aid language learners. This app features translation, chat, and conversation editing capabilities, powered by ChatGPT and an integrated text-to-voice converter. It supports Google account login for user authentication and is fully dockerized for easy setup and deployment. The user interface is enhanced using HTMX, providing a dynamic and responsive experience.

## Features
- **Translation**: Translate text into different languages.
- **Chat Interface**: Engage in conversations with a ChatGPT-powered bot.
- **Conversation Editing**: Edit and refine conversations for learning purposes.
- **Text-to-Voice Conversion**: Convert translations to audio for auditory learning.
- **Google Account Integration**: Secure and convenient login using Google accounts.
- **Dynamic User Interface**: Enhanced with HTMX for a responsive and interactive experience.
- **Dockerized Environment**: Easy setup and deployment with Docker and Docker Compose.

## Technology Stack
- **Backend**: Django
- **Frontend**: HTMX for dynamic UI, [other frontend technologies]
- **AI and NLP**: ChatGPT
- **Text-to-Voice**: Text-to-voice conversion API
- **Authentication**: Google OAuth
- **Cache and Sessions**: Redis
- **Containerization**: Docker and Docker Compose
- **Database**: [Database used, e.g., PostgreSQL]

## Installation

### Prerequisites
- Docker and Docker Compose

### Setup
1. Clone the repository:
```
git clone [repository URL]
cd [repository name]
```
2. Create a `variables.env` file in the project root with the necessary environment variables:
```
# Example content of variables.env
DB_NAME=db_name
DB_USER=myuser
DB_PASSWD=yourpassword1
DJ_DEBUG=True
DJ_SECRET_KEY="django-insecure-hs7j037urx7iav+7#10%-vu4l4f5@@-1_zo)oft3g8vf2jmp"
EMAIL_HOST=posteo.de
EMAIL_HOST_USER=username@posteo.net
EMAIL_HOST_PASSWORD=yourpassword2
EMAIL_USE_SSL=True
EMAIL_PORT=465
DEFAULT_FROM_EMAIL=username@posteo.net
REDIS_HOST=redis
REDIS_USERNAME=guest
REDIS_PASSWORD=yourpassword3
REDIS_PORT=6379
REDIS_DB=5
REDIS_DB_OPT=6
REDIS_DB_CELERY=3
REDIS_DB_CACHE=4
DJANGO_SUPERUSER_FIRST_NAME=Yourfirstname
DJANGO_SUPERUSER_LAST_NAME=Yourlastname
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=username@posteo.net
DJANGO_SUPERUSER_PASSWORD=yourpasword4
HOST_IP=192.168.1.1
CELERY_BROKER=redis://redis:6379/3
CELERY_BACKEND=redis://redis:6379/4
```

3. Run the application using Docker Compose:
```
docker compose up -d
```

## Usage
- Access the application at `http://localhost:[port]` (replace `[port]` with the port you've configured, default is usually 8000).

## Contributing
Contributions to the Language Learning Assistant are welcome! Here's how to contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b my-new-feature`.
3. Make your changes and commit: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin my-new-feature`.
5. Submit a pull request.

## License
Apache License Version 2.0


