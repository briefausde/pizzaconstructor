from django.contrib import admin
from .models import *


admin.site.register(IngredientGroup)
admin.site.register(Ingredient)
admin.site.register(Pizza)
admin.site.register(PizzaIngredient)
admin.site.register(Order)
