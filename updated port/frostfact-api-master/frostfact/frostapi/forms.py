from django import forms
from .models import EventData


class EventDataForm(forms.ModelForm):
    event_date = forms.DateField(
        widget=forms.DateInput(format='%m-%d-%Y', attrs={'placeholder': 'MM/DD/YYYY'}),
        required=True
    )

    class Meta:
        model = EventData
        fields = '__all__'
