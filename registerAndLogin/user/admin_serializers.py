from rest_framework import serializers
from .admin_models import UserBanRecord, AgentRating, KnowledgeBase
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_active']

class UserBanRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBanRecord
        fields = '__all__'

class AgentRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRating
        fields = '__all__'

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = '__all__'