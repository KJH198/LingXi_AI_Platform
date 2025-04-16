from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from django.shortcuts import get_object_or_404
from .models import Agent, Workflow, Node, KnowledgeBase, Document, DocumentChunk, AgentKnowledgeBase
import json
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .serializers import (
    AgentSerializer, WorkflowSerializer, NodeSerializer,
    KnowledgeBaseSerializer, DocumentSerializer, DocumentChunkSerializer,
    AgentKnowledgeBaseSerializer
)

class WorkflowSaveView(APIView):

    def post(self, request):
        try:
            data = request.data
            #print('接收到的工作流数据结构体:', data)

            workflow_name = data.get('name')
            if not workflow_name:
                raise ValueError("Workflow name is required.")

            # 使用filter查找workflow，如果没有找到就返回None
            workflow = Workflow.objects.filter(name=workflow_name).first()
            if not workflow:
                # 如果没有找到，创建新的工作流
                workflow = Workflow.objects.create(name=workflow_name)
            else:
                # 如果找到了，删除原有节点
                workflow.nodes.all().delete()

            # ✅ 保存完整结构体
            workflow.structure = data
            workflow.save()

            #print('保存前的工作流数据结构体:', workflow.structure)

            #new_workflow = Workflow.objects.get(name=workflow.name)
            #print("从数据库中读取到的结构体：", new_workflow.structure)

            #all_workflows = Workflow.objects.all()
            #for wf in all_workflows:
            #    print(f"工作流名称: {wf.name}")
            #    print(f"结构体: {wf.structure}")

            # ✅ 保持原有节点存储逻辑
            raw_nodes = data.get('nodes', [])
            raw_edges = data.get('edges', [])

            successors_map = defaultdict(list)
            predecessors_map = defaultdict(list)

            for edge in raw_edges:
                source = edge['source']
                target = edge['target']
                successors_map[source].append(target)
                predecessors_map[target].append(source)

            for node in raw_nodes:
                node_id = node['id']
                node_data = node['data']
                if node.get('type') == 'process':
                    node_type = node_data.get('processType')
                else:
                    node_type = node.get('type')

                Node.objects.create(
                    workflow=workflow,
                    node_id=node_id,
                    node_type=node_type,
                    predecessors=predecessors_map.get(node_id, []),
                    successors=successors_map.get(node_id, [])
                )

            # print(workflow_name)
            # for node in workflow.nodes.all():
            #    print(f"Node {node.node_id}: type={node.node_type}")
            #    print(f"  predecessors: {node.predecessors}")
            #    print(f"  successors: {node.successors}")

            return Response({
                "code": 200,
                "message": "工作流保存成功",
                "data": {
                    "name": workflow.name
                }
            })

        except Exception as e:
            print("保存失败:", str(e))
            return Response({
                "code": 500,
                "message": "保存工作流失败",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkflowRetrieveView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        agent_id = request.data.get('agent_id')
        workflow_id = request.data.get('workflow_id')

        if not all([user_id, agent_id, workflow_id]):
            return Response({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 查找智能体是否属于该用户
            agent = get_object_or_404(Agent, id=agent_id, user_id=user_id)

            # 查找工作流是否属于该智能体
            workflow = get_object_or_404(Workflow, id=workflow_id, agent=agent)

            return Response({"workflow": workflow.structure}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 知识库视图集
class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KnowledgeBase.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        knowledge_base = self.get_object()
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(knowledge_base=knowledge_base)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        knowledge_base = self.get_object()
        documents = Document.objects.filter(knowledge_base=knowledge_base)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

# 文档视图集
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(knowledge_base__owner=self.request.user)

    @action(detail=True, methods=['post'])
    def chunk(self, request, pk=None):
        document = self.get_object()
        content = request.data.get('content')
        chunk_index = request.data.get('chunk_index')
        
        if not content or chunk_index is None:
            return Response(
                {'error': 'Content and chunk_index are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chunk = DocumentChunk.objects.create(
            document=document,
            content=content,
            chunk_index=chunk_index
        )
        
        serializer = DocumentChunkSerializer(chunk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 智能体知识库关联视图集
class AgentKnowledgeBaseViewSet(viewsets.ModelViewSet):
    serializer_class = AgentKnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AgentKnowledgeBase.objects.filter(agent__user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_agent(self, request):
        agent_id = request.data.get('agent_id')
        knowledge_base_id = request.data.get('knowledge_base_id')
        priority = request.data.get('priority', 0)

        agent = get_object_or_404(Agent, id=agent_id, user=request.user)
        knowledge_base = get_object_or_404(KnowledgeBase, id=knowledge_base_id)

        agent_kb = AgentKnowledgeBase.objects.create(
            agent=agent,
            knowledge_base=knowledge_base,
            priority=priority
        )

        serializer = self.get_serializer(agent_kb)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_priority(self, request, pk=None):
        agent_kb = self.get_object()
        priority = request.data.get('priority')
        
        if priority is not None:
            agent_kb.priority = priority
            agent_kb.save()
            
        serializer = self.get_serializer(agent_kb)
        return Response(serializer.data)