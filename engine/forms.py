from django import forms
from .models import DOUGH_CHOICES, Pizza


class PizzaForm(forms.ModelForm):
    dough = forms.ChoiceField(label='Тесто', choices=DOUGH_CHOICES, widget=forms.RadioSelect, initial='0')

    class Meta:
        model = Pizza
        fields = ('dough',)

