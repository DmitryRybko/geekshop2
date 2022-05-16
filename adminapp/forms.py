from django.contrib.auth import get_user_model
from django.forms import ModelForm, HiddenInput

from authapp.forms import ShopUserChangeForm
from mainapp.models import ProductCategory, Product


class AdminShopUserUpdateForm(ShopUserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'password',
                  'email', 'age', 'avatar',
                  'is_staff', 'is_superuser', 'is_active')


class AdminProductCategoryCreateForm(ModelForm):
    class Meta:
        model = ProductCategory
        fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field_name, field in self.fileds.items():
                field.widget.attrs['class'] = f'form-control {field_name}'


class AdminProductUpdateForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'category':
                field.widget = HiddenInput()
