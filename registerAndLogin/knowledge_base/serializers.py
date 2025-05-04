from rest_framework import serializers
from .models import KnowledgeBase, KnowledgeBaseFile

class KnowledgeBaseFileSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(required=True)
    size = serializers.IntegerField(required=True)
    upload_time = serializers.DateTimeField(source='uploaded_at', read_only=True)
    
    class Meta:
        model = KnowledgeBaseFile
        fields = ['id', 'file', 'filename', 'size', 'upload_time', 'status', 'knowledge_base']
        read_only_fields = ['id', 'upload_time', 'status']
    
    def validate(self, data):
        if 'file' not in data:
            raise serializers.ValidationError({"file": "文件不能为空"})
        if 'filename' not in data:
            raise serializers.ValidationError({"filename": "文件名不能为空"})
        if 'size' not in data:
            raise serializers.ValidationError({"size": "文件大小不能为空"})
        return data

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    files = KnowledgeBaseFileSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    name = serializers.CharField(required=True, error_messages={
        'required': '知识库名称不能为空',
        'blank': '知识库名称不能为空'
    })
    type = serializers.ChoiceField(choices=KnowledgeBase.TYPE_CHOICES, required=True, error_messages={
        'required': '知识库类型不能为空',
        'invalid_choice': '知识库类型必须是 text 或 image'
    })
    description = serializers.CharField(required=False, allow_blank=True)
    fileCount = serializers.SerializerMethodField()
    lastUpdated = serializers.SerializerMethodField()
    views = serializers.IntegerField(source='followers.count', read_only=True, default=0)
    followers = serializers.IntegerField(source='followers.count', read_only=True, default=0)
    
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'type', 'status', 'createdAt', 'files', 
                  'fileCount', 'lastUpdated', 'views', 'followers']
        read_only_fields = ['id', 'createdAt', 'status', 'views', 'followers']
    
    def get_fileCount(self, obj):
        # 如果查询时已经通过 annotate 添加了 file_count
        if hasattr(obj, 'file_count'):
            return obj.file_count
        # 否则手动计算
        return obj.files.count()
    
    def get_lastUpdated(self, obj):
        # 返回格式化的最后更新时间
        return obj.created_at.strftime('%Y-%m-%d')  # 可以根据需要调整格式