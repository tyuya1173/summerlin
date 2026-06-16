from django import forms
from .models import Account, Admin, Item

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

class RegisterForm(forms.Form):
    user_id = forms.CharField(label="会員ID", max_length=128)
    password = forms.CharField(label="パスワード", max_length=256)
    password_confirm = forms.CharField(label="パスワード(確認)", max_length=256)
    name = forms.CharField(label="お名前", max_length=128)
    address = forms.CharField(label="ご住所", max_length=256)

    def clean_user_id(self):
        user_id = self.cleaned_data["user_id"]
        if Account.objects.filter(user_id=user_id).exists():
            raise forms.ValidationError("この会員IDは既に使われています")
        return user_id

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        pw2 = cleaned.get("password_confirm")
        if pw and pw2 and pw != pw2:
            self.add_error("password_confirm", "パスワードが一致しません")
        return cleaned
    
class UpdateUserForm(forms.Form):
    password = forms.CharField(
        label="パスワード", max_length=256, required=False,
    )
    password_confirm = forms.CharField(
        label="パスワード(確認)", max_length=256, required=False,
    )
    name = forms.CharField(
        label="お名前", max_length=128,
    )
    address = forms.CharField(
        label="ご住所", max_length=256,
    )

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        pw2 = cleaned.get("password_confirm")
        if (pw or pw2) and pw != pw2:
            self.add_error("password_confirm", "パスワードが一致しません")
        return cleaned
    
class AdminLoginForm(forms.Form):

    admin_id = forms.CharField(
        label="管理者ID", max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="パスワード", max_length=256,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        admin_id = cleaned.get("admin_id")
        password = cleaned.get("password")

        if admin_id and password:
            admin = Admin.objects.filter(admin_id=admin_id).first()
            if admin is None or admin.password != password:
                raise forms.ValidationError("会員IDまたはパスワードが正しくありません")
            self.admin = admin
        return cleaned
    
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "manufacturer", "color", "price", "stock", "recommended", "category"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "recommended": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }