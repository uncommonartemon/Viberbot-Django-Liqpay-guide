Viber bot in django + liqpay payment system. shop simplified example

> Python 3.11.4, other dependencies can be found in requireme. Full documentation for the bot- [viber api](https://developers.viber.com/docs/api/rest-bot-api/)
---

1.Django
  - [Install django & settings.py](#install)
  - [Models & admin setup](#models--admin)
  - [Rest api framework](#Rest-api-framework)

2.Viberbot
  - [Sethook](#sethook)
  - [Keyboard example](#Keyboard-example)
  - [Catalog creation](#Catalog-creation)
  - [Liqpay](#Liqpay)
  
## Install

Open the terminal in the project directory. Packages we need to install: django, viberbot, rest framework, Pillow
```
pip install Django
```
```
pip install viberbot
```
```
pip install djangorestframework
```
```
pip install Pillow
```
Next, create a django project, and create a bot application in the project as well.
Django project I will call 'project' and the application where the viber bot will be located will be called 'viberbotapp'.
```
django-admin startproject project
```
```
cd project
```
```
py manage.py startapp viberbotapp
```
All that's left is to get your server up and running
```
py manage.py runserver
```
After that, you should have something like this in the console:
```
You have 18 unapplied migration(s)...
...
Django version 4.2.5, using settings 'project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
When we follow the link, we should see this:
![Screenshot_1](https://github.com/uncommonartemon/viberbot/assets/51698182/190672c6-ece0-48f5-8838-e392381763d9)

Now, let's open the project/settings.py file, here we should add our application to the INSTALLED_APPS array, and add django rest framerwork. 

```python
INSTALLED_APPS = [
  ...
  'rest_framework',
  'viberbotapp',
  ...
]
```
Also change: 
```python
ALLOWED_HOSTS = ['*']
```
Next, we look for the variable STATIC_URL and next to it we add such variables :
```python
import os 
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```
## Models & admin
Now let's move on to model generation, in which we will define the structure of future created objects in our database. Open the file viberbotapp/models.py:
```python
class Seller(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='seller_images/')  
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    weight = models.FloatField()
    image = models.ImageField(upload_to='product_images/') 
    def __str__(self):
        return self.name
```
As you can see , we have created 2 models - seller and product, which will depend on the seller. Each class will create a separate table in the database for itself, and each variable will create a cell (in our case).
But luckily for us, we don't have to go into the database - django will do it for us. To do this, we will need to create a migration and execute it. In the terminal, disconnect the server, and enter the following commands:
```
py manage.py makemigrations
```
```
py manage.py migrate
```
And only after successful completion - django will make changes to the database structure.
So, we already have two empty tables waiting for us, and we will fill them through the admin panel. But first we need to register our models in the admin panel. Open viberbotapp/admin.py and add:
```python
from .models import Product, Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'weight', 'image')
```
This code adds a form to the admin interface for registering new items in the database, based on an already created model.
Before entering the admin panel, we need to do one last thing - create a superuser. Type in the terminal :
```
py manage.py createsuperuser
```
After your registration, start the server and go to "http://127.0.0.1:8000/admin/" or "http://localhost:8000/admin/". authorize.
If everything is done successfully, we will see something similar:
![Screenshot_2](https://github.com/uncommonartemon/Viberbot-Django-Liqpay/assets/51698182/cb4a7d14-0bca-4152-989f-764ff7ae16ef)

Next add sellers and products. For example, I will add two sellers, as well as 2 products for each seller. 

![Screenshot_3](https://github.com/uncommonartemon/Viberbot-Django-Liqpay/assets/51698182/03b5aba6-dfc1-4e86-b3f1-e7baf65b8543)

Done. on the product and seller page in the admin panel, we see a table like this :
⋅⋅⋅
![Screenshot_4](https://github.com/uncommonartemon/Viberbot-Django-Liqpay/assets/51698182/2356eecc-20ae-41b5-b275-55ea34acc973)

On the right side you will see links for the image. To make the links to the image available in the admin (and not only in the admin, but also in the future for rest requests) - open project/urls.py and modernize it a bit:
```python
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
Fine, keep urls.py open.

## Rest api framework

This is the last step before we leave django. That is, we need to create a RESTful api. In simple words, we will write a code with the help of which our customer (Viber client) will knock on the door of our server and ask for the information he needs, in our case it is information about products and sellers. Let's start by creating a door - add a new path to urls.py:
```python
urlpatterns = [
    path('viber/', include('viberbotapp.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
This means that the /viber request will be forwarded to ursl.py, which we will create now. Go to the directory of your viberbotapp application and create a new urls.py there.
Now let's fill him in, too:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/sellers/', views.Sellers.as_view(), name='sellers'),
]
```
In order to provide the user with information about sellers, his viber will request information on the link "host"/viber/api/sellers, and upon receiving this request, our server will launch the Sellers class, which is located in views.py. Actually, this is the door to our server. Now go to views.py and create classes:
```python
from rest_framework import generics, serializers
from .models import Seller, Product

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class Sellers(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
```
If everything is done correctly, then when you go to the address of the query in your browser (http://localhost:8000/viber/api/sellers/) you can see the result:
![Rest](https://github.com/uncommonartemon/viberbot/assets/51698182/d48b3f26-7240-4045-9a89-d2404194d274)

I'll also add a "door" for items, what we'll end up with is , views.py:
```python
from rest_framework import generics, serializers
from .models import Seller, Product

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class Sellers(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class Products(generics.ListAPIView):
    serializer_class = ProductsSerializer
    def get_queryset(self):
        seller_name = self.kwargs['seller'] 
        return Product.objects.filter(seller__name=seller_name)
```
urls.py:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/sellers/', views.Sellers.as_view(), name='sellers'),
    path('api/seller/<str:seller>', views.Products.as_view(), name='products'),
    path('',views.webhook, name='viber_webhook'),
]
```
I also created a webhook to communicate with viber, this will be our mediator between the user and the server. 

## Sethook
---
I just mentioned webhook, so now we will create a sethook.py that will send a signal to our path('',views.webhook, name='viber_webhook') if the status of the signal is 0 (successful), the bot will turn on. 
> If you haven't registered your bot yet, go to https://partners.viber.com/.

Create a sethook.py file in the root of the django directory , alongside manage.py
sethook.py:
```python
import requests
import json
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': 'YOUR_TOKEN' }
sen = dict(url='https://7499-188-163-102-40.ngrok-free.app/viber/',
           event_types = ['unsubscribed', 'conversation_started', 'message', 'delivered', 'subscribed'])
r = requests.post(hook, json.dumps(sen), headers=headers)
print(r.json())
```
>Replace 'YOUR_TOKEN' with the token you were given when registering the bot!
Note my url, I use the program ngrok which creates a virtual white ip, and forwards to my local host

Next, we will create a receiver for this hook in views.py :
```python
...
from django.views.decorators.csrf import csrf_exempt
from viberbot.api.bot_configuration import BotConfiguration
from viberbot import Api
from django.http import HttpResponse

BASE_URL = 'https://7499-188-163-102-40.ngrok-free.app'
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
>Replace 'YOUR_TOKEN'

So, now let's try to run sethook.py, it will serve as our ignition key. First, start your server (if it is not running): 
```
py manage.py runserver
```
Then create a second terminal and run sethook in the project directory:
```
py sethook.py
```
And if your print shows a status of 0, then all is well and your bot has woken up and you can write to it now. Example response :
```
{'status': 0, 'status_message': 'ok', 'chat_hostname': 'SN-CHAT-02_', 'event_types': ['subscribed', 'unsubscribed', 'conversation_started', 'delivered', 'message']}
```
> the bot is available via barcode at partners.viber.com

## Keyboard example
---
I'll add a button to the bot right away:
add some imports
```python
import json
from viberbot.api.messages import TextMessage, KeyboardMessage,  RichMediaMessage
```
then modify our webhook function 
```python
@csrf_exempt
def webhook(request):
    if request.method == "POST":
        viber = json.loads(request.body.decode('utf-8'))
        if viber['event'] == 'conversation_started':
            start_button(viber['user']['id'])
    return HttpResponse(status=200)
```
We are knocked to the server through the webhook that we made, then we store in the variable 'viber' the received information about the "POST" request that came to us, in particular in it we will use the id viber user.
and if the user visits the bot for the first time, the "conversation_started" event will occur. where we will call the function start_button, which will eventually throw back to the user a keyboard with one "start" button. Now about the functions itself :
```python
def start_button_(viber_id):
    keyboard = KeyboardMessage(keyboard=start_build(), min_api_version=6)
    viber_api.send_messages(viber_id, [keyboard])

def start_build():
    keyboard = {
        "Type": "keyboard",
        "InputFieldState" : "hidden",
        "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#ae9ef4",
            "Text": "<font color='#e5e1ff'><b>start</b></font>",
            "TextSize": "large",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "ActionBody": 'start',
            "Silent": True
        },
        ]
    }
    return keyboard
```
The first function calls the keyboard and returns it to the user by its id .
The second function generates the keyboard and returns its styles. 
Note the "ActionBody" : 'start', this means that when the user clicks on this button, it will send us a new request with the event "message" with the value "start". Here's what I got:
![Screenshot_5](https://github.com/uncommonartemon/viberbot/assets/51698182/fe6618c8-8b8b-4536-8660-08dbdcaa1e45)

## Catalog creation 

Now let's put a handler on this message, which will show our sellers to the user:
```python
@csrf_exempt
def webhook(request):
    if request.method == "POST":
        viber = json.loads(request.body.decode('utf-8'))
        if viber['event'] == 'conversation_started':
            start_button(viber['user']['id'])

        if viber['event'] == 'message': #Add a new event handler
            message = viber['message']['text'] #Save the resulting text 
            sender_id = viber['sender']['id'] #Save the id of the user who sent the bot the message
            if message == 'start':
                show_sellers(sender_id)
    return HttpResponse(status=200)
```
Let's immediately prepare a function that will send a request to our host, to get information about sellers:
```python
...
HOST_URL = 'https://faf5-188-163-102-40.ngrok-free.app' #At the beginning of the file, add the address 
... 
```
```python
import requests
...
def api_rest(url):
    api_path = HOST_URL + '/viber/api/' + url
    response = requests.get(api_path)
    result = response.json()
    return result
```
As you remember we have urls.py specifies the paths for the api :
```python
urlpatterns = [
    path('api/sellers/', views.Sellers.as_view(), name='sellers'),
    path('api/seller/<str:seller>', views.Products.as_view(), name='products'),
    path('',views.webhook, name='viber_webhook'),
]
```
Function api_rest will complete the path depending on what we pass to it as an argument.
Next:
```python
def show_sellers(sender_id):
    sellers_list = api_rest('sellers/')
    carousel = RichMediaMessage(tracking_data='tracking_data', min_api_version=7, rich_media=sellers_carousel(sellers_list))
    viber_api.send_messages(sender_id, carousel)

def sellers_carousel(sellers):
    carousel = {
        'Type' : 'rich_media',
        "ButtonsGroupColumns": 6,
        "ButtonsGroupRows": 7,
        "Buttons": [],
        "BgColor": "#ae9ef4",
    }
    for seller in sellers:
        image = {
            'Columns' : 6,
            'Rows': 6,
            'Image': seller['image'],
            'ActionBody': seller['name'],
            'Silent': True,
        }
        name = {
            'Columns' : 6,
            'Rows': 1,
            'Text': "<font color='#e5e1ff'><b>" + seller['name'] + "</b></font>",
            "BgColor": "#ae9ef4",
            'ActionBody': seller['name'],
            'Silent' : True,
        }
        carousel['Buttons'].append(image)
        carousel['Buttons'].append(name)
    return carousel
```
As you can see - here is a similar situation, the only difference is that we get a json sheet with information about our sellers, and implement it in the carousel, instead of keyboad. 
We form the carousel quite simply: we pass the list with sellers to our carousel, and then we form the elements of our carousel by cycles.
Here's how it turned out for me:

![Screenshot_6](https://github.com/uncommonartemon/viberbot/assets/51698182/615ec8e3-577e-4490-9e67-38d865fc6160)
> Note : viber api has a limit on carousel length, keyboard, and also on the size of the received json.

Let's continue , we will also make a handler for the carousel buttons, where we will wait for the name of the seller :
```python
...
        if viber['event'] == 'message':
            message = viber['message']['text'] #Save the resulting text 
            sender_id = viber['sender']['id'] #Save the id of the user who sent the bot the message
            if message == 'start':
                show_sellers(sender_id)
            elif message in sellers_list():
                products(message, sender_id)
```
```python
def sellers_list():
    sellers_list = []
    for seller in api_rest('sellers/'):
        sellers_list.append(seller['name'])
    return sellers_list
```
```python
def products(message, sender_id):
    url = 'seller/' + message
    products = api_rest(url)
    carousel = RichMediaMessage(tracking_data='tracking_data', min_api_version=7, rich_media=products_carousel(products))
    viber_api.send_messages(sender_id, carousel)

def products_carousel(products):
    carousel = {
        'Type' : 'rich_media',
        "ButtonsGroupColumns": 6,
        "ButtonsGroupRows": 7,
        "Buttons": [],
        "BgColor": "#ae9ef4",
    }
    for product in products:
        name = {
            'Columns' : 6,
            'Rows': 1,
            'Text': "<font color='#e5e1ff'><b>" + product['name'] + "</b></font>",
            "BgColor": "#ae9ef4",
            'ActionBody': product['name'],
            'Silent' : True,
        }
        carousel['Buttons'].append(name)
        image = {
            'Columns' : 6,
            'Rows': 5,
            'Image': product['image'],
            'ActionBody': product['name'],
            'Silent': True,
        }
        carousel['Buttons'].append(image)
        weight = {
            'Columns' : 3,
            'Rows': 1,
            'Text': "<font color='#e5e1ff'><b>" + str(product['weight']) + " kg</b></font>",
            "BgColor": "#ae9ef4",
            'ActionBody': product['weight'],
            'Silent': True,
        }
        carousel['Buttons'].append(weight)
        price = {
            'Columns' : 3,
            'Rows': 1,
            'Text': "<font color='#e5e1ff'><b>" + str(product['price']) + " caps</b></font>",
            "BgColor": "#ae9ef4",
            'ActionBody': product['price'],
            'Silent': True,
        }
        carousel['Buttons'].append(price)
        
    return carousel
```

It seems to be working:

![Screenshot_7](https://github.com/uncommonartemon/viberbot/assets/51698182/3336d980-932f-4e80-b3c4-cb498b3bfcdd)

## Liqpay
---
>If the user clicked on the product, then viber sends just the ActionBody of the product to our server, based on that alone we should initiate payment. I will do a rough example (like the whole guide) : just try to find in db a product with the same name that the server received. Usually this is not very practical for a real online store, but for an example it will work.

```python
def webhook(request):
    if request.method == "POST":
      ...
      if viber['event'] == 'message':
        ...
        elif message in product_list():
          pay(message, sender_id) 
```
```python
def product_list():
    products = Product.objects.all()
    product_names = [product.name for product in products]
    return product_names
```
Now let's install the liqpay sdk, I did it via git bash 
```
pip install git+https://github.com/liqpay/sdk-python
```
>This is for newer versions of python

[Liqpay api](#https://www.liqpay.ua/en/documentation/api/home)
Now let's move on to the "pay" function itself:
```python
import random
import string
import datetime
from liqpay import LiqPay
#...
#Other code

def order_number():
    random_numbers = format(random.randint(100, 999))
    order_number = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + random_numbers
    return order_number

def pay(message, sender_id):
    liqpay = LiqPay(PUBLIC_KEY, PRIVATE_KEY)
    params = {
        "action"    : "pay",
        "version"   : "3",
        "amount"    : int(Product.objects.get(name=message).price),
        "currency"  : "UAH", #Unfortunately they don't accept payment with caps :(
        "order_id"  : order_number(),
        'description' : "test",
        #'server_url': HOST_URL + '/viber/pay-callback/', #Here you can specify the path where the call-back will arrive
        #'info': sender_id, #You can write whatever you want, in our case you can use sender_id , and send a message to this user with call-back state
    }
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    response = requests.post(url="https://www.liqpay.ua/api/3/checkout", data={'signature': signature, 'data': data})
    if response.status_code == 200:
        keyboard = KeyboardMessage(keyboard={
            "Type": "keyboard",
            "InputFieldState" : "hidden",
            "Buttons": [
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": "#ae9ef4",
                "Text": "<font color='#e5e1ff'><b>pay</b></font>",
                "TextSize": "large",
                "TextVAlign": "middle",
                "TextHAlign": "center",
                "ActionType":"open-url",
                "ActionBody": response.url,
                "Silent": True
            },
            ]
        }, min_api_version=6)
        viber_api.send_messages(sender_id, [keyboard])
```

> Replace PUBLIC_KEY and PRIVATE_KEY with those given to you by liqpay
>  Previous requests were made by viber itself, collecting all the information together, here - is made by our server. 

Fill in the params: in 'amount' we search for our product among models.Products and use its price. 
Then generate order_id using order_number() : the function returns a set of numbers made up of year, month, day, hour, minute, second and a random three-digit number. 
Next we use the liqpay package to uniquely sign and encode it, and then send it all to "https://www.liqpay.ua/api/3/checkout" at once.
If liqpay has successfully processed everything, it will return a reply with a payment link. We will immediately create a keyboard with a button-link ("ActionType": "open-url") to the link returned by liqpay ("ActionBody": response.url).

