from django import forms
from .models import FeeRequest
from .models import ACTIVITY_CHOICES, AGENCY_CHOICES

BOOTSTRAP_FORM_CONTROL_CLASS = 'form-control'
BOOTSTRAP_FORM_SELECT_CLASS = 'form-select'


class FeeRequestForm(forms.ModelForm):

    class Meta:
        model = FeeRequest
        exclude = ('driver', 'reasons', 'timestamp')

        widgets = {
            'activity': forms.Select(attrs={'class': BOOTSTRAP_FORM_SELECT_CLASS}, choices=ACTIVITY_CHOICES),
            'agency': forms.Select(attrs={'class': BOOTSTRAP_FORM_SELECT_CLASS}, choices=AGENCY_CHOICES),
            'date': forms.DateInput(attrs={'class': BOOTSTRAP_FORM_CONTROL_CLASS, 'type': 'date'})
        }


