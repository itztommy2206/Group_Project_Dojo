from django.db import models
import re
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

## ************************* UserManager & User Model****************************** ##
class UserManager(models.Manager):
    def reg_validator(self, postData):
        errors = {}
        if len(postData['first_name']) == 0:
            errors['first_name'] = "First name is required!"
        elif len(postData['first_name']) < 2 or postData['first_name'].isalpha() != True:
            errors['first_name'] = "First name must be at least 2 charactors long, letters only!"
        if len(postData['last_name']) == 0:
            errors['last_name'] = "Last name is required!"
        elif len(postData['last_name']) < 2 or postData['last_name'].isalpha() != True:
            errors['last_name'] = "Last name must be at least 2 charactors long, letters only!"

        if len(postData['email']) == 0:
            errors['email'] = "Email is required!"
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email format!"
        elif User.objects.filter(email = postData['email']).exists():
            errors['email'] = "Email already registed"

        if len(postData['password']) == 0:
            errors['password'] = "Password is required!"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 charactors long!"
        elif postData['password'] != postData['confirm_pw']:
            errors['password'] = "Password and Confirmed Password must match."
        return errors

    def log_validator(self, postData):
        errors = {}
        if len(postData['email']) == 0:
            errors['email'] = "Email is required!"
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email format!"

        if len(postData['password']) == 0:
            errors['password'] = "Password is required!"
        return errors

class User(models.Model):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

class City(models.Model):
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    

    class Meta:
        verbose_name_plural = "cities"