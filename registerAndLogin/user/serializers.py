from rest_framework import serializers
from .models import User, AgentReview, KnowledgeBase, Agent
from django.utils import timezone
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'phone_number', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', '')
        )
        return user

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'email', 'is_active',
                 'is_admin', 'ban_status', 'ban_start_time', 'ban_end_time')
        read_only_fields = ('id', 'username', 'phone_number', 'email', 'is_admin')

class BanUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    ban_type = serializers.ChoiceField(choices=[
        ('7days', '封禁7天'),
        ('10days', '封禁10天'),
        ('permanent', '永久封禁'),
        ('remove', '解除封禁')
    ])

    def update_ban_status(self, user):
        ban_type = self.validated_data['ban_type']
        
        if ban_type == 'remove':
            user.ban_status = 'normal'
            user.ban_start_time = None
            user.ban_end_time = None
        else:
            user.ban_status = ban_type
            user.ban_start_time = timezone.now()
            if ban_type == '7days':
                user.ban_end_time = timezone.now() + timedelta(days=7)
            elif ban_type == '10days':
                user.ban_end_time = timezone.now() + timedelta(days=10)
            else:  # permanent
                user.ban_end_time = None
        
        user.save()
        return user

class AgentReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    agent = serializers.StringRelatedField()

    class Meta:
        model = AgentReview
        fields = ('id', 'agent', 'user', 'rating', 'comment', 'created_at', 'is_approved')
        read_only_fields = ('id', 'created_at')

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = KnowledgeBase
        fields = ('id', 'title', 'content', 'created_by', 'created_at', 'updated_at', 'is_published')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

class AgentSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Agent
        fields = ('id', 'name', 'description', 'created_by', 'created_at', 'is_public')
        read_only_fields = ('id', 'created_by', 'created_at')