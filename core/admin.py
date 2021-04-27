from django.contrib import admin
from .models import Foo, FeeRequest, FeeReason

admin.site.register(Foo)
admin.site.register(FeeRequest)
admin.site.register(FeeReason)
