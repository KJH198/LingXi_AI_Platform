from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from django.shortcuts import get_object_or_404
from .models import Agent, Workflow, Node
import json

class WorkflowSaveView(APIView):

    def post(self, request):
        try:
            data = request.data
            print('接收到的工作流数据结构体:', data)

            user_id = request.data.get("userId")
            name = data.get('name')
            if not name:
                raise ValueError("Workflow name is required.")

            # 使用filter查找workflow，如果没有找到就返回None
            workflow = Workflow.objects.filter(name=name, user_id=user_id).first()
            if not workflow:
                # 如果没有找到，创建新的工作流
                workflow = Workflow.objects.create(name=name, user_id=user_id)
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
                source_handle = edge.get('sourceHandle')
                target_handle = edge.get('targetHandle')
                successors_map[source].append({
                    'target': target,
                    'targetHandle': target_handle
                })
                predecessors_map[target].append({
                    'source': source,
                    'sourceHandle': source_handle
                })

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
                    node_data=node_data,
                    predecessors=predecessors_map.get(node_id, []),
                    successors=successors_map.get(node_id, [])
                )

            print('workflow id:', workflow.id)
            for node in workflow.nodes.all():
                print(f"Node {node.node_id}: type={node.node_type}")
                print(f"  predecessors: {node.predecessors}")
                print(f"  successors: {node.successors}")

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