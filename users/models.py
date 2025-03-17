from django.db import models

# Create your models here.
def __str__(self):
    return self.name

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)   