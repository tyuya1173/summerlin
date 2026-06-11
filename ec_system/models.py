from django.db import models

class Account(models.Model):

    class Meta:

        db_table = "account_user"

    user_id = models.CharField(verbose_name="会員ID", max_length=128, primary_key=True, db_index=True)
    password = models.CharField(verbose_name="パスワード", max_length=256, null=True)
    name = models.CharField(verbose_name="名前", null=True, max_length=128)
    address = models.CharField(verbose_name="住所", null=True, max_length=256)

class Category(models.Model):

    class Meta:

        db_table = "shopping_category"

    category_id = models.IntegerField(verbose_name="カテゴリID", primary_key=True, db_index=True)
    name = models.CharField(verbose_name="カテゴリ名", max_length=256, null=True)

class Item(models.Model):

    class Meta:

        db_table = "shopping_item"

    item_id = models.IntegerField(verbose_name="商品ID", primary_key=True, db_index=True)
    name = models.CharField(verbose_name="商品名", max_length=128, null=True)
    manufacturer = models.CharField(verbose_name="メーカー名", max_length=32, null=True)
    color = models.CharField(verbose_name="商品の色", max_length=16, null=True)
    price = models.IntegerField(verbose_name="価格", null=True)
    stock = models.IntegerField(verbose_name="在庫数", null=True)
    recommended = models.BooleanField(verbose_name="オススメ", max_length=1, null=True, default=False)
    category = models.ForeignKey(Category, verbose_name="カテゴリID",  on_delete=models.CASCADE, null=True)

class Itemincart(models.Model):

    class Meta:

        db_table = "shopping_itemsincart"

    amount = models.IntegerField(verbose_name="数量", null=True)
    booked_date = models.DateTimeField(verbose_name="登録日", null=True, auto_now_add=True)
    item = models.ForeignKey(Item, verbose_name="商品ID", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(Account, verbose_name="会員ID", null=True, on_delete=models.CASCADE)

class Purchase(models.Model):

    class Meta:

        db_table = "shopping_purchase"

    purchase_id = models.IntegerField(verbose_name="注文ID", primary_key=True, db_index=True)
    destination = models.CharField(verbose_name="配送先", max_length=256, null=True)
    booked_date = models.DateTimeField(verbose_name="注文日", null=True, auto_now_add=True)
    cancel = models.BooleanField(verbose_name="キャンセル", max_length=1, null=True, default=False)
    user = models.ForeignKey(Account, verbose_name="注文者", max_length=128, null=True, on_delete=models.CASCADE)

class Purchasedetail(models.Model):

    class Meta:

        db_table = "shopping_purchasedetail"

    purchase_detail_id = models.IntegerField(verbose_name="注文詳細ID", primary_key=True, db_index=True)
    amount = models.IntegerField(verbose_name="注文数", null=True)
    item = models.ForeignKey(Item, verbose_name="商品ID", on_delete=models.CASCADE, null=True)
    purchase = models.ForeignKey(Purchase, verbose_name="注文ID", on_delete=models.CASCADE, null=True)

class Admin(models.Model):

    class Meta:

        db_table = "administrator_admin"

    admin_id = models.CharField(verbose_name="管理者ID", primary_key=True, max_length=128, db_index=True)
    password = models.CharField(verbose_name="パスワード", null=True, max_length=256)