from django.contrib import admin
from .models import Lecturer, Review, Comment, Faculty

# This tells Django to display these tables in the admin panel
admin.site.register(Lecturer)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Faculty)