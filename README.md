# Viber bot in Django + LiqPay payment system (shop simplified example)

> Python 3.11.4. Dependencies in `requirements.txt`. [Viber API docs](https://developers.viber.com/docs/api/rest-bot-api/)

---

1. Django

   * [Install & settings](#install)
   * [Models & admin](#models--admin)
   * [Rest API](#rest-api-framework)

2. Viberbot

   * [Set hook](#sethook)
   * [Keyboard](#keyboard-example)
   * [Catalog](#catalog-creation)
   * [LiqPay](#liqpay)

---

## Install

```bash
pip install Django viberbot djangorestframework Pillow
```

Create project and app:

```bash
django-admin startproject project
cd project
py manage.py startapp viberbotapp
py manage.py runserver
```

`settings.py`:

```python
INSTALLED_APPS = [
  ...
  'rest_framework',
  'viberbotapp',
]
ALLOWED_HOSTS = ['*']

import os 
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Models & admin

`viberbotapp/models.py`

```python
class Seller(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='seller_images/')
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    weight = models.FloatField()
    image = models.ImageField(upload_to='product_images/')
    def __str__(self): return self.name
```

```bash
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
```

`viberbotapp/admin.py`

```python
from .models import Product, Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'weight', 'image')
```

`project/urls.py`

```python
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Screenshot:**

```
Screenshot_1.png
```

---

## Rest API framework

`project/urls.py`

```python
urlpatterns = [
    path('viber/', include('viberbotapp.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`viberbotapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/sellers/', views.Sellers.as_view(), name='sellers'),
    path('api/seller/<str:seller>', views.Products.as_view(), name='products'),
    path('', views.webhook, name='viber_webhook'),
]
```

`viberbotapp/views.py`

```python
from rest_framework import generics, serializers
from .models import Seller, Product

class SellerSerializer(serializers.ModelSerializer):
    class Meta: model = Seller; fields = '__all__'

class Sellers(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class ProductsSerializer(serializers.ModelSerializer):
    class Meta: model = Product; fields = '__all__'

class Products(generics.ListAPIView):
    serializer_class = ProductsSerializer
    def get_queryset(self):
        return Product.objects.filter(seller__name=self.kwargs['seller'])
```

**Screenshot:**

```
Screenshot_2.png
```

---

## Sethook

`sethook.py`

```python
import requests, json
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': 'YOUR_TOKEN'}
sen = dict(url='https://<ngrok-url>/viber/', event_types=['unsubscribed','conversation_started','message','delivered','subscribed'])
print(requests.post(hook, json.dumps(sen), headers=headers).json())
```

`views.py`

```python
from django.views.decorators.csrf import csrf_exempt
from viberbot.api.bot_configuration import BotConfiguration
from viberbot import Api
from django.http import HttpResponse

bot_configuration = BotConfiguration(
    name="Vault bot",
    avatar=None,
    auth_token='YOUR_TOKEN',
)
viber_api = Api(bot_configuration)

@csrf_exempt
def webhook(request):
    return HttpResponse(status=200)
```

**Screenshot:**

```
Screenshot_3.png
```

---

## Keyboard example

```python
import json
from viberbot.api.messages import TextMessage, KeyboardMessage, RichMediaMessage

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        viber = json.loads(request.body.decode('utf-8'))
        if viber['event'] == 'conversation_started':
            start_button(viber['user']['id'])
    return HttpResponse(status=200)

def start_button(viber_id):
    keyboard = KeyboardMessage(keyboard=start_build(), min_api_version=6)
    viber_api.send_messages(viber_id, [keyboard])

def start_build():
    return {
        "Type": "keyboard","InputFieldState":"hidden","Buttons":[{
            "Columns":6,"Rows":1,"BgColor":"#ae9ef4",
            "Text":"<font color='#e5e1ff'><b>start</b></font>",
            "TextSize":"large","TextVAlign":"middle","TextHAlign":"center",
            "ActionBody":'start',"Silent":True
        }]}
```

**Screenshot:**

```
Screenshot_4.png
```

---

## Catalog creation

```python
@csrf_exempt
def webhook(request):
    if request.method == "POST":
        viber = json.loads(request.body.decode('utf-8'))
        if viber['event'] == 'conversation_started':
            start_button(viber['user']['id'])
        if viber['event'] == 'message':
            message = viber['message']['text']
            sender_id = viber['sender']['id']
            if message == 'start':
                show_sellers(sender_id)
            elif message in sellers_list():
                products(message, sender_id)
    return HttpResponse(status=200)
```

**Screenshot:**

```
Screenshot_5.png
```

---

## Liqpay

```python
if message in product_list():
    pay(message, sender_id)

def product_list():
    return [p.name for p in Product.objects.all()]
```

Install:

```bash
pip install git+https://github.com/liqpay/sdk-python
```

```python
import random,string,datetime,requests
from liqpay import LiqPay

def order_number():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(100,999))

def pay(message, sender_id):
    liqpay = LiqPay(PUBLIC_KEY, PRIVATE_KEY)
    params = {
        "action":"pay","version":"3",
        "amount": int(Product.objects.get(name=message).price),
        "currency":"UAH","order_id":order_number(),
        'description':"test"
    }
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    response = requests.post("https://www.liqpay.ua/api/3/checkout", data={'signature':signature,'data':data})
    if response.status_code==200:
        keyboard = KeyboardMessage(keyboard={
            "Type":"keyboard","InputFieldState":"hidden","Buttons":[{
                "Columns":6,"Rows":1,"BgColor":"#ae9ef4",
                "Text":"<font color='#e5e1ff'><b>pay</b></font>",
                "TextSize":"large","TextVAlign":"middle","TextHAlign":"center",
                "ActionType":"open-url","ActionBody":response.url,"Silent":True
            }]},min_api_version=6)
        viber_api.send_messages(sender_id,[keyboard])
```

**Screenshot:**

```
Screenshot_6.png
```

---

✅ Done. Now the README includes screenshots again (as placeholders like `Screenshot_X.png`) in the same style, fully English.
