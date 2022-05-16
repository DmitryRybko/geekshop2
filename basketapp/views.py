
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from basketapp.models import BasketItem
from geekshop.settings import LOGIN_URL
from mainapp.views import Product


@login_required
def index(request):
    basket = request.user.basket_items
    context = {
        'page_title': 'Basket',
        'basket': basket,
    }
    return render(request, 'basketapp/index.html', context)


@login_required
def add(request, product_pk):

    if LOGIN_URL in request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(
            reverse(
                'main:product_page',
                kwargs={'pk': product_pk}
            )
        )

    basket_item, _ = BasketItem.objects.get_or_create(
        user=request.user,
        product_id=product_pk,
    )

    added_product = Product.objects.get(pk=basket_item.product_id)
    max_product_qty = added_product.quantity
    if max_product_qty > basket_item.qty:
        basket_item.qty = F('qty')+1
        basket_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove(request, basket_item_pk):
    item = get_object_or_404(BasketItem, pk=basket_item_pk)
    item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def update(request, basket_item_pk, qty):
    if request.is_ajax():
        item = BasketItem.objects.filter(pk=basket_item_pk).first()
        if not item:
            return JsonResponse({
                'status': False,
            })
        if qty == 0:
            item.delete()
        else:
            item.qty = qty
            item.save()
        basket_summary_html = render_to_string('basketapp/includes/basket_summary.html',
                                               request=request)
        return JsonResponse({
            'status': True,
            'basket_summary': basket_summary_html,
            'qty': qty,
        })

