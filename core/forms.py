from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory
from .models import User, Caravan, CaravanImage, BlockedPeriod

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('user_type',)

class CaravanForm(forms.ModelForm):
    AMENITY_CHOICES = [
        ('Wi-Fi', 'Wi-Fi'),
        ('Shower', 'Shower'),
        ('Kitchen', 'Kitchen'),
        ('Heating', 'Heating'),
        ('Air Conditioning', 'Air Conditioning'),
        ('TV', 'TV'),
        ('Pet Friendly', 'Pet Friendly'),
    ]

    amenities = forms.MultipleChoiceField(
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Caravan
        fields = ['name', 'description', 'capacity', 'location', 'amenities']

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

CaravanImageFormSet = modelformset_factory(
    CaravanImage,
    form=CaravanImageForm,
    extra=3,  # Allow up to 3 extra forms for new images
    can_delete=True # Allow deleting existing images
)

class BlockedPeriodForm(forms.ModelForm):
    class Meta:
        model = BlockedPeriod
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

BlockedPeriodFormSet = modelformset_factory(
    BlockedPeriod,
    form=BlockedPeriodForm,
    extra=2, # Allow 2 extra forms for new blocked periods
    can_delete=True # Allow deleting existing blocked periods
)
