from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(DiscreteMetricData)
admin.site.register(ContinuousMetricData)
admin.site.register(Test)
