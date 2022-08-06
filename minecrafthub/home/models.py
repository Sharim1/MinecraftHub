from django.db import models

# Create your models here.

class ContactUs(models.Model):
    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

