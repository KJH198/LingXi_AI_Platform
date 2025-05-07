from rest_framework import serializers
from user.models import PublishedAgent, User
from knowledge_base.models import KnowledgeBase

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class HotAgentSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer()
    followerCount = serializers.SerializerMethodField()
    likeCount = serializers.SerializerMethodField()
    isFollowed = serializers.SerializerMethodField()
    
    class Meta:
        model = PublishedAgent
        fields = ['id', 'name', 'description', 'avatar', 'creator', 
                 'followerCount', 'views', 'likeCount', 'created_at', 'isFollowed']
    
    def get_followerCount(self, obj):
        return obj.followers.count()
    
    def get_likeCount(self, obj):
        return obj.likes.count()
    
    def get_isFollowed(self, obj):
        # 这个字段是在视图中动态设置的
        return getattr(obj, 'is_followed', False)

class HotKnowledgeBaseSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(source='user')
    fileCount = serializers.SerializerMethodField()
    followerCount = serializers.SerializerMethodField()
    isFollowed = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'creator', 
                 'fileCount', 'followerCount', 'created_at', 'isFollowed']
    
    def get_fileCount(self, obj):
        if hasattr(obj, 'file_count'):
            return obj.file_count
        return obj.files.count()
    
    def get_followerCount(self, obj):
        if hasattr(obj, 'follower_count'):
            return obj.follower_count
        return obj.followers.count()
    
    def get_isFollowed(self, obj):
        return getattr(obj, 'is_followed', False)