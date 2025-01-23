
from django import forms
from django_select2 import forms as s2forms
from core.models import ScenarioInfo, Scenario
from core.models import ScenarioInfo, Scenario, BaseScenario, GeographicArea, State

class ScenarioInfoForm(forms.ModelForm):
    class Meta:
        model = ScenarioInfo
        fields = ['name', 'description', 'data_revision', 'condition', 'type_id', 'backout', 'point_src', 'atm_dep', 'climate_change', 'soil', 'base_load']

class MultipleHiddenInput(forms.HiddenInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def value_from_datadict(self, data, files, name):
        return data.getlist(name)  # This handles multiple values

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, {'type': 'hidden', 'name': name})
        id_ = final_attrs.get('id')
        # Render multiple hidden inputs for each value
        if isinstance(value, (list, tuple)):
            return '\n'.join([forms.HiddenInput().render(name, v, {'id': f'{id_}_{i}'}) for i, v in enumerate(value)])
        else:
            return super().render(name, value, attrs, renderer)

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', 'scenario_info', 'geographic_areas']
        widgets = {
            'scenario_info': forms.Select(attrs={'class': 'select2'}),
            #'geographic_areas': forms.SelectMultiple(attrs={'class': 'select2'}),
            #'geographic_areas': forms.HiddenInput(),
            'geographic_areas': MultipleHiddenInput(),
        }

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)

class ScenarioShareForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['shared_with']
        widgets = {
            'shared_with': forms.SelectMultiple(attrs={'size': 10}),
        }
