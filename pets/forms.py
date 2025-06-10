from django import forms
from .models import ScheduledTask

class ScheduledTaskForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control form-control-lg border-secondary bg-white"
            }
        ),
        required=False
    )
    class Meta:
        model = ScheduledTask
        fields = '__all__'
