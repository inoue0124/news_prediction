from django.db import models

class Article(models.Model):
    category = models.IntegerField()
    text = models.CharField(max_length=1024)

class naive_model(models.Model):
    vocabularies = models.TextField()
    wordcount = models.TextField()
    prob_category = models.TextField()
    denominator = models.TextField()
    
