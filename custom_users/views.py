from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import permissions, generics, status

from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.db.models import Q
import requests

from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView

from django.views.decorators.csrf import csrf_exempt

from .utils import otp_generator

from .models import User, PhoneOTP
from .serializers import (CreateUserSerialzier, 
                        ChangePasswordSerializer, 
                        LoginUserSerializer, 
                        UserSerializer, 
                        UserSerializer,
                        ForgotPasswordSerializer)



class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)
        return super().post(request, format=None)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]



class UpdateProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer


class UserView(generics.RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user




def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or 
    passed phone number as argument.
    """

    if phone:
        
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)

        #link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfrg&templatename=wisfrags&var1={otp_key}'
   
        #result = requests.get(link, verify=False)

        return otp_key
    else:
        return False

'''
Send OTP to the new user but if the user exists then no OTP wil be send, instead user has to reset password again
ALso, if the OTP count is more than 10 then, user has to contact the customer care support.
'''
class SendPhoneOTP(APIView):
    def post(self, *args, **kwargs):
        phone_number = self.request.data.get('phone')

        if phone_number:

            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)

            if user.exists():  #this means that the user already exists, no new OTP for them
                return Response({'status':False, 'detail':'User already exist. Kindly reset your password.'})

            else: #if the user doesn't exists 
                otp = send_otp(phone)
                print(phone, otp)
                if otp: #if the otp already exists, then we'll increase the PhoneOTP.count by 1, max_limit is 10
                    otp = str(otp)
                    old_otp = PhoneOTP.objects.filter(phone__iexact = phone)

                    if old_otp.exists():
                        old_otp = old_otp.first()
                        otp_count = old_otp.count

                        if otp_count > 10:
                            return Response ({
                            'status':False,
                            'detail':'You have exceeded the OTP limit. Kindly contact our customer care support.'
                            })

                        old_otp.count = otp_count + 1
                        old_otp.otp = otp
                        old_otp.save()
                        print("count increase", old_otp.count)
                        return Response ({
                        'status':True,
                        'detail':'OTP sent successfully.'
                        })

                    else:
                        PhoneOTP.objects.create(
                            phone = phone,
                            otp = otp)
                        return Response ({
                        'status':True,
                        'detail':'OTP sent successfully.'
                        })
                        

                else:
                    return Response ({
                        'status':False,
                        'detail':'OTP sending error. Please try after sometime'
                        })


        else:
            return Response ({
                'status': False,
                'detail':'No phone number has been received. Kindly do the POST request.'
                })




'''
Validating the OTP which is sent to the user
'''

class ValidateOTP(APIView):
    def post(self, *args, **kwargs):
        phone = self.request.data.get('phone',False)
        otp_sent = self.request.data.get('otp',False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)

            if old.exists():
                old = old.first()
                otp = old.otp

                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()
                    return Response({
                        'status' : True, 
                        'detail' : 'OTP matched, kindly proceed to save password'
                    })
                else:
                    return Response({
                        'status' : False, 
                        'detail' : 'OTP incorrect, please try again'
                    })

            else:
                return Response({
                    'status' : False,
                    'detail' : 'Incorrect Phone number. Kindly request a new otp with this number'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or otp was not recieved in Post request'
            })




class Register(APIView):
    # permission_classes_by_action = {'create': [permissions.AllowAny]}
    def post(self, *args, **kwargs):
        phone = self.request.data.get('phone', False)
        password = self.request.data.get('password', False)
        
        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)

            if user.exists():
                return Response({
                    'status': False, 
                    'detail': 'Phone Number already have account associated. Kindly try forgot password'
                    })

            else:
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    old=old.first()

                    if old.logged:
                        temp_data = {'phone':phone,'password':password}
                        serializer = CreateUserSerialzier(data=temp_data)
                        serializer.is_valid(raise_exception = True)
                        user = serializer.save()

                        old.delete()
                        return Response({
                            'status' : True, 
                            'detail' : 'Congratulations, user has been created successfully.'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                        })

                else:
                    return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly request a new otp with this number'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or password was not recieved in Post request'
            })






class ValidatePhoneForgot(APIView):
    def post(self, *args, **kwargs):
        phone_number = self.request.data.get('phone')

        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)

            if user.exists():
                otp = send_otp(phone)
                print(phone, otp)

                if otp:
                    otp = str(otp)
                    old = PhoneOTP.objects.filter(phone__iexact=phone)

                    if old.exists():
                        old=old.first()
                        # count=old.count

                        if old.count > 10:
                            return Response({
                                'status' : False, 
                                'detail' : 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                            })
                        else:
                            old.count = old.count+1
                            old.otp = otp
                            old.save()
                            return Response({'status': True, 'detail': 'OTP has been sent for password reset. Limits about to reach.'})

                    else:
                        count = 0
                        count = count + 1
                        PhoneOTP.objects.create(
                            phone=phone,
                            otp=otp,
                            count=count,
                            forgot=True)
                        return Response({'status': True, 'detail': 'OTP has been sent for password reset'})

                else:
                    return Response({
                                    'status': False, 'detail' : "OTP sending error. Please try after some time."
                                })


            else:
                return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly try a new account for this number'
                })




class ValidateForgotOtp(APIView):
    def post(self, *args, **kwargs):
        phone = self.request.data.get('phone', False)
        otp_sent = self.request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone=phone)

            if old.exists():
                old=old.first()

                if old.forgot==False:
                    return Response({
                        'status' : False, 
                        'detail' : 'This phone has not received valid otp for forgot password. Request a new otp or contact help centre.'
                    })

                else:
                    otp = old.otp

                    if str(otp) == str(otp_sent):
                        old.forgot_logged = True
                        old.save()
                        return Response({
                        'status' : True, 
                        'detail' : 'OTP matched, kindly proceed to create new password'
                        })

                    else:
                        return Response({
                        'status' : False, 
                        'detail' : 'OTP incorrect, please try again'
                        })

            else:
                return Response({
                    'status' : False,
                    'detail' : 'Phone not recognised. Kindly request a new otp with this number'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or otp was not recieved in Post request'
            })





class ForgotPasswordChange(APIView):
    def post(self, *args, **kwargs):
        phone = self.request.data.get('phone', False)
        otp = self.request.data.get('otp', False)
        password = self.request.data.get('password', False)

        if phone and otp and password:
            old = PhoneOTP.objects.filter(Q(phone__iexact = phone) & Q(otp__iexact = otp))
            if old.exists():

                old = old.first()
                if old.forgot_logged:

                    post_data ={
                    'phone':phone,
                    'password':password
                    }
                    user_obj = get_object_or_404(User, phone__iexact=phone)
                    serializer = ForgotPasswordSerializer(data = post_data)

                    if serializer.is_valid():
                        if user_obj:
                            user_obj.set_password(serializer.data.get('password'))
                            user_obj.is_active = True
                            user_obj.save()
                            old.delete()
                            return Response({
                            'status' : True,
                            'detail' : 'Password changed successfully. Please Login'
                            })

                else:
                    return Response({
                    'status' : False,
                    'detail' : 'OTP Verification failed. Please try again in previous step'
                    })

            else:
                return Response({
                'status' : False,
                'detail' : 'Phone and otp are not matching or a new phone has entered. Request a new otp in forgot password'
            })

        else:
            return Response({
                'status' : False,
                'detail' : 'Post request have parameters mising.'
            })




