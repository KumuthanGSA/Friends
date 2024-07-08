from rest_framework import serializers
#local imports
from .models import User


class AdminRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class SearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'name']
