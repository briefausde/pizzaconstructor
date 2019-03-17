import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


DOUGH_CHOICES = [
   ('0', 'Тонкое'),
   ('1', 'Пышное')
]


class IngredientGroup(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    group = models.ForeignKey(IngredientGroup, on_delete=models.CASCADE)
    cost = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class PizzaIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

    @property
    def price(self):
        return self.ingredient.cost * self.amount


class Pizza(models.Model):
    dough = models.CharField(choices=DOUGH_CHOICES, max_length=1)
    ingredients = models.ManyToManyField(PizzaIngredient)

    def __str__(self):
        return "Pizza"


class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=14, null=True)
    name = models.CharField(max_length=64, null=True)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    is_confirm = models.BooleanField(default=False)
    is_created = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)

    @property
    def price(self):
        return sum([i.price for i in self.pizza.ingredients.all()])

    def __str__(self):
        return "{} order by {} created at {}".format("[Confirmed]" if self.is_confirm else "[Not Confirmed]",
                                                     self.email,
                                                     self.created_date.strftime('%B %d, %I:%M %p'))

