from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from ordersapp.forms import OrderForm, OrderItemForm
from ordersapp.models import Order, OrderItem


class LoggedUserOnlyMixin:
    @method_decorator(user_passes_test(lambda user: user.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderList(LoggedUserOnlyMixin, ListView):
    model = Order

    def get_queryset(self):
        return self.request.user.orders.all()


class OrderCreate(LoggedUserOnlyMixin, CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        OrderFormSet = inlineformset_factory(Order, OrderItem,
                                             form=OrderItemForm, extra=3)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, self.request.FILES)
        else:
            context['form'].initial['user'] = self.request.user
            basket_items = self.request.user.basket.all()
            if basket_items and basket_items.count():
                OrderFormSet = inlineformset_factory(
                    Order, OrderItem, form=OrderItemForm,
                    extra=basket_items.count() + 1
                )
                formset = OrderFormSet()
                for form, basket_item in zip(formset.forms, basket_items):
                    form.initial['product'] = basket_item.product
                    form.initial['qty'] = basket_item.qty
            else:
                formset = OrderFormSet()

        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.instance = self.object  # one to many
                orderitems.save()
                self.request.user.basket.all().delete()

        # delete empty order
        if self.object.total_cost == 0:
            self.object.delete()

        return order


class OrderUpdate(LoggedUserOnlyMixin, UpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(
            Order, OrderItem, form=OrderItemForm, extra=1
        )
        if self.request.POST:
            formset = OrderFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            formset = OrderFormSet(instance=self.object)
            for form in formset.forms:
                instance = form.instance
                if instance.pk:
                    form.initial['price'] = instance.product.price
        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)

            if orderitems.is_valid():
                orderitems.save()

        # delete empty order
        if self.object.total_cost == 0:
            self.object.delete()

        return order


# View an order in readonly

class OrderView(LoggedUserOnlyMixin, ListView):

    def get_queryset(self):
        self.order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return OrderItem.objects.filter(order=self.order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context


def purchase(request, order_pk):
    current_order = Order(order_pk)
    current_order.status = 'S'
    current_order.save(update_fields=['status'])
    return HttpResponseRedirect(reverse('ordersapp:view', kwargs={'pk': order_pk}))


class OrderDelete(LoggedUserOnlyMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('orders:index')


@receiver(pre_save, sender=OrderItem)
def product_quantity_update_save(sender, instance, **kwargs):
    if instance.pk:
        instance.product.quantity -= instance.qty - sender.get_item(instance.pk).qty
    else:
        instance.product.quantity -= instance.qty
    instance.product.save()


@receiver(pre_delete, sender=OrderItem)
def product_quantity_update_delete(sender, instance, **kwargs):
    print('orderitem delete')
    instance.product.quantity += instance.qty
    instance.product.save()


@receiver(pre_delete, sender=Order)
def product_quantity_update_delete(sender, instance, **kwargs):
    for item in instance.items.all():
        item.product.quantity += item.qty
        item.product.save()

