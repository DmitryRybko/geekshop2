from mainapp.models import ProductCategory


def categories(request):
    return {
        'categories': ProductCategory.objects.filter(is_active=True)
    }
