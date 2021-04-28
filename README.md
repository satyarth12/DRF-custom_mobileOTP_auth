# DRF - Custom user mobile OTP Authentication System

## Introduction 
This is django-rest-framwork custom mobile otp authentication system, which can be used in multiple use cases for allowing the users to register themselves with the mobile OTP they receive . 
Users can also update their profile.

## Urls
Custom Urls have been used and can be seen in progress via POSTMAN or by connecting it to some frontend framwork.

## Running app
1. activating the pip virtual env 
```
pipenv shell
```
2. Installing packages 
```
pipenv install -r requirements.txt
```
3. Making Migrations
```
python manage.py makemigrations
python manage.py migrate
```
4. Running server
```
python manage.py runserver
```
 
 
### NOTE :
Third party apps such as twillio or any other messaging apps can be used for sending the OTP. 
Here, I've used a simple function to generate OTP in the local server.

