from rest_framework import serializers
from .models import KnowledgeBase, KnowledgeBaseFile

class KnowledgeBaseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseFile
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    files = KnowledgeBaseFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'type', 'created_at', 'files']
        read_only_fields = ['created_at'] 