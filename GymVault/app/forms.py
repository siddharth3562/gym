from django import forms
from django.core.exceptions import ValidationError  
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields from the model

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')

        # Validate flavor and subcategory for supplements
        if category == 'supplement':
            flavor = cleaned_data.get('flavor')
            subcategory = cleaned_data.get('subcategory')

            if not flavor:
                self.add_error('flavor', "Flavor is required for supplements.")
            if not subcategory:
                self.add_error('subcategory', "Subcategory is required for supplements.")

        # No need to validate material anymore for equipment
        return cleaned_data
