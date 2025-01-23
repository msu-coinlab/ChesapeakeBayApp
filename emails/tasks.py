from .models import Email, EmailGroup
#from sections.models import Section
#from members.models import Member
from time import sleep
from celery import shared_task
import subprocess
from django.core.files import File
import pytz
import json
import csv
from zipfile import ZipFile
import os
from os.path import basename
from django.utils import timezone
from django.shortcuts import render
from templated_mail.mail import BaseEmailMessage

from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model
import time
import subprocess
from datetime import datetime

from datetime import datetime

def zipit(directory, zip_filename, prefix='/results/'):
    file_paths = get_all_file_paths(directory)
    # writing files to a zipfile
    with ZipFile(zip_filename,'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file, prefix + basename(file))

# celery -A api4opt beat --loglevel=info
# celery -A api4opt worker --loglevel=info

# pipenv install django-templated-mail




@shared_task
def send_emails():
    results = Email.objects.filter(status='P')
    print(len(results))
    for result in results[:4]:
        try:
            reply_to = result.context.pop('reply_to', None)
            context = result.context
            message = BaseEmailMessage(
                template_name='emails/body.html',
                context=context,
            )
            #message.attach_file('static/images/dog.jpg')
            print(result.recipient)
            if reply_to:
                message.send(to=result.recipient, reply_to=[reply_to])
            else:
                message.send(to=result.recipient)

            result.context['reply_to'] = reply_to

            message.error = ''
            result.created_at = timezone.now()
            result.status = 'S'
            print('Message Sent')
        except Exception as e:
            result.error = e
            result.created_at = timezone.now()
            result.status = 'F'
            print('Message with Error')
        result.save()
        time.sleep(10)


def is_member_of_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    return user.groups.filter(pk=group.pk).exists()
@shared_task
def create_email_groups():
    section_group = {}
    #sections = Section.objects.filter()
    #for section in sections:
    #    slug = str(section.slug)
    #    section_group[slug] = []
    #members = Member.objects.all()
    #for member in members:
    #    user = get_user_model().objects.filter(id=member.user.id).first()
    #    section_group['miembros'] = section_group.get('miembros', []) + [user.id]
    #    # by section
    #    for mem_sec in member.sections.all():
    #        slug = str(mem_sec.slug)
    #        section_group[slug] = section_group.get(slug, []) + [user.id]

    #    groups = ['comision_membresia', 'comision_premio', 'consejo_directivo']
    #    for group in groups:
    #        if user.groups.filter(name=group).exists():
    #            section_group[group] = section_group.get(group, []) + [user.id]

    #    membership_types = ['regulares', 'adherentes', 'correspondientes']
    #    if member.membership == 'R':
    #        section_group['regulares'] = section_group.get('regulares', []) + [user.id]
    #    elif member.membership == 'adherentes':
    #        section_group['A'] = section_group.get('adherentes', []) + [user.id]
    #    elif member.membership == 'C':
    #        section_group['correspondientes'] = section_group.get('correspondientes', []) + [user.id]

    #for key, value in section_group.items():
    #    if EmailGroup.objects.filter(title=key).exists() and value!= []:
    #        email_group = EmailGroup.objects.filter(title=key).first()
    #        curr_users_list = []
    #        curr_users = email_group.users.all()
    #        for item in curr_users:
    #            curr_users_list.append(item.id)


    #        if sorted(curr_users_list) != sorted(value):
    #            email_group.users.set(value)
    #            email_group.save()
    #    elif value != [] :
    #        new_email_group = EmailGroup(title=key)
    #        new_email_group.save()
    #        #for element in value:
    #        #    new_email_group.users.add(element)
    #        new_email_group.users.set(value)
    #        new_email_group.save()


@shared_task
def create_certificate(name):
    # Load the template
    template_path = "template.html"
    with open(template_path, 'r') as file:
        template = file.read()

    # Replace placeholders
    date_today = datetime.now().strftime("%d de %B de %Y")
    personalized_html = template.replace("{name}", name).replace("{{date}}", date_today)

    # Save the personalized HTML to a new file
    output_html_path = f"{name}_certificate.html"
    with open(output_html_path, 'w') as file:
        file.write(personalized_html)

    # Convert to PDF using wkhtmltopdf
    output_pdf_path = f"{name}_certificate.pdf"
    subprocess.call(['wkhtmltopdf', output_html_path, output_pdf_path])
    print(f"Certificate created: {output_pdf_path}")


