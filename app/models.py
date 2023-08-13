from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class ApiKey(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.prefix


class Test(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    alpha = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class DiscreteMetricData(models.Model):
    id = models.BigAutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    variant = models.CharField(max_length=255)
    metric = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.metric)


class ContinuousMetricData(models.Model):
    id = models.BigAutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    variant = models.CharField(max_length=255)
    metric = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.metric)
