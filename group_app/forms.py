from django.forms import ModelForm, TextInput
from .models import City, Zip


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ["city"]
        widgets = {'city':TextInput(attrs={'class':'input', 'placeholder':'City Name'})}

class ZipForm(ModelForm):
    class Meta:
        model = Zip
        fields = ['zipcode']
        widgets = {"zipcode":TextInput(attrs={"class":'input', 'placeholder':"Zipcode"})}

    # def clean_zipcode(self):
    #     zipcode = cleaned_data.get("zipcode")
    #     if len(zipcode) > 5:
    #         raise 