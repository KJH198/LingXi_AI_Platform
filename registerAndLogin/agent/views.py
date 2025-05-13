from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from django.shortcuts import get_object_or_404
from .models import Agent, Workflow, Node
from django.db import DatabaseError
from rest_framework.permissions import IsAuthenticated
import json
from django.conf import settings
import os
import uuid
from datetime import datetime
from user.models import PublishedAgent


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

            # print('保存前的工作流数据结构体:', workflow.structure)

            # new_workflow = Workflow.objects.get(name=workflow.name)
            # print("从数据库中读取到的结构体：", new_workflow.structure)

            # all_workflows = Workflow.objects.all()
            # for wf in all_workflows:
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

    def get(self, request, *args, **kwargs):
        print(request)
        workflow_id = self.kwargs.get('workflowId')

        try:
            workflow = get_object_or_404(Workflow, id=workflow_id)

            return Response({"workflow": workflow.structure}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetWorkflowsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取当前用户的 ID
            user_id = request.user.id

            # 过滤工作流
            workflows = Workflow.objects.filter(user_id=user_id)

            data = []
            for workflow in workflows:
                data.append({
                    'id': workflow.id,
                    'name': workflow.name,
                })

            return Response({
                'code': 200,
                'message': 'success',
                'data': data
            })
        except DatabaseError as e:
            # 数据库查询异常处理
            return Response({
                'code': 500,
                'message': f'数据库查询出错: {str(e)}'
            }, status=500)
        except Exception as e:
            # 其他未知异常处理
            return Response({
                'code': 500,
                'message': f'发生未知错误: {str(e)}'
            }, status=500)


class DeleteWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, workflow_id):
        try:
            workflow = Workflow.objects.get(id=workflow_id, user_id=request.user.id)
            workflow.delete()
            return Response({
                'code': 200,
                'message': '删除成功'
            })
        except Workflow.DoesNotExist:
            return Response({
                'code': 404,
                'message': '该工作流不存在或无权限删除'
            })


class GetInputAndOutputCountView(APIView):
    def get(self, request, workflow_id):  # 改成 get
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            input_nodes = Node.objects.filter(workflow=workflow, node_type='input')
            output_nodes = Node.objects.filter(workflow=workflow, node_type='output')
            input_node_count = input_nodes.count()
            output_node_count = output_nodes.count()

            input_node_names = []
            for node in input_nodes:
                node_data = node.node_data or {}
                name = node_data.get('name', 'input')
                input_node_names.append(name)

            output_node_names = []
            for node in output_nodes:
                node_data = node.node_data or {}
                name = node_data.get('name', 'input')
                output_node_names.append(name)

            data = {
                'input_node_count': input_node_count,
                'input_node_names': input_node_names,
                'output_node_count': output_node_count,
                'output_node_names': output_node_names
            }
            print(data)
            return Response({
                "code": 200,
                "message": "查询成功",  # 改了
                "data": data
            })
        except Workflow.DoesNotExist:
            return Response({
                'code': 404,
                'message': '该工作流不存在'
            })

class AgentGetInputAndOutputCountView(APIView):
    def get(self, request, agent_id):  # 改成 get
        try:
            agent = PublishedAgent.objects.get(id=agent_id)
            workflow_id = agent.workflow_id
            if not workflow_id:
                return Response({
                    'code': 404,
                    'message': '该智能体没有关联的工作流'
                })
            # 获取工作流
            workflow = Workflow.objects.get(id=workflow_id)
            input_nodes = Node.objects.filter(workflow=workflow, node_type='input')
            output_nodes = Node.objects.filter(workflow=workflow, node_type='output')
            input_node_count = input_nodes.count()
            output_node_count = output_nodes.count()

            input_node_names = []
            for node in input_nodes:
                node_data = node.node_data or {}
                name = node_data.get('name', 'input')
                input_node_names.append(name)

            output_node_names = []
            for node in output_nodes:
                node_data = node.node_data or {}
                name = node_data.get('name', 'input')
                output_node_names.append(name)

            data = {
                'input_node_count': input_node_count,
                'input_node_names': input_node_names,
                'output_node_count': output_node_count,
                'output_node_names': output_node_names
            }
            print(data)
            return Response({
                "code": 200,
                "message": "查询成功",  # 改了
                "data": data
            })
        except Workflow.DoesNotExist:
            return Response({
                'code': 404,
                'message': '该工作流不存在'
            })


class AgentAvatarUploadView(APIView):
    """智能体头像上传视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取上传的文件
            avatar_file = request.FILES.get('avatar')
            if not avatar_file:
                return Response({
                    'code': 400,
                    'message': '未检测到上传的头像文件'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 检查文件类型
            if not avatar_file.content_type.startswith('image/'):
                return Response({
                    'code': 400,
                    'message': '请上传图像文件'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 检查文件大小
            if avatar_file.size > 2 * 1024 * 1024:  # 2MB
                return Response({
                    'code': 400,
                    'message': '头像文件不能超过2MB'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 处理文件保存
            # 确保上传目录存在
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'agent_avatars')
            os.makedirs(avatar_dir, exist_ok=True)

            # 生成唯一文件名
            ext = os.path.splitext(avatar_file.name)[1]
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"temp_{uuid.uuid4().hex[:8]}_{timestamp}{ext}"

            # 保存文件
            filepath = os.path.join(avatar_dir, filename)
            with open(filepath, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)

            # 生成URL
            avatar_url = f"/media/agent_avatars/{filename}"

            print('生成的头像URL:', avatar_url)

            # 如果agent_id已存在，更新对应记录的头像URL
            agent_id = request.POST.get('agent_id')
            if agent_id:
                agent = PublishedAgent.objects.filter(id=agent_id).first()
                if agent:
                    # 如果有旧头像，可以考虑删除
                    if agent.avatar and os.path.exists(os.path.join(settings.MEDIA_ROOT, agent.avatar.lstrip('/'))):
                        try:
                            os.remove(os.path.join(settings.MEDIA_ROOT, agent.avatar.lstrip('/')))
                        except:
                            pass  # 忽略删除失败的情况

                    agent.avatar = avatar_url
                    agent.save()

            return Response({
                'code': 200,
                'message': '头像上传成功',
                'data': {
                    'avatar': avatar_url
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'头像上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CleanupTempResourcesView(APIView):
    """清理未使用的临时资源"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print('清理临时资源请求:', request)
            temp_avatar = request.data.get('temp_avatar')
            print('临时资源:', temp_avatar)

            if not temp_avatar:
                return Response({
                    'code': 400,
                    'message': '缺少临时资源信息'
                }, status=status.HTTP_400_BAD_REQUEST)

            filename = os.path.basename(temp_avatar)

            # 确保路径是安全的，只处理temp_前缀的文件
            if 'temp_' in filename:
                print('需要清理的临时文件名:', filename)

                # 直接构建文件路径，避免使用os.path.join与以/开头的路径
                avatar_dir = os.path.join(settings.MEDIA_ROOT, 'agent_avatars')
                file_path = os.path.join(avatar_dir, filename)

                print('构建的文件路径:', file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已清理临时文件: {file_path}")

            return Response({
                'code': 200,
                'message': '临时资源清理成功'
            })

        except Exception as e:
            print(f"清理临时资源失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'清理临时资源失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)