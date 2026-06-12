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

class IteminCartForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    amountForm = forms.ChoiceField(
        label="数量",
        choices=[(i, i) for i in range(1, 101)],
        widget=forms.widgets.Select
    )

class LoginForm(forms.Form):
    """M01: ログインフォーム（入力の有無だけ検証。ID/PWの照合はビュー側で行う）"""

    user_id = forms.CharField(
        label="会員ID", max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="パスワード", max_length=256,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        user_id = cleaned.get("user_id")
        password = cleaned.get("password")

        if user_id and password:
            account = Account.objects.filter(user_id=user_id).first()
            if account is None or account.password != password:
                raise forms.ValidationError("会員IDまたはパスワードが正しくありません")
            self.account = account
        return cleaned
