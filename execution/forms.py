

from django import forms
from django_select2 import forms as s2forms
from core.models import Execution 

class ExecutionForm(forms.ModelForm):
    class Meta:
        model = Execution 
        fields = ['scenario'] 


