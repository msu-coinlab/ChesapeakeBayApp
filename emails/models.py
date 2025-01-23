from django.db import models
from django.utils import timezone as django_tz
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify
from cast import settings
from .validators import validate_file_size, validate_file_extension
from django_ckeditor_5.fields import CKEditor5Field

class EmailTemplate(models.Model):
    title = models.CharField(unique=True, max_length=255, verbose_name='Title')
    subject = models.CharField(max_length=255, verbose_name='Subject')
    message = CKEditor5Field(verbose_name='Messaje', blank=True)
    attachment = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True, validators=[validate_file_size, validate_file_extension])
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['-title']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.title)
            self.slug = slug[:50]


        return super(EmailTemplate, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('email_template', args=[self.slug])


class EmailGroup(models.Model):
    title = models.CharField(unique=True, max_length=255, verbose_name='Title')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='email_group_users', verbose_name='Users')
    slug = models.SlugField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Email Group'
        verbose_name_plural = 'Email Groups'
        ordering = ['-title']

    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.title)
            self.slug = slug[:50]
        return super(EmailGroup, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('email_group',
                       args=[self.slug])

class EmailMassive(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')
    slug = models.SlugField()
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='from_users', verbose_name='From')
    to_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='to_users', verbose_name='to')
    to_group = models.ForeignKey(EmailGroup, on_delete=models.CASCADE, blank=True, null=True, related_name='to_groups', verbose_name='To groups')
    cc_users = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='cc_users', verbose_name='CC')
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, verbose_name='Template')
    created_at = models.DateTimeField(blank=True, null=True)
    send = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Massive Email'
        verbose_name_plural = 'Massive Emails'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.title)
            self.slug = slug[:50]
        return super(EmailMassive, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('email_massive', args=[self.slug])


class EmailInstant(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='from_instant_users', verbose_name='From', blank=True, null=True)
    to_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='to_users_instant', verbose_name='For')
    to_group = models.ForeignKey(EmailGroup, on_delete=models.CASCADE, blank=True, null=True, related_name='to_groups_instant', verbose_name='To group')
    cc_users = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='cc_users_instant', verbose_name='CC')
    subject = models.CharField(max_length=255, verbose_name='Subject')
    message = CKEditor5Field(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True )
    send = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Instant Email'
        verbose_name_plural = 'Instant Emails'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('email_instant', args=[self.id])

class Email(models.Model):
    STATUS_PENDING = 'P'
    STATUS_SENT = 'S'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed')
    ]
    recipient = models.JSONField(default=list, null=False)
    context = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        ordering = ['-created_at']
    def __str__(self):
        return str(self.created_at)

