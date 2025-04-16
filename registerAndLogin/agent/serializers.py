from rest_framework import serializers
from .models import Agent, Workflow, Node, KnowledgeBase, Document, DocumentChunk, AgentKnowledgeBase

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'user', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ['id', 'agent', 'name', 'structure', 'created_at']
        read_only_fields = ['created_at']

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'workflow', 'node_id', 'node_type', 'predecessors', 'successors']

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'owner', 'is_public']
        read_only_fields = ['created_at', 'updated_at', 'owner']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'knowledge_base', 'title', 'content', 'document_type', 'created_at', 'updated_at', 'metadata']
        read_only_fields = ['created_at', 'updated_at']

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'content', 'embedding', 'chunk_index', 'metadata']
        read_only_fields = ['embedding']

class AgentKnowledgeBaseSerializer(serializers.ModelSerializer):
    knowledge_base = KnowledgeBaseSerializer(read_only=True)
    knowledge_base_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AgentKnowledgeBase
        fields = ['id', 'agent', 'knowledge_base', 'knowledge_base_id', 'priority', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        knowledge_base_id = validated_data.pop('knowledge_base_id')
        knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id)
        return AgentKnowledgeBase.objects.create(knowledge_base=knowledge_base, **validated_data)
