from django.db import models

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
    