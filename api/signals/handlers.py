from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

def say_hello(request):
    notify_customers.delay('Hello there')
    return render(request, 'hello.html', {'name': 'Gregorio'})

def say_hello2(request):
    try:
       message = BaseEmailMessage(
           template_name='emails/hello.html',
           context={'name': 'Toscano'}
       )
       message.attach_file('static/images/dog.jpg')
       message.send(['gtoscano@gmail.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'Gregorio'})
