from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.http import Http404
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from django_tables2 import SingleTableView, SingleTableMixin

from django_filters.views import FilterView
from .models import Email, EmailGroup, EmailMassive, EmailTemplate, EmailInstant
from .forms import EmailMassiveForm, EmailInstantForm, EmailInstantForm
from cast import settings
from datetime import datetime
from .tasks import send_emails
from .tasks import create_email_groups
from .tables import EmailTemplateTable, EmailMassiveTable, EmailGroupTable, EmailInstantTable
from .filters import EmailTemplateFilter, EmailMassiveFilter, EmailGroupFilter, EmailInstantFilter


from django.contrib.auth import get_user_model

#def create_email_groups():
class CreateEmailGroups(UserPassesTestMixin, ListView):
    template_name = 'emails/groups_updated.html'
    queryset = EmailGroup.objects.filter()
    context_object_name = 'objects'
    paginate_by = 30

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        ctx = super(CreateEmailGroups, self).get_context_data(**kwargs)
        create_email_groups()
        return ctx

class ListEmailGroups(UserPassesTestMixin, SingleTableMixin, FilterView):
    model = EmailGroup
    table_class = EmailGroupTable
    #template_name = 'emails/list_email_groups.html'
    template_name = 'emails/list_table_generic.html'
    #queryset = EmailGroup.objects.filter()
    filterset_class = EmailGroupFilter
    context_object_name = 'objects'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filterset_class(self.request.GET, queryset=queryset).qs

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()


    def get_context_data(self, **kwargs):
        ctx = super(ListEmailGroups, self).get_context_data(**kwargs)
        ctx['create_title'] = 'Agregar Grupo de Correos'
        ctx['title'] = 'Listado de Grupos de Correos'
        ctx['create_url'] = reverse('create_email_group')
        return ctx

class CreateEmailGroup(UserPassesTestMixin, CreateView):
    model = EmailGroup
    fields = ['title', 'users']
    template_name = 'emails/create_generic.html'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_success_url(self):
        return reverse('list_email_groups')

    def get_context_data(self, **kwargs):
        ctx = super(CreateEmailGroup, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Agregar'
        ctx['title'] = 'Agregar Grupo de Correo'
        return ctx


class UpdateEmailGroup(UserPassesTestMixin, UpdateView):
    model = EmailGroup
    fields = ['title', 'users']

    template_name = 'emails/update_generic.html'
    context_object_name = 'object'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_success_url(self):
        return reverse('list_email_groups')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateEmailGroup, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Actualizar'
        ctx['page_title'] = 'Actualizar Grupo de Correo'
        return ctx


class DeleteEmailGroup(UserPassesTestMixin, DeleteView):
    template_name = 'emails/delete_generic.html'
    model = EmailGroup
    success_url = reverse_lazy('list_email_groups')
    success_message = 'Borrado exitosamente'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        ctx = super(DeleteEmailGroup, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Borrar'
        ctx['page_title'] = 'Borrar Grupo de Correo'
        return ctx

class EmailGroupView(UserPassesTestMixin, DetailView):
    template_name = 'emails/email_group.html'
    model = EmailGroup
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        kwargs['users'] = self.get_object().users.all()
        return super(EmailGroupView, self).get_context_data(**kwargs)

    def get_object(self):
        obj = super(EmailGroupView, self).get_object()
        return obj

class ListEmailTemplates(UserPassesTestMixin, SingleTableMixin, FilterView):
    model = EmailTemplate
    table_class = EmailTemplateTable
    template_name = 'emails/list_table_generic.html'
    filterset_class = EmailTemplateFilter
    context_object_name = 'objects'
    paginate_by = 30  

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filterset_class(self.request.GET, queryset=queryset).qs

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        ctx = super(ListEmailTemplates, self).get_context_data(**kwargs)
        ctx['create_title'] = 'Añadir Plantilla'
        ctx['title'] = 'Listado de Plantillas de Correos'
        ctx['create_url'] = reverse('create_email_template')

        return ctx

class CreateEmailTemplate(UserPassesTestMixin, CreateView):
    model = EmailTemplate
    fields = ['title', 'subject', 'message', 'attachment']
    template_name = 'emails/create_generic.html'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_success_url(self):
        # Redirects to the list of email templates after successful form submission
        return reverse_lazy('list_email_templates')

    def get_context_data(self, **kwargs):
        ctx = super(CreateEmailTemplate, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Agregar'
        ctx['title'] = 'Agregar Plantilla de Correo'
        return ctx

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        # Perform custom actions here, for example:
        # You can manipulate the instance before saving
        email_template = form.save(commit=False)
        # e.g., set the user who created the template
        email_template.created_by = self.request.user
        email_template.save()

        # Optionally, you can add a success message
        messages.success(self.request, "Plantilla de correo creada exitosamente")

        # Finally, redirect to the success URL
        return super(CreateEmailTemplate, self).form_valid(form)

class UpdateEmailTemplate(UserPassesTestMixin, UpdateView):
    model = EmailTemplate
    fields = ['title', 'subject', 'message', 'attachment']
    template_name = 'emails/update_generic.html'
    context_object_name = 'object'
    
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_success_url(self):
        return reverse('list_email_templates')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateEmailTemplate, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Actualizar'
        ctx['page_title'] = 'Actualizar Plantilla de Correo'
        return ctx


class DeleteEmailTemplate(UserPassesTestMixin, DeleteView):
    template_name = 'emails/delete_generic.html'
    model = EmailTemplate
    success_url = reverse_lazy('list_email_templates')
    success_message = 'Borrado exitosamente'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        ctx = super(DeleteEmailTemplate, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Borrar Plantilla'
        ctx['page_title'] = 'Borrar Plantilla de Correo'
        return ctx

class EmailTemplateView(UserPassesTestMixin, DetailView):
    template_name = 'emails/email_template.html'
    model = EmailTemplate
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_object(self):
        obj = super(EmailTemplateView, self).get_object()
        return obj


class ListEmailMassives(UserPassesTestMixin, SingleTableMixin, FilterView):
    model = EmailMassive
    table_class = EmailMassiveTable
    #template_name = 'emails/list_email_massive.html'
    template_name = 'emails/list_table_generic.html'
    filterset_class = EmailMassiveFilter
    #queryset = EmailMassive.objects.filter()
    context_object_name = 'objects'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filterset_class(self.request.GET, queryset=queryset).qs

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        ctx = super(ListEmailMassives, self).get_context_data(**kwargs)
        ctx['create_title'] = 'Crear Correo Masivo'
        ctx['title'] = 'Listado de Correos Masivos'
        ctx['create_url'] = reverse('create_email_massive')

        return ctx


class CreateEmailMassive(UserPassesTestMixin, CreateView):
    model = EmailMassive
    form_class = EmailMassiveForm
    template_name = 'emails/create_generic.html'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_success_url(self):
        return reverse('list_email_massives')

    def get_form_kwargs(self):
        kwargs = super(CreateEmailMassive, self).get_form_kwargs()
        kwargs.update({'disabled_fields':['send']})
        return kwargs
    def get_context_data(self, **kwargs):
        ctx = super(CreateEmailMassive, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Agregar'
        ctx['page_title'] = 'Agregar correo masivo'
        return ctx

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        return super().form_valid(form)



def create_emails(object):
    recipient = []
    recipient_cc = []
    if object.cc_users not in (None, '') and object.cc_users not in recipient_cc:
        recipient_cc.append(object.cc_users.email)

    if object.to_group not in (None, ''):
        email_group = EmailGroup.objects.get(pk=object.to_group.pk) or None
        for user in email_group.users.all():
            if user.email not in recipient:
                recipient.append(user.email)


    if object.to_users not in (None, '', []):
        for user in object.to_users.all():
            if user.email not in recipient:
                recipient.append(user.email)


    email_template = EmailTemplate.objects.get(pk=object.email_template.pk) or None
    emails = []
    for email_pk in recipient:
        user = get_user_model().objects.get(email=email_pk)
        gender = 'a' if user.gender == 'F' else 'o'
        short_name = user.get_short_name()
        full_name = user.get_full_name()
        technical_support_email='ayuda@amexcomp.mx'
        today = datetime.today().strftime('%Y-%m-%d')
        president = 'Dr. Carlos Coello'
        email = '{}'.format(user.email)

        body = email_template.message.format(oa_genero=gender, primer_nombre=short_name,
                                             nombre_completo=full_name, email=email,
                                             soporte_tecnico_email=technical_support_email,
                                             presidente=president, hoy=today
                                             )
        emails.append({'body':body, 'recipient':[email] + recipient_cc, 'subject':email_template.subject, 'full_name':full_name })
    return emails

class UpdateEmailMassive(UserPassesTestMixin, UpdateView):
    model = EmailMassive
    form_class = EmailMassiveForm
    template_name = 'emails/update_generic.html'
    context_object_name = 'object'
    '''
    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        obj = self.get_object()

        if obj.send == True :
            #return super(UpdateEmailMassive, self).dispatch(request, *args, **kwargs)
            print(request)
            print(args)
            print(kwargs)
            redirect(reverse_lazy('disabled_update_email_massive', args=args, kwargs=kwargs))
        else:
            return super(UpdateEmailMassive, self).dispatch(request, *args, **kwargs)
    '''
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_form_kwargs(self):
        kwargs = super(UpdateEmailMassive, self).get_form_kwargs()
        #kwargs.update({'disabled_fields':['title', 'to_users']})
        obj = self.get_object()
        if obj.send == True :
            kwargs.update({'disabled_fields':'__all__'})
        return kwargs

    def get_object(self):
        obj = super(UpdateEmailMassive, self).get_object()
        return obj

    def get_success_url(self):
        return reverse('list_email_massives')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateEmailMassive, self).get_context_data(**kwargs)
        if ctx['object'].send == False:
            ctx['button_name'] = 'Actualizar'
            ctx['page_title'] = 'Actualizar Correo Massivo'
        else:
            ctx['button_name'] = 'Cancel'
            ctx['page_title'] = 'View Email Massive'
        return ctx

    def form_valid(self, form):
        form.instance.from_user = self.request.user

        if form.instance.send == True and form.instance.sent == False:
            form.instance.sent = True

            emails = create_emails(form.instance)
            message = ''
            for my_email in emails:
                full_name = my_email['full_name']
                recipient = my_email['recipient']
                subject = my_email['subject']
                body = my_email['body']
                new_email = Email(recipient=recipient, context={'reply_to':self.request.user.email, 'body': body, 'subject':subject} )

                new_email.save()

        return super().form_valid(form)
        #https://stackoverflow.com/questions/32998300/django-createview-how-to-perform-action-upon-save
        #self.object = form.save()
        # do something with self.object
        # remember the import: from django.http import HttpResponseRedirect
        #return HttpResponseRedirect(self.get_success_url())

class DisabledUpdateEmailMassive(UpdateEmailMassive):

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        return super(DisabledUpdateEmailMassive, self).dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        ctx = super(DisabledUpdateEmailMassive, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Cancelar'
        ctx['page_title'] = 'Ver Email Masivo'
        return ctx

    def get_form_kwargs(self):
        kwargs = super(DisabledUpdateEmailMassive, self).get_form_kwargs()
        #kwargs.update({'disabled_fields':['title', 'to_users']})
        kwargs.update({'disabled_fields':'__all__'})
        return kwargs


class EmailMassiveView(UserPassesTestMixin, DetailView):
    template_name = 'emails/email_massive.html'
    model = EmailMassive
    context_object_name = 'object'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_object(self):
        obj = super(EmailMassiveView, self).get_object()
        return obj

    def get_context_data(self, **kwargs):
        kwargs['to_users'] = self.get_object().to_users.all()
        return super(EmailMassiveView, self).get_context_data(**kwargs)



class DryRunEmailMassive(UserPassesTestMixin, DetailView):
    template_name = 'emails/dry_run.html'
    model = EmailMassive
    context_object_name = 'object'

    '''
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
        '''
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        object = self.get_object()
        emails = create_emails(object)
        message = ''
        for my_email in emails:
            print (my_email)
            full_name = my_email['full_name']
            recipient = my_email['recipient']
            subject = my_email['subject']
            my_body = my_email['body']
            message += '<hr>A: {}&lt;{}&gt;<br>ASUNTO: {}<br>{}'.format(full_name, recipient, subject, my_body)
        kwargs['subject'] = 'hola'
        kwargs['message'] = message
        #kwargs['subject'] = email_template.subject
        return super(DryRunEmailMassive, self).get_context_data(**kwargs)

class DeleteEmailMassive(UserPassesTestMixin, DeleteView):
    template_name = 'emails/delete_generic.html'
    model = EmailMassive
    success_url = reverse_lazy('list_email_massives')
    success_message = 'Borrado exitosamente'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        ctx = super(DeleteEmailMassive, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Borrar Correo Masivo'
        ctx['page_title'] = 'Confirmar Borrar'
        return ctx
    '''
    def get_queryset(self):
        qs = super(DeleteEmailMassive, self).get_queryset()
        return qs.filter(owner=self.request.user)
        '''


class ListEmailInstants(UserPassesTestMixin, SingleTableMixin, FilterView):
    model = EmailInstant
    table_class = EmailInstantTable
    #template_name = 'emails/list_email_instant.html'
    template_name = 'emails/list_table_generic.html'
    filterset_class = EmailInstantFilter
    #queryset = EmailInstant.objects.filter()
    context_object_name = 'objects'
    paginate_by = 30
    
    def get_queryset(self):
        # Get the initial queryset from the base class, already filtered by the filterset_class
        queryset = super().get_queryset()
        filtered_queryset = self.filterset_class(self.request.GET, queryset=queryset).qs

        # Further filter the queryset to only include items where from_user is the current user
        return filtered_queryset.filter(from_user=self.request.user)

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='email').exists()

    def get_context_data(self, **kwargs):
        ctx = super(ListEmailInstants, self).get_context_data(**kwargs)
        ctx['create_title'] = 'Crear Correo'
        ctx['title'] = 'Listado de Correos'
        ctx['create_url'] = reverse('create_email_instant')

        return ctx


class CreateEmailInstant(UserPassesTestMixin, CreateView):
    model = EmailInstant
    form_class = EmailInstantForm
    template_name = 'emails/create_generic.html'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='email').exists()
    '''
    def get_form_kwargs(self):
        kwargs = super(CreateEmailInstant, self).get_form_kwargs()
        kwargs.update({'disabled_fields':['send']})
        return kwargs
    '''
    def get_success_url(self):
        return reverse('list_email_instants')

    def get_context_data(self, **kwargs):
        ctx = super(CreateEmailInstant, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Enviar'
        ctx['page_title'] = 'Nuevo correo'
        return ctx

    def form_valid(self, form):
        instance = form.save(commit=False)
        
        # Set any additional fields on the instance as needed
        instance.from_user = self.request.user
        
        # Now save the instance to the database
        instance.save()
        
        # After saving the instance, Django allows you to work with M2M relationships.
        # This is where you'd normally handle form.save_m2m() if you had M2M data submitted via the form.
        # For custom handling or if you need to ensure M2M relations are set up here, do it before proceeding.
        form.save_m2m()
        #form.instance.from_user = self.request.user

        emails = create_emails_instant(instance)

        message = ''
        for my_email in emails:
            print('my_email',my_email)
            full_name = my_email['full_name']
            recipient = my_email['recipient']
            subject = my_email['subject']
            body = my_email['body']
            new_email = Email(recipient=recipient, context={'reply_to':self.request.user.email, 'body': body, 'subject':subject} )
            new_email.save()
        return super().form_valid(form)



class UpdateEmailInstant(UserPassesTestMixin, UpdateView):
    model = EmailInstant
    form_class = EmailInstantForm
    template_name = 'emails/update_generic.html'
    context_object_name = 'object'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='email').exists()
    def get_form_kwargs(self):
        kwargs = super(UpdateEmailInstant, self).get_form_kwargs()
        #kwargs.update({'disabled_fields':['title', 'to_users']})
        obj = self.get_object()
        if obj.send == True :
            kwargs.update({'disabled_fields':'__all__'})
        return kwargs

    def get_object(self):
        obj = super(UpdateEmailInstant, self).get_object()
        return obj

    def get_success_url(self):
        return reverse('list_email_instants')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateEmailInstant, self).get_context_data(**kwargs)
        if ctx['object'].send == False:
            ctx['button_name'] = 'Actualizar'
            ctx['page_title'] = 'Actualizar Correo'
        else:
            ctx['button_name'] = 'Cancel'
            ctx['page_title'] = 'Ver Correo'
        return ctx

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        if form.instance.send == True and form.instance.sent == False:
            form.instance.sent = True

            emails = create_emails_instant(form.instance)
            message = ''
            for my_email in emails:
                full_name = my_email['full_name']
                recipient = my_email['recipient']
                subject = my_email['subject']
                body = my_email['body']
                new_email = Email(recipient=recipient, context={'reply_to':self.request.user.email, 'body': body, 'subject':subject} )
                new_email.save()

        return super().form_valid(form)
        #https://stackoverflow.com/questions/32998300/django-createview-how-to-perform-action-upon-save
        #self.object = form.save()
        # do something with self.object
        # remember the import: from django.http import HttpResponseRedirect
        #return HttpResponseRedirect(self.get_success_url())

class DisabledUpdateEmailInstant(UpdateEmailInstant):
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='email').exists()

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        return super(DisabledUpdateEmailInstant, self).dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        ctx = super(DisabledUpdateEmailInstant, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Cancelar'
        ctx['page_title'] = 'Ver Correo'
        return ctx

    def get_form_kwargs(self):
        kwargs = super(DisabledUpdateEmailInstant, self).get_form_kwargs()
        #kwargs.update({'disabled_fields':['title', 'to_users']})
        kwargs.update({'disabled_fields':'__all__'})
        return kwargs


class EmailInstantView(UserPassesTestMixin, DetailView):
    template_name = 'emails/email_instant.html'
    model = EmailInstant
    context_object_name = 'object'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='email').exists()

    def get_object(self):
        obj = super(EmailInstantView, self).get_object()
        return obj

    def get_context_data(self, **kwargs):
        kwargs['to_users'] = self.get_object().to_users.all()
        return super(EmailInstantView, self).get_context_data(**kwargs)


class DryRunEmailInstant(UserPassesTestMixin, DetailView):
    template_name = 'emails/dry_run.html'
    model = EmailInstant
    context_object_name = 'object'

    '''
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
        '''
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()

    def get_context_data(self, **kwargs):
        object = self.get_object()
        emails = create_emails_instant(object)
        message = ''
        for my_email in emails:
            print (my_email)
            full_name = my_email['full_name']
            recipient = my_email['recipient']
            subject = my_email['subject']
            my_body = my_email['body']
            message += '<hr>A: {}&lt;{}&gt;<br>ASUNTO: {}<br>{}'.format(full_name, recipient, subject, my_body)
        kwargs['subject'] = 'hola'
        kwargs['message'] = message
        #kwargs['subject'] = email_template.subject
        return super(DryRunEmailInstant, self).get_context_data(**kwargs)

class DeleteEmailInstant(UserPassesTestMixin, DeleteView):
    template_name = 'emails/delete_generic.html'
    model = EmailInstant
    success_url = reverse_lazy('list_email_instant')
    success_message = 'Borrado exitosamente'
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        ctx = super(DeleteEmailInstant, self).get_context_data(**kwargs)
        ctx['button_name'] = 'Borrar Correo'
        ctx['page_title'] = 'Confirmar Borrar'
        return ctx
    '''
    def get_queryset(self):
        qs = super(DeleteEmailInstant, self).get_queryset()
        return qs.filter(owner=self.request.user)
        '''

def create_emails_instant(object):
    recipient = []
    recipient_cc = []
    if object.cc_users not in (None, '') and object.cc_users not in recipient_cc:
        recipient_cc.append(object.cc_users.email)

    if object.to_group not in (None, ''):
        email_group = EmailGroup.objects.get(pk=object.to_group.pk) or None
        for user in email_group.users.all():
            if user.email not in recipient:
                recipient.append(user.email)


    if object.to_users not in (None, '', []):
        for user in object.to_users.all():
            if user.email not in recipient:
                recipient.append(user.email)


    emails = []
    for email_pk in recipient:
        user = get_user_model().objects.get(email=email_pk)
        gender = 'a' if user.gender == 'F' else 'o'
        short_name = user.get_short_name()
        full_name = user.get_full_name()
        technical_support_email='ayuda@amexcomp.mx'
        today = datetime.today().strftime('%Y-%m-%d')
        president = 'Dr. Eduardo Morales'
        email = '{}'.format(user.email)

        body = object.message.format(oa_genero=gender, primer_nombre=short_name,
                                             nombre_completo=full_name, email=email,
                                             soporte_tecnico_email=technical_support_email,
                                             presidente=president, hoy=today
                                             )
        emails.append({'body':body, 'recipient':[email] + recipient_cc, 'subject':object.subject, 'full_name':full_name})
    return emails

