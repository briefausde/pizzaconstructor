"""pizzamaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from engine.views import *


ingredient_group_urls = [
    path('new/', IngredientGroupCreateView.as_view(), name='ingredient_group_create'),
    path('<int:pk>/edit/', IngredientGroupEditView.as_view(), name='ingredient_group_update'),
    path('<int:pk>/delete/', IngredientGroupDeleteView.as_view(), name='ingredient_group_delete'),
    path('', IngredientGroupListView.as_view(), name='ingredient_group_list'),
]

ingredient_urls = [
    path('new/', IngredientCreateView.as_view(), name='ingredient_create'),
    path('<int:pk>/edit/', IngredientEditView.as_view(), name='ingredient_update'),
    path('<int:pk>/delete/', IngredientDeleteView.as_view(), name='ingredient_delete'),
    path('', IngredientListView.as_view(), name='ingredient_list'),
]

order_urls = [
    path('<str:id>', OrderView.as_view(), name='order_create'),
    path('<str:id>/confirm/<str:code>', OrderConfirmView.as_view(), name='order_confirm'),
    path('detail/<str:id>', OrderDetailView.as_view(), name='order_detail'),
    path('', OrderListView.as_view(), name='order_list'),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PizzaFormView.as_view(), name='main'),
    path('create/', AjaxCreatePizzaView.as_view(), name='pizza_create'),
    path('order/', include(order_urls)),
    path('group/', include(ingredient_group_urls)),
    path('ingredient/', include(ingredient_urls)),
]
