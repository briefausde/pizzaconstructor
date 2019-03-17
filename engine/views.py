import json
from uuid import UUID

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import *

from .forms import *
from .models import *
from .utils import generate_confirm_code


class UUIDValidatorMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            UUID(self.kwargs['id']).version
        except ValueError:
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)


# Pizza views

class PizzaFormView(FormView):
    model = Pizza
    template_name = 'engine/pizza_form.html'
    form_class = PizzaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        ingredients = {}
        for group in IngredientGroup.objects.all():
            ingredients[group.name] = [(i.pk, i.name, i.cost) for i in Ingredient.objects.filter(group=group)]

        context['ingredients'] = json.dumps(ingredients)
        return context


class AjaxCreatePizzaView(View):
    def post(self, *args, **kwargs):
        try:
            pizza = Pizza.objects.create(dough=self.request.POST.get('dough', 0))

            for i in Ingredient.objects.all():
                amount = self.request.POST.get(i.name, 0)
                if amount and int(amount) > 0:
                    pizza_ingredient = PizzaIngredient.objects.create(ingredient=i, amount=amount)
                    pizza.ingredients.add(pizza_ingredient)

            order = Order.objects.create(pizza=pizza)
            url = reverse('order_create', args=(str(order.id),))
            return HttpResponse(json.dumps(url), content_type="application/json")

        except ValueError:
            return HttpResponseBadRequest()


# Order views

class OrderView(UUIDValidatorMixin, UpdateView):
    model = Order
    template_name = 'engine/order.html'
    context_object_name = 'order'
    fields = ['email', 'phone', 'name']

    def form_valid(self, form):
        self.object = form.save()
        order = self.object
        order.is_created = True
        order.save()

        message = render_to_string('engine/email_order_confirm_message.html', {
            'order': order,
            'domain': get_current_site(self.request),
            'confirm_code': generate_confirm_code(order),
        })

        send_mail('Confirm order', message, 'admin', [order.email])

        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('order_create', args=(self.object.id,))


class OrderConfirmView(View):
    model = Order

    def get(self, *args, **kwargs):
        order = get_object_or_404(self.model, id=self.kwargs['id'])

        if not order.is_confirm:
            if generate_confirm_code(order) == self.kwargs['code']:
                order.is_confirm = True
                order.confirmed_date = timezone.now()
                order.save()
                return HttpResponseRedirect(reverse('order_create', args=(order.id,)))

        return HttpResponse('Invalid token!')


class OrderListView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'engine/order_list.html'

    def get_queryset(self):
        return Order.objects.exclude(is_created=False).order_by('-created_date').all()


class OrderDetailView(UUIDValidatorMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'engine/order_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs['id'])


# IngredientGroup views

class IngredientGroupListView(ListView):
    model = IngredientGroup
    context_object_name = 'groups'
    template_name = 'engine/ingredient_group_list.html'


class IngredientGroupCreateView(CreateView):
    model = IngredientGroup
    template_name = 'engine/default_form.html'
    fields = ['name']

    def get_success_url(self):
        return reverse('ingredient_group_list')


class IngredientGroupEditView(UpdateView):
    model = IngredientGroup
    template_name = 'engine/default_form.html'
    fields = ['name']

    def get_success_url(self):
        return reverse('ingredient_group_list')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class IngredientGroupDeleteView(DeleteView):
    model = IngredientGroup
    template_name = 'engine/confirm_delete.html'

    def post(self, request, *args, **kwargs):
        obj = self.object
        if self.request.POST.get("confirm_delete"):
            obj.delete()
            return HttpResponseRedirect(reverse('ingredient_group_list'))
        return self.get(self, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


# Ingredient views

class IngredientListView(ListView):
    model = Ingredient
    context_object_name = 'ingredients'
    template_name = 'engine/ingredient_list.html'


class IngredientCreateView(CreateView):
    model = Ingredient
    template_name = 'engine/default_form.html'
    fields = ['name', 'group', 'cost']

    def get_success_url(self):
        return reverse('ingredient_list')


class IngredientEditView(UpdateView):
    model = Ingredient
    template_name = 'engine/default_form.html'
    fields = ['name', 'group', 'cost']

    def get_success_url(self):
        return reverse('ingredient_list')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class IngredientDeleteView(DeleteView):
    model = Ingredient
    template_name = 'engine/confirm_delete.html'

    def post(self, request, *args, **kwargs):
        obj = self.object
        if self.request.POST.get("confirm_delete"):
            obj.delete()
            return HttpResponseRedirect(reverse('ingredient_list'))
        return self.get(self, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])
