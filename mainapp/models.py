from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(verbose_name='название', max_length=64, unique=True)
    description = models.TextField(verbose_name='описание', blank=True)
    is_active = models.BooleanField('active', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(using=using)


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='наименование', max_length=128)
    image = models.ImageField(upload_to='products_images', blank=True)
    short_desc = models.CharField(verbose_name='краткое описание', max_length=60, blank=True)
    price = models.DecimalField(verbose_name='цена продукта', max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(verbose_name='доступное количество', default=0)
    is_active = models.BooleanField('active', default=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @classmethod
    def get_items(cls):
        return cls.objects.select_related('category').filter(is_active=True, category__is_active=True)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['name']
