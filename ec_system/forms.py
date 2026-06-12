from django import forms
from .models import Category, Account

class ItemSearchForm(forms.Form):

    category = forms.ChoiceField(
        label="カテゴリ",
        required=False
    )

    keyword = forms.CharField(
        label="キーワード",
        required=False,
        max_length=128,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("all", "すべて")]
        choices += [(str(c.category_id), c.name) for c in Category.objects.all()]
        self.fields["category"].choices = choices