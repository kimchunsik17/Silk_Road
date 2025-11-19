from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CaravanImage

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('user_type',)

class ReservationForm(forms.Form):
    user_id = forms.IntegerField()
    caravan_id = forms.IntegerField()
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data

class CaravanImageForm(forms.ModelForm):
    class Meta:
        model = CaravanImage
        fields = ['image', 'description']
