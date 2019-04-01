from django.db import models


class employee(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    gender = models.IntegerField(default=0)
    comments = models.TextField(null=True)
    department = models.ForeignKey('department', on_delete=models.CASCADE)


class department(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True, default='dept')
    total_income = models.FloatField()

