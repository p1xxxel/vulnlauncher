from django.db import models

class Search(models.Model):
    search_query = models.CharField(max_length=200)
