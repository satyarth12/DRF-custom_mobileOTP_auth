from django.urls import path, include, re_path
from .views import (SendPhoneOTP, 
					ValidateOTP, 
					Register, 
					LoginAPI, 
					ChangePasswordView, 
					UpdateProfileView, 
					UserView,
					ValidatePhoneForgot,
					ValidateForgotOtp,
					ForgotPasswordChange)
from knox import views as knox_views
app_name = "custom_users"

urlpatterns = [

	path('sendotp/', SendPhoneOTP.as_view()),
	path('validateotp/', ValidateOTP.as_view()),
	path('register/', Register.as_view()),

	path('login/', LoginAPI.as_view()),
	path('logout/', knox_views.LogoutView.as_view()),
	path('change_password/<int:pk>/', ChangePasswordView.as_view()),

	path('user_profile/', UserView.as_view()),
	path('update_profile/<int:pk>/', UpdateProfileView.as_view()),

	path('validate_phone_forgot/', ValidatePhoneForgot.as_view()),
	path('validate_forgot_otp/', ValidateForgotOtp.as_view()),
	path('change_forgot_password/', ForgotPasswordChange.as_view())

]