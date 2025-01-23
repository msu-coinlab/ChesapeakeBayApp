
from django import forms
from core.models import Bmp, BmpCost, State


class BmpCostSelectionForm(forms.Form):
    bmp = forms.ModelChoiceField(queryset=None, initial=None)  # Removed the direct queryset assignment
    state = forms.ModelChoiceField(queryset=None, initial=None)  # Removed the direct queryset assignment
    cost = forms.DecimalField(max_digits=8, decimal_places=2, required=False, disabled=True, initial=0.00)
    unit = forms.CharField(max_length=20, required=False, disabled=True, initial="N/A")
    new_cost = forms.DecimalField(max_digits=8, decimal_places=2)

    def __init__(self, *args, **kwargs):
        bmps = kwargs.pop('bmps', None)  # Extract bmps from kwargs
        states = kwargs.pop('states', None)  # Extract states from kwargs
        super(BmpCostSelectionForm, self).__init__(*args, **kwargs)

        if bmps is not None:
            self.fields['bmp'].queryset = bmps
        if states is not None:
            self.fields['state'].queryset = states


class BmpCostForm(forms.ModelForm):
    class Meta:
        model = BmpCost
        fields = ['bmp', 'cost', 'unit', 'state']

