from rest_framework import serializers
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model
User = get_user_model()



class CreateUserSerialzier(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id','phone','password')
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



#used for giving in the knox auth login and update user profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'name', 'first_login', 'standard', 'score' )


    def validate(self, attrs):
        phone = attrs.get('phone')
        if phone:
            if User.objects.filter(phone=phone).exists():
                if User.objects.filter(phone=phone).count() > 1:
                    msg = {'detail': 'Phone number is already associated with another user. Try a new one.', 'status':False}
                    raise serializers.ValidationError(msg)

        return attrs


    def update(self, instance, validated_data):
        instance.phone = validated_data['phone']
        instance.name = validated_data['name']
        instance.standard = validated_data['standard']
        instance.score = validated_data['score']

        instance.save()
        return instance




class LoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)


    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            if User.objects.filter(phone=phone).exists():
                user = authenticate(request=self.context.get('request'), phone=phone, password=password)

            else:
                msg = {'detail': 'Phone number is not registered.','register': False}
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs



class ChangePasswordSerializer(serializers.HyperlinkedModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model=User
        fields = ('old_password','password')


    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({'old_password':"Old password is not correct"})
        return value


    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance



class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)