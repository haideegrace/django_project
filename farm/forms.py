from django import forms
from django.utils import timezone
from .models import ActivityLog, Employee, Animal

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'employee', 'animal', 'date', 'time', 'notes', 'photo']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date and time
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
            self.fields['time'].initial = timezone.now().time()

        # Make photo field more prominent
        self.fields['photo'].widget.attrs.update({
            'accept': 'image/*',
            'capture': 'environment'
        })
        self.fields['photo'].help_text = 'Upload a photo as proof of this activity'