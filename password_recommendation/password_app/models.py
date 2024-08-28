from django.db import models

class UserInfo(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    maiden_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    religion = models.CharField(max_length=10)
    profession = models.CharField(max_length=100)
    complexion = models.CharField(max_length=50)

    def __str__(self):
        return self.name
