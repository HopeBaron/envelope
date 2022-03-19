from rest_framework import serializers
from . import models


class EntitySerializer(serializers.ModelSerializer):
    create_date = serializers.ReadOnlyField()
    delete_date = serializers.ReadOnlyField()


class UserSerializer(EntitySerializer):
    password = serializers.CharField(write_only=True)
    last_login = serializers.ReadOnlyField()

    class Meta:
        model = models.User
        fields = '__all__'
    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)

class ChatSerializer(EntitySerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=models.User.objects.all()
    )

    class Meta:
        model = models.Chat
        fields = '__all__'


class MessageSerializer(EntitySerializer):
    author = UserSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)

    class Meta:
        model = models.Message
        fields = '__all__'


class MembershipSerializer(EntitySerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all()
    )
    chat = ChatSerializer(read_only=True)

    class Meta:
        model = models.Membership
        fields =  '__all__'
        lookup_field = 'user'
