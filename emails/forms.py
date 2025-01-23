from django import forms

from .models import EmailMassive, EmailInstant
#https://stackoverflow.com/questions/55506000/syntax-for-disabling-all-form-fields-in-django
#https://www.reddit.com/r/django/comments/s8disn/how_to_create_detailview_looks_like_updateview/
class EmailMassiveForm(forms.ModelForm):
    class Meta:
        model = EmailMassive
        fields = ['title', 'to_users', 'to_group', 'cc_users', 'email_template', 'send']

    def __init__(self, disabled_fields= [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_users'].widget.attrs.update({'x-ref': 'toUsersSelect'})
        self.fields['to_group'].widget.attrs.update({'x-ref': 'toGroupSelect'})
        if isinstance(disabled_fields, str) and disabled_fields=='__all__':
            disabled_fields = list(self.fields)
        if isinstance(disabled_fields, list):
            for field in disabled_fields:
                if field in self.fields:
                    self.fields[field].disabled = True
        #self.fields['title'].disabled = True

class EmailInstantForm(forms.ModelForm):
    class Meta:
        model = EmailInstant
        fields = ['to_users', 'to_group', 'cc_users', 'subject', 'message']

    def __init__(self, disabled_fields= [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_users'].widget.attrs.update({'x-ref': 'toUsersSelect'})
        self.fields['to_group'].widget.attrs.update({'x-ref': 'toGroupSelect'})
        if isinstance(disabled_fields, str) and disabled_fields=='__all__':
            disabled_fields = list(self.fields)
        if isinstance(disabled_fields, list):
            for field in disabled_fields:
                if field in self.fields:
                    self.fields[field].disabled = True
        #self.fields['title'].disabled = True
