from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Test(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    name = models.CharField(max_length = 255)
    type = models.CharField(max_length = 255)

    def __str__(self):
        return self.name

class DiscreteMetricData(models.Model):
    test      =  models.ForeignKey(Test,on_delete = models.CASCADE)
    variant   =  models.CharField(max_length = 255)
    metric    =  models.BinaryField()
    dataTime  =  models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.metric)
    
class ContinuousMetricData(models.Model):
    test      =  models.ForeignKey(Test,on_delete = models.CASCADE)
    variant   =  models.CharField(max_length = 255)
    metric    =  models.DecimalField(max_digits = 5, decimal_places = 2)
    dataTime  =  models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.metric)