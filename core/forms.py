from django import forms
from django_select2 import forms as s2forms
from core.models import GeographicArea, BaseScenario
from .models import BmpCost
from .models import Bmp, State

class GeographicAreasWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
        "state__icontains",
    ]


class BmpCostSelectionForm(forms.Form):
    bmp = forms.ModelChoiceField(queryset=Bmp.objects.all(),
                                 )
    state = forms.ModelChoiceField(queryset=State.objects.all(),
                                   )
    cost = forms.DecimalField(max_digits=8, decimal_places=2, required=False, disabled=True, initial=0.00)
    unit = forms.CharField(max_length=20, required=False, disabled=True, initial="N/A")
    new_cost = forms.DecimalField(max_digits=8, decimal_places=2)
class BmpCostForm(forms.ModelForm):
    class Meta:
        model = BmpCost
        fields = ['bmp', 'cost', 'unit', 'state']

