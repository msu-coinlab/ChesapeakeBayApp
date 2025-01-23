
import django_filters
from .models import EmailTemplate, EmailMassive, EmailGroup, EmailInstant
from django_filters.widgets import RangeWidget
from django.db.models import Q

class EmailTemplateFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    subject = django_filters.CharFilter(lookup_expr='icontains')

    #published_date = django_filters.DateRangeFilter()
    #published_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'type': 'date'}))
    class Meta:
        model = EmailTemplate 
        #fields = [ 'title', 'publication_type', 'published_date']
        fields = [ 'title', 'subject']

class EmailGroupFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = EmailGroup
        fields = [ 'title',]

class EmailMassiveFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    #published_date = django_filters.DateRangeFilter()
    #published_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'type': 'date'}))
    class Meta:
        model = EmailMassive
        #fields = [ 'title', 'publication_type', 'published_date']
        fields = ['title', 'from_user', 'email_template', 'send']


class EmailInstantFilter(django_filters.FilterSet):
    subject = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EmailInstant
        #fields = [ 'title', 'publication_type', 'published_date']
        fields = ['subject']
