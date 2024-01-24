from django.db import models

class UploadedFile(models.Model):
    class InvoiceType(models.TextChoices):
        RESTAURANT = 'Restaurant_Bill'
        INVOICE = 'Invoice' 
        HOTEL = 'Hotel_Stay_Bill'
        TRAVEL = 'Travel_Bill'
        FUEL = 'Fuel_Bill'
    
    file_id = models.IntegerField(primary_key=True)
    invoice_class = models.CharField(max_length=100,choices=InvoiceType.choices,default=InvoiceType.INVOICE)
    file = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
