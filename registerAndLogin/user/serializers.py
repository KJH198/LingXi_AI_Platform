from rest_framework import serializers
from .models import User, Announcement, AgentDraft

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



class UserDetailSerializer(serializers.ModelSerializer):

    """用户详情序列化器，包含所有字段"""

    class Meta:

        model = User

        fields = '__all__'

        read_only_fields = ('id', 'created_at', 'updated_at', 'last_login')



class UserBanSerializer(serializers.Serializer):

    """用户封禁序列化器"""

    reason = serializers.CharField(max_length=500, required=True)

    is_permanent = serializers.BooleanField(default=False)


class AgentDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentDraft
        fields = ['id', 'name', 'description', 'avatar', 'model_id', 'workflow_id', 
                 'knowledge_bases', 'model_params', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']