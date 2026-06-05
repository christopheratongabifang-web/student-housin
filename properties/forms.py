from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    amenities_text = forms.CharField(
        required=False,
        help_text="Enter amenities separated by commas (e.g. WiFi, Gym, Parking)",
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500'})
    )

    class Meta:
        model = Property
        fields = ['title', 'description', 'price_per_month', 'latitude', 'longitude', 'distance_to_campus']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500', 'rows': 4}),
            'price_per_month': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500', 'step': '0.000001'}),
            'distance_to_campus': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded focus:ring-indigo-500 focus:border-indigo-500', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.amenities:
            self.initial['amenities_text'] = ", ".join(self.instance.amenities)

    def save(self, commit=True):
        instance = super().save(commit=False)
        amenities_str = self.cleaned_data.get('amenities_text', '')
        if amenities_str:
            instance.amenities = [a.strip() for a in amenities_str.split(',') if a.strip()]
        else:
            instance.amenities = []
            
        if commit:
            instance.save()
        return instance
