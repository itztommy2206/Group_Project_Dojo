from django.forms import ModelForm, TextInput
from .models import City


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ["city"]
        widgets = {'city':TextInput(attrs={'class':'input', 'placeholder':'City Name'})}
