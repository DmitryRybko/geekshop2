from django.urls import path
import ordersapp.views as ordersapp


app_name = 'ordersapp'

urlpatterns = [
    path('', ordersapp.OrderList.as_view(), name='index'),
    path('create/', ordersapp.OrderCreate.as_view(), name='create'),
    path('update/<int:pk>/', ordersapp.OrderUpdate.as_view(), name='update'),
    path('view/<int:pk>/', ordersapp.OrderView.as_view(), name='view'),
    path('purchase/<int:order_pk>/', ordersapp.purchase, name='purchase'),
    path('delete/<int:pk>/', ordersapp.OrderDelete.as_view(), name='delete'),
]
