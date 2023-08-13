from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ContinuousMetricData)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'type', 'alpha')
    list_filter = ('id', 'user', 'name', 'type', 'alpha')
    search_fields = ('id', 'user', 'name', 'type', 'alpha')
    readonly_fields=('id',)

admin.site.register(Test, TestAdmin)

class DiscreteMetricDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'variant', 'metric', 'date')
    list_filter = ('id', 'test', 'variant', 'metric', 'date')
    search_fields = ('id', 'test', 'variant', 'metric', 'date')
    readonly_fields=('id',)

admin.site.register(DiscreteMetricData, DiscreteMetricDataAdmin)
