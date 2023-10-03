from rest_framework import generics, serializers
from .models import Seller, Product
import requests
from django.http import HttpResponse, JsonResponse

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
    
from django.views.decorators.csrf import csrf_exempt
from viberbot.api.bot_configuration import BotConfiguration
from viberbot import Api
from django.http import HttpResponse
import json
from viberbot.api.messages import TextMessage, KeyboardMessage,  RichMediaMessage


PUBLIC_KEY = ''
PRIVATE_KEY = ''
HOST_URL = 'https://faf5-188-163-102-40.ngrok-free.app'
bot_configuration = BotConfiguration(
    name="Vault bot",
    avatar=None,
    auth_token='YOUR_TOKEN',
)   
viber_api = Api(bot_configuration)
@csrf_exempt
def webhook(request):
    if request.method == "POST":
        viber = json.loads(request.body.decode('utf-8'))
        if viber['event'] == 'conversation_started':
            start_button(viber['user']['id'])
        if viber['event'] == 'message':
            message = viber['message']['text'] #Save the resulting text 
            sender_id = viber['sender']['id'] #Save the id of the user who sent the bot the message
            if message == 'start':
                show_sellers(sender_id)
            elif message in sellers_list():
                products(message, sender_id)
            elif message in product_list():
                pay(message, sender_id)
    return HttpResponse(status=200)

def start_button(viber_id):
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

def api_rest(url):
    api_path = HOST_URL + '/viber/api/' + url
    response = requests.get(api_path)
    result = response.json()
    return result

def sellers_list():
    sellers_list = []
    for seller in api_rest('sellers/'):
        sellers_list.append(seller['name'])
    return sellers_list    

def product_list():
    products = Product.objects.all()
    product_names = [product.name for product in products]
    return product_names

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

import random
import string
import datetime
from liqpay import LiqPay

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
        "currency"  : "USD", #Unfortunately they don't accept payment with caps :(
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