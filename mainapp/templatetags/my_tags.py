from django import template
from django.conf import settings

register = template.Library()


def media_folder_products(string):
    """
    Автоматически добавляет относительный URL-путь к медиафайлам продуктов
    products_images/product1.jpg --> /media/products_images/product1.jpg
    """
    if not string:
        string = 'products_images/default.jpg'

    return f'{settings.MEDIA_URL}{string}'


@register.filter(name='media_folder_users')
def media_folder_users(string):

    if not string:
        string = 'avatars/default.jpg'

    return f'{settings.MEDIA_URL}{string}'


register.filter('media_folder_products', media_folder_products)
