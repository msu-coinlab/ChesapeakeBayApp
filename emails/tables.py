import django_tables2 as tables
from .models import EmailTemplate, EmailMassive , EmailInstant
from django.utils.html import format_html

    
class EmailTemplateTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='emails/partials/actions_email_template.html',
        orderable=False,
        exclude_from_export=True,
        verbose_name='Acciones'
    )


    class Meta:
        model = EmailTemplate 
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('title', 'subject')
        order_by = ('title', 'subject')
        empty_text = 'No hay registros'
        attrs = {
            'class': 'table table-striped'
        }
        search_placeholder = 'Buscar...'


class EmailGroupTable(tables.Table):
    Opciones = tables.TemplateColumn(orderable=False, exclude_from_export=True, verbose_name="Acciones", template_code='''
<div class="d-flex justify-content-center">
    <a href="{% url 'update_email_group' record.slug %}" class="text-primary me-2">
        <span class="material-icons">edit</span>
    </a>
    <a href="{% url 'delete_email_group' record.slug %}" class="text-danger">
        <span class="material-icons">delete</span>
    </a>
</div>
''')

    class Meta:
        model = EmailTemplate 
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('title', )
        order_by = ('title', )
        empty_text = 'No hay registros'
        attrs = {
            'class': 'table table-striped'
        }
        search_placeholder = 'Buscar...'

class EmailMassiveTable(tables.Table):
    title = tables.Column(verbose_name='Título')
    from_user = tables.Column(verbose_name='De')
    email_template = tables.Column(verbose_name='Plantilla')
    send = tables.Column(verbose_name='Enviado')

    acciones = tables.TemplateColumn(template_code='''
        {% if record.send == False %}
            <div class="d-flex justify-content-center">
                <a href="{% url 'update_email_massive' record.slug %}" class="text-primary me-2">
                    <span class="material-icons">edit</span>
                </a>
                <a href="{% url 'dry_run_email_massive' record.slug %}" class="text-primary me-2">
                    <span class="material-icons">preview</span>
                </a>
                <a href="{% url 'delete_email_massive' record.slug %}" class="text-danger">
                    <span class="material-icons">delete</span>
                </a>
            </div>
        {% else %}
            <div class="d-flex justify-content-center">
                <a href="{% url 'disabled_update_email_massive' record.slug %}" class="text-primary me-2">
                    <span class="material-icons">visibility</span>
                </a>
                <a href="{% url 'delete_email_massive' record.slug %}" class="text-danger">
                    <span class="material-icons">delete</span>
                </a>
            </div>
        {% endif %}

    ''', orderable=False, verbose_name='Acciones')

    #Opciones = tables.TemplateColumn(orderable=False, template_code='<a href="/emails/update-email-template/{{record.slug}}/" class="btn btn-primary">Editar</a><a href="/emails/delete-email-template/{{record.slug}}" class="btn btn-danger" style="margin-left: 10px;">Delete</a>')

    class Meta:
        model = EmailMassive
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('title', 'from_user', 'email_template', 'send', 'acciones')
        order_by = ('send', 'from_user', 'email_template', 'title')
        empty_text = 'No hay registros'
        attrs = {
            'class': 'table table-striped'
        }
        search_placeholder = 'Buscar...'

class EmailInstantTable(tables.Table):
    subject = tables.Column(verbose_name='Asunto')

    acciones = tables.TemplateColumn(template_code='''
            <div class="d-flex justify-content-center">
                <a href="{% url 'disabled_update_email_instant' record.pk %}" class="text-primary me-2">
                    <span class="material-icons">visibility</span>
                </a>
                <a href="{% url 'delete_email_instant' record.pk %}" class="text-danger">
                    <span class="material-icons">delete</span>
                </a>
            </div>
    ''', orderable=False, verbose_name='Acciones')

    #Opciones = tables.TemplateColumn(orderable=False, template_code='<a href="/emails/update-email-template/{{record.slug}}/" class="btn btn-primary">Editar</a><a href="/emails/delete-email-template/{{record.slug}}" class="btn btn-danger" style="margin-left: 10px;">Delete</a>')

    class Meta:
        model = EmailInstant
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('subject', 'created_at', 'acciones')
        order_by = ('-send', 'subject')
        empty_text = 'No hay registros'
        attrs = {
            'class': 'table table-striped'
        }
        search_placeholder = 'Buscar...'
