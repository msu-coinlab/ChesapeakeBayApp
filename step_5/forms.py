
from django import forms
from core.models import Bmp, BmpCost, State


class BmpConstraintSelectionForm(forms.Form):
    bmp = forms.ModelChoiceField(queryset=None)  # Removed the direct queryset assignment
    unit = forms.CharField(max_length=20, required=False, disabled=True, initial="N/A")
    max_quantity = forms.DecimalField(max_digits=8, decimal_places=2, initial='')

    def __init__(self, *args, **kwargs):
        bmps = kwargs.pop('bmps', None)  # Extract bmps from kwargs
        super(BmpConstraintSelectionForm, self).__init__(*args, **kwargs)

        if bmps is not None:
            self.fields['bmp'].queryset = bmps

