from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json
from rest_framework.parsers import JSONParser
from .models import AIAgent, AbnormalBehavior, Announcement, User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserDetailSerializer, AgentDraftSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings
from django.utils import timezone
import time
from datetime import timedelta
from .models import (
    User, UserActionLog, PublishedAgent, AgentComment,
    AgentDraft,
    # ... 其他导入 ...
)
from knowledge_base.models import KnowledgeBase, KnowledgeBaseComment
from django.core.paginator import Paginator
from community.models import Post, PostImage, PostAgent, PostKnowledgeBase
from community.models import PostLike, PostFavorite, PostComment
from django.shortcuts import get_object_or_404
# from community.models import PostComment as AgentComment
# from community.models import Post
# from ..knowledge_base.models import KnowledgeBase, KnowledgeBaseComment

@csrf_exempt
def register(request):
    """
    Register a new user.

    Request body should contain:
    - username: The username of the user.
    - password: The password of the user.
    - phone_number: The phone number of the user.
    - email (optional): The email address of the user.

    Returns:
    - 201: User registered successfully.
    - 400: Invalid request data or user already exists.
    - 405: Invalid request method.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        phone_number = data.get('phone_number')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        if User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'error': 'Phone number already exists'}, status=400)

        User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            email=email,
        )
        return JsonResponse({'message': 'User registered successfully'}, status=201)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def user_login(request):
    """
    用户登录接口

    请求体格式:
    {
        "phone_number": "手机号",
        "password": "密码"
    }

    返回格式:
    {
        "success": true/false,
        "token": "token字符串"  // 登录成功时返回
        "message": "错误信息"   // 登录失败时返回
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            password = data.get('password')

            if not phone_number or not password:
                return JsonResponse({
                    'success': False,
                    'message': '手机号和密码不能为空'
                })
            # 通过手机号查找用户
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
            except Exception as e:
                print(f"查询用户出错: {str(e)}")
                print(f"错误类型: {type(e)}")
                import traceback
                traceback.print_exc()
                return JsonResponse({
                    'success': False,
                    'message': '服务器内部错误'
                }, status=500)
            # 验证上次登录是否在今天
            if user.last_login and user.last_login.date() != timezone.now().date():
                user.online_duration = timezone.timedelta()  # 重置在线时长
                user.login_times = 0  # 重置登录次数
                user.unexpected_operation_times = 0  # 重置异常操作次数
                user.save()
                
            # 验证密码
            if not user.check_password(password):
                UserActionLog.objects.create(
                    user=user,
                    action='login_failed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    target_id=user.id,
                    target_type='user'
                )
                user.unexpected_operation_times += 1
                user.save()
                return JsonResponse({
                    'success': False,
                    'message': '密码错误'
                })
            # 验证封禁
            if user.is_banned():
                UserActionLog.objects.create(
                    user=user,
                    action='login_failed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    target_id=user.id,
                    target_type='user'
                )
                ban_type_mapping = {
                'light': '轻度违规',
                'medium': '中度违规',
                'severe': '严重违规',
                'permanent': '永久封禁'
                }
                reason = f"{ban_type_mapping.get(user.ban_type, '未知类型')}（{user.ban_reason}）"
                return JsonResponse({
                    'success': False,
                    'message': '账号封禁中：' + reason
                })
            user.is_active = True
            user.save()
            
            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # 登录用户
            login(request, user)
            
            # 生成登录日志信息
            UserActionLog.objects.create(
                user=user,
                action='login',
                ip_address=request.META.get('REMOTE_ADDR'),
                target_id=user.id,
                target_type='user'
            )
            user.last_login = timezone.now()
            user.login_times += 1
            if user.last_login_ip != request.META.get('REMOTE_ADDR'):
                AbnormalBehavior.objects.create(
                    user=user,
                    abnormal_type='login_ip_change',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    is_handled=False,
                    handled_at=None,
                    handled_notes=''
                )
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()

            return JsonResponse({
                'success': True,
                'id': user.id,
                'token': access_token
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的请求数据'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': '不支持的请求方法'
    }, status=405)

@csrf_exempt
def user_logout(request, user_id=None):
    """
    用户登出接口

    返回格式:
    {
        "success": true/false,
        "message": "错误信息"  // 登出失败时返回
    }
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        UserActionLog.objects.create(
                user=request.user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
                target_id=request.user.id,
                target_type='user'
            )
        user = User.objects.filter(id=user_id).first()
        user.online_duration += timedelta(seconds=(time.time() - user.last_login.timestamp()))
        user.save()
        print(f"User {user.username} logged out. Today online duration: {user.online_duration}")
        try:
            return JsonResponse({
                'code': 200
            })
        except Exception as e:
            return JsonResponse({
                'code': 500
            })

@csrf_exempt
def update_user_info(request):
    """
    Update user information.

    Request body may contain:
    - username: The new username of the user.
    - phone_number: The new phone number of the user.
    - email: The new email address of the user.
    - bio: The new bio of the user.

    Returns:
    - 200: User information updated successfully.
    - 400: Username or phone number already exists.
    - 401: User is not authenticated.
    - 405: Invalid request method.
    """
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        data = json.loads(request.body)
        user = request.user

        # 检查用户名是否已存在
        if 'username' in data and data['username'] != user.username:
            user.username = data['username']
        if 'phone_number' in data and data['phone_number'] != user.phone_number:
            if User.objects.filter(phone_number=data['phone_number']).exists():
                return JsonResponse({'error': 'Phone number already exists'}, status=400)
            user.phone_number = data['phone_number']
        if 'email' in data:
            user.email = data['email']
        if 'bio' in data:
            user.bio = data['bio']
            
        user.save()
        return JsonResponse({'message': 'User information updated successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def home(request):
    return render(request, 'home.html')

class UserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class AdminDashboardView(APIView):
    """管理员操作台视图"""
    def get(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 返回操作台基本信息
        data = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'banned_users': User.objects.filter(is_banned=True).count()
        }
        return Response(data)

class UserManagementView(APIView):
    """用户管理视图，提供以下功能：
    1. 获取用户列表及统计信息
    2. 获取单个用户详情
    """
    def get(self, request, user_id=None):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 获取单个用户详情
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response({
                    'user': serializer.data,
                    'message': '获取用户详情成功'
                })
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取用户列表及统计信息
        users = User.objects.all()
        user_data = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'registerTime': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'lastLoginTime': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                'status': 'banned' if user.is_banned() else 'normal',
                'violationType': user.ban_type if user.ban_type else None,
            }
            user_data.append(user_dict)
        
        return Response({
            'users': user_data,
            'total': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'banned_users': User.objects.filter(ban_until__gt=timezone.now()).count(),
            'message': '获取用户列表成功'
        })

class AdminBanView(APIView):
    """管理员封禁用户"""
    def post(self, request, user_id=None):
        """封禁用户"""
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        if not user_id:
            return Response({'error': '用户ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        ban_type = request.data.get('type')  # 获取封禁类型，默认为严重违规
        ban_reason = request.data.get('reason')  # 获取封禁原因
        duration = request.data.get('duration')  # 获取封禁时长
        
        try:
            user = User.objects.get(id=user_id)
            user.ban_reason = ban_reason
            user.ban_type = ban_type
            if (ban_type == 'permanent'):
                user.ban_until = datetime.now() + timedelta(days=365*100)  # 永久封禁
            else:
                # 将时间戳转换为datetime对象
                from datetime import datetime, timedelta
                user.ban_until = datetime.now() + timedelta(days=duration)
            user.save()
            
            return Response({
                'success': True,
                'message': '用户封禁成功'
            })
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

class AdminUnbanView(APIView):
    """管理员解封用户"""
    def post(self, request, user_id=None):
        """解封用户"""
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        if not user_id:
            return Response({'error': '用户ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.ban_reason = None
            user.ban_until = None
            user.ban_type = None
            user.save()
            
            # 生成新的JWT令牌
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            return Response({
                'success': True,
                'message': '用户解封成功',
                'token': access_token  # 返回新的访问令牌
            })
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

class AgentRatingView(APIView):
    """智能体评分与评价"""
    def post(self, request):
        # 验证用户权限
        if not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        agent_id = request.data.get('agent_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        # 验证评分范围(1-5星)
        if not rating or not 1 <= int(rating) <= 5:
            return Response({'error': '评分必须是1-5之间的整数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存评价到数据库
        from .models import AgentRating
        try:
            rating_obj = AgentRating.objects.create(
                user=request.user,
                agent_id=agent_id,
                rating=rating,
                comment=comment
            )
            return Response({
                'message': '评价成功',
                'rating_id': rating_obj.id
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """获取智能体列表"""
        try:
            # 验证管理员权限
            if not request.user.is_admin:
                return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

            from .models import AIAgent

            # 获取查询参数
            status_filter = request.query_params.get('status', 'pending')

            # 查询智能体列表
            agents = AIAgent.objects.filter(status=status_filter)

            # 构造返回数据
            data = [
                {
                    'id': agent.id,
                    'name': agent.name,
                    'creator': agent.creator.username,
                    'status': agent.status,
                    'created_at': agent.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for agent in agents
            ]

            return Response({
                'agents': data,
                'total': agents.count(),
                'pending_count': AIAgent.objects.filter(status='pending').count(),
                'approved_count': AIAgent.objects.filter(status='approved').count(),
                'rejected_count': AIAgent.objects.filter(status='rejected').count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListAPIView(APIView):
    """获取用户列表接口"""
    def get(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all()
        user_data = []
        for user in users:
            user_dict = {
                'id': str(user.id),
                'username': user.username,
                'register_time': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'violation_type': user.ban_reason.split(':')[0] if user.ban_reason else None,
                'status': 'banned' if user.is_banned() else 'normal',
                'ip_address': user.last_login_ip if hasattr(user, 'last_login_ip') else None,
                'device': user.last_login_device if hasattr(user, 'last_login_device') else None
            }
            user_data.append(user_dict)
        
        return Response({'users': user_data})

class UserDetailAPIView(APIView):
    """获取用户详情接口"""
    def get(self, request, user_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            return Response({
                'id': str(user.id),
                'username': user.username,
                'register_time': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login_time': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                'violation_type': user.ban_reason.split(':')[0] if user.ban_reason else None,
                'status': 'banned' if user.is_banned() else 'normal',
                'ip_address': user.last_login_ip if hasattr(user, 'last_login_ip') else None,
                'device': user.last_login_device if hasattr(user, 'last_login_device') else None
            })
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

class UserOperationRecordsView(APIView):
    """获取用户操作记录接口"""
    def post(self, request, user_id=None):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        page = 1
        page_size = 20
        
        if user_id:
            userActionLogs = UserActionLog.objects.filter(user_id=user_id)
        else:
            userActionLogs = UserActionLog.objects.all()
        
        # 构造返回数据
        records = [
            {
                'user_id':log.user.id,
                'ip_address':log.ip_address,
                'user_name':log.user.username,
                'time':log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'action':log.get_action_display() if hasattr(log, 'get_action_display') else log.action,
                'target_id':log.target_id,
                'target_type':log.get_target_type_display() if hasattr(log, 'get_target_type_display') else log.target_type
            }for log in userActionLogs if log.action != 'login_failed' and log.action != 'logout' and log.action != 'login'
        ]
        
        paginator = Paginator(records, page_size)
        try:
            records_page = paginator.page(page)
        except:
            records_page = paginator.page(1)
        
        return Response({
            'records': records,
            'total': paginator.count,
            'page': records_page.number,
            'page_size': int(page_size),
            'page_count': paginator.num_pages
        })

class UserAbnormalBehaviorsView(APIView):
    """获取用户异常行为接口"""
    def get(self, request, user_id=None):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        page = 1
        page_size = 20
        
        if user_id:
            logs = AbnormalBehavior.objects.filter(user_id=user_id).all()
        else:
            logs = AbnormalBehavior.objects.filter().all()
        
        # 构造返回数据
        behaviors = [
            {
                'user_id': log.user.id,
                'user_name': log.user.username,
                'abnormal_time': log.abnormal_time.strftime('%Y-%m-%d %H:%M:%S') if log.abnormal_time else None,
                'abnormal_type': log.abnormal_type,
                'ip_address': log.ip_address,
                'is_handled': log.is_handled,
                'handled_at': log.handled_at.strftime('%Y-%m-%d %H:%M:%S') if log.handled_at else None,
                'handled_notes': log.handled_notes,
            }
            for log in logs
        ]
        
        paginator = Paginator(behaviors, page_size)
        try:
            behaviors_page = paginator.page(page)
        except:
            behaviors_page = paginator.page(1)
        
        return Response({
            'behaviors': behaviors,
            'total': paginator.count,
            'page': behaviors_page.number,
            'page_size': int(page_size),
            'page_count': paginator.num_pages
        })

class AdminGetAgents(APIView):
    """获取智能体列表接口"""
    def get(self, request, agent_id=None):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 获取查询参数
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        
        if agent_id:
            agents = PublishedAgent.objects.filter(id=agent_id).first()
        else:
            agents = PublishedAgent.objects.filter(status='pending').order_by('-created_at')

        # 构造返回数据
        agent_data = [
            {
                'agentID':agent.id,
                'name':agent.name,
                'description':agent.description,
                'time':agent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'creatorID':agent.creator.id,
                'status':agent.status,
                'is_OpenSource':agent.is_OpenSource,
            } for agent in agents
        ]
    
        # 分页处理
        paginator = Paginator(agent_data, page_size)
        try:
            agents_page = paginator.page(page)
        except:
            agents_page = paginator.page(1)
        
        return Response({
            'agents': agent_data,
            'total': paginator.count,
            'page': agents_page.number,
            'page_size': int(page_size),
            'page_count': paginator.num_pages
        })

class AdminChangeAgentSataus(APIView):
    def post(self, request, agent_id=None):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        if not agent_id:
            return Response({'error': '智能体ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            enable = request.data.get('enable')
            agent = PublishedAgent.objects.filter(id=agent_id).first()
            if enable:
                agent.status = 'approved'
            else:
                agent.status = 'rejected'
                AbnormalBehavior.objects.create(
                    user=agent.creator,
                    abnormal_type='content_violation',
                    ip_address=agent.creator.last_login_ip,
                    is_handled=False,
                    handled_at=None,
                    handled_notes=''
                )
            agent.save()
            return Response({
                'success': True,
                'message': '智能体状态更新成功'
            })

class UserBehaviorStatsView(APIView):
    """获取用户行为统计数据接口"""
    def get(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 模拟统计数据
        return Response({
            'today_logins': 15,
            'avg_login_duration': 12.5,
            'abnormal_logins': 3
        })

class UserBehaviorLogsView(APIView):
    """获取用户行为日志接口"""
    def get(self, request, user_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 模拟行为日志数据
        logs = [{
            'id': '1',
            'action': 'login',
            'target_id': None,
            'target_type': None,
            'ip_address': '192.168.1.1',
            'created_at': '2025-04-20T10:00:00Z'
        }]
        
        return Response({
            'logs': logs,
            'total': len(logs)
        })

class KnowledgeBaseView(APIView):
    """知识库管理"""
    def post(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        title = request.data.get('title')
        content = request.data.get('content')
        
        # 实际项目中应该保存到知识库模型
        return Response({'message': '知识库创建成功'})

    def delete(self, request, kb_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 实际项目中应该删除知识库记录
        return Response({'message': '知识库删除成功'})

    def put(self, request, kb_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        content = request.data.get('content')
        # 实际项目中应该更新知识库内容
        return Response({'message': '知识库更新成功'})

class AdminLoginView(APIView):
    """
    管理员登录接口
    
    请求体格式:
    {
        "phone_number": "手机号",
        "password": "密码"
    }

    返回格式:
    {
        "success": true/false,
        "token": "token字符串"  // 登录成功时返回
        "message": "错误信息"   // 登录失败时返回
    }
    """
    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')
            password = request.data.get('password')

            if not phone_number or not password:
                return Response({
                    'success': False,
                    'message': '手机号和密码不能为空'
                })

            # 通过手机号查找用户
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '用户不存在'
                })

            # 验证是否为管理员
            if not user.is_admin:
                return Response({
                    'success': False,
                    'message': '你不是管理员'
                })

            # 验证密码
            if not user.check_password(password):
                return Response({
                    'success': False,
                    'message': '密码错误'
                })

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'success': True,
                'token': access_token,
                'id': user.id,
                'message': '管理员登录成功'
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFollowingView(APIView):
    """
    用户关注相关接口
    
    1. 获取关注列表
    请求方式: GET
    路径参数: user_id - 用户ID
    
    2. 关注用户
    请求方式: POST
    路径参数: user_id - 当前用户ID
    请求体: {
        "target_user_id": 目标用户ID
    }
    
    3. 取消关注
    请求方式: DELETE
    路径参数: user_id - 当前用户ID
    请求体: {
        "target_user_id": 目标用户ID
    }
    
    返回格式:
    {
        "success": true/false,
        "data": {
            "following": [
                {
                    "id": 用户ID,
                    "username": "用户名",
                    "phone_number": "手机号",
                    "email": "邮箱"
                }
            ],
            "following_count": 关注数,
            "followers_count": 粉丝数
        },
        "message": "错误信息"  // 失败时返回
    }
    """
    def get(self, request, user_id):
        try:
            # 获取目标用户
            target_user = User.objects.get(id=user_id)
            
            # 获取关注列表
            following = target_user.following.all()
            
            # 序列化关注用户数据
            following_data = [{
                'id': user.id,
                'username': user.username,
                'phone_number': user.phone_number,
                'email': user.email
            } for user in following]
            
            return Response({
                'success': True,
                'data': {
                    'following': following_data,
                    'following_count': target_user.get_following_count(),
                    'followers_count': target_user.get_followers_count()
                }
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, user_id):
        """
        关注用户
        """
        try:
            # 验证用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 获取目标用户ID
            target_user_id = user_id
            if not target_user_id:
                return Response({
                    'success': False,
                    'message': '目标用户ID不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 获取目标用户
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '目标用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否已经关注
            if request.user.is_following(target_user):
                return Response({
                    'success': False,
                    'message': '已经关注过该用户'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 添加关注
            if request.user.follow(target_user):
                return Response({
                    'success': True,
                    'message': '关注成功'
                })
            else:
                return Response({
                    'success': False,
                    'message': '不能关注自己'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, user_id):
        """
        取消关注用户
        """
        try:
            # 验证用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 获取目标用户ID
            target_user_id = user_id
            if not target_user_id:
                return Response({
                    'success': False,
                    'message': '目标用户ID不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 获取目标用户
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '目标用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否已经关注
            if not request.user.is_following(target_user):
                return Response({
                    'success': False,
                    'message': '未关注该用户'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 取消关注
            request.user.unfollow(target_user)
            return Response({
                'success': True,
                'message': '取消关注成功'
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserInfoView(APIView):
    """获取用户信息接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'code': 200,
            'username': user.username,
            'phone_number': user.phone_number,
            'email': user.email,
            'bio': user.bio,
            'avatar': user.avatar,
            'posts_count': 0,  # 暂时写死为0
            'followers': user.get_followers_count(),
            'following': user.get_following_count()
        }
        return Response(data)

class UpdateUserInfoView(APIView):
    """更新用户信息接口"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'email' in data:
            user.email = data['email']
        if 'bio' in data:
            user.bio = data['bio']
        if 'avatar' in data:
            user.avatar = data['avatar']

        try:
            user.save()
            return Response({
                'code': 200,
                'message': '个人信息更新成功'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)


class UploadAvatarView(APIView):
    """上传用户头像接口"""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        user = request.user
        avatar_file = request.FILES.get('avatar')

        if not avatar_file:
            return Response({
                'code': 400,
                'message': '请选择要上传的头像文件'
            }, status=400)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'code': 400,
                'message': '只支持jpg、png、gif格式的图片'
            }, status=400)

        # 验证文件大小（限制为2MB）
        if avatar_file.size > 2 * 1024 * 1024:
            return Response({
                'code': 400,
                'message': '图片大小不能超过2MB'
            }, status=400)

        try:
            # 生成文件名
            file_extension = avatar_file.name.split('.')[-1]
            file_name = f'avatars/{user.id}_{int(time.time())}.{file_extension}'

            # 确保目录存在
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            if not os.path.exists(avatar_dir):
                os.makedirs(avatar_dir)

            # 保存文件
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)

            # 更新用户头像URL
            avatar_url = f'{settings.MEDIA_URL}{file_name}'
            user.avatar = avatar_url
            user.save()

            return Response({
                'code': 200,
                'message': '头像更新成功',
                'data': {
                    'avatar': avatar_url
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'头像上传失败：{str(e)}'
            }, status=500)

class AgentManagementView(APIView):

    """智能体管理视图，提供以下功能：

    1. 获取待审核智能体列表

    2. 审核智能体

    3. 获取智能体详情

    """

    def get(self, request):

        # 验证管理员权限

        if not request.user.is_admin:

            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        

        from .models import AIAgent

        status_filter = request.query_params.get('status', 'pending')

        

        # 获取智能体列表

        agents = AIAgent.objects.filter(status=status_filter)

        

        # 返回智能体基本信息

        data = [{

            'id': agent.id,

            'name': agent.name,

            'creator': agent.creator.username,

            'status': agent.status,

            'created_at': agent.created_at

        } for agent in agents]

        

        return Response({

            'agents': data,

            'total': agents.count(),

            'pending_count': AIAgent.objects.filter(status='pending').count(),

            'approved_count': AIAgent.objects.filter(status='approved').count(),

            'rejected_count': AIAgent.objects.filter(status='rejected').count()

        })



    def post(self, request):

        """审核智能体"""

        # 验证管理员权限

        if not request.user.is_admin:

            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        

        agent_id = request.data.get('agent_id')

        decision = request.data.get('decision')  # 'approve' or 'reject'

        notes = request.data.get('notes', '')

        

        from .models import AIAgent, AgentReview

        try:

            agent = AIAgent.objects.get(id=agent_id)

            

            # 更新智能体状态

            if decision == 'approve':

                agent.status = 'approved'

            else:

                agent.status = 'rejected'

            agent.review_notes = notes

            agent.save()

            

            # 创建审核记录

            AgentReview.objects.create(

                agent=agent,

                reviewer=request.user,

                decision=decision,

                notes=notes

            )

            

            return Response({

                'success': True,

                'message': '审核操作成功',

                'new_status': agent.status

            })

            

        except AIAgent.DoesNotExist:

            return Response({'error': '智能体不存在'}, status=status.HTTP_404_NOT_FOUND)

class UserActionLogView(APIView):
    """用户行为日志视图"""

    def get(self, request):
        """用户行为日志视图"""
        try:
            # 验证管理员权限
            if not request.user.is_admin:
                return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

            from .models import UserActionLog
            from django.db.models import Q

            # 获取查询参数
            user_id = request.query_params.get('user_id')
            action = request.query_params.get('action')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # 构建查询条件
            query = Q()
            if user_id and user_id != 'undefined':
                query &= Q(user_id=user_id)
            if action and action != 'undefined':
                query &= Q(action=action)
            if start_date and start_date != 'undefined':
                query &= Q(created_at__gte=start_date)
            if end_date and end_date != 'undefined':
                query &= Q(created_at__lte=end_date)

            # 获取日志记录
            logs = UserActionLog.objects.filter(query).order_by('-created_at')


            # 返回日志数据
            data = [
                {
                    'id': log.id,
                    'user_id': log.user.id,
                    'user_name': log.user.username if log.user else '未知用户',
                    # 直接使用显示值而不是代码值
                    'action': log.get_action_display() if hasattr(log, 'get_action_display') else log.action,
                    'target_id': log.target_id,
                    'target_type': log.get_target_type_display() if hasattr(log, 'get_target_type_display') else log.target_type,
                    'ip_address': log.ip_address,
                    'time': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for log in logs
            ]

            return Response({
                'logs': data,
                'total': logs.count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSearchView(APIView):

    """用户搜索视图，返回完整用户信息"""

    permission_classes = [IsAuthenticated]

    

    def get(self, request):

        query = request.query_params.get('q', '')

        users = User.objects.filter(username__icontains=query)

        serializer = UserDetailSerializer(users, many=True)

        return Response({

            'success': True,

            'data': serializer.data

        })

class UserLoginRecordView(APIView):
    """用户登录记录视图"""
    def post(self, request, user_id=None):
        try:
            # 验证管理员权限
            if not request.user.is_admin:
                return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
            
            # 获取查询参数(没有用默认值)
            data = JSONParser().parse(request)
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if user_id:
                # 查询特定用户的登录信息
                userActionLogs = UserActionLog.objects.filter(user_id=user_id).order_by('-created_at')
            else:
                # 查询所有用户登录信息
                userActionLogs = UserActionLog.objects.all().order_by('-created_at')

            # 构造返回数据
            records = [
                {
                    'user_id':userActionLog.user.id,
                    'ip_address':userActionLog.ip_address,
                    'user_name':userActionLog.user.username,
                    'time':userActionLog.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_active':userActionLog.user.is_active,
                    'user_email':userActionLog.user.email,
                    'user_phone_number':userActionLog.user.phone_number
                }
                for userActionLog in userActionLogs if userActionLog.action == 'login' or userActionLog.action == 'logout' or userActionLog.action == 'failed_login'
            ]
            
            total_login_times = 0
            total_online_duration = timezone.timedelta()
            total_unexpected_operation_times = 0
            if user_id:
                # 计算特定用户的登录次数、在线时长和异常操作次数
                user = User.objects.get(id=user_id)
                total_login_times = user.login_times
                total_online_duration = user.online_duration
                total_unexpected_operation_times = user.unexpected_operation_times
            else:
                # 计算所有用户的登录次数、在线时长和异常操作次数
                for user in User.objects.all():
                    total_login_times += user.login_times
                    total_online_duration += user.online_duration
                    total_unexpected_operation_times += user.unexpected_operation_times
                    
                    if user.login_times >= 30:
                        AbnormalBehavior.objects.create(
                            user=user,
                            abnormal_time=timezone.now(),
                            abnormal_type='frequent_login',
                            ip_address=user.last_login_ip,
                            is_handled=False,
                            handled_notes='',
                        )
                    if user.unexpected_operation_times >= 5:
                        AbnormalBehavior.objects.create(
                            user=user,
                            abnormal_time=timezone.now(),
                            abnormal_type='frequent_failed_login',
                            ip_address=user.last_login_ip,
                            is_handled=False,
                            handled_notes='',
                        )
                    if user.online_duration >= timezone.timedelta(hours=12):
                        AbnormalBehavior.objects.create(
                            user=user,
                            abnormal_time=timezone.now(),
                            abnormal_type='long_online_duration',
                            ip_address=user.last_login_ip,
                            is_handled=False,
                            handled_notes='',
                        )
            
            # 分页处理
            paginator = Paginator(records, page_size)
            try:
                records_page = paginator.page(page)
            except:
                records_page = paginator.page(1)

            return Response({
                'total_login_times': total_login_times,
                'total_online_duration': str(total_online_duration),
                'total_unexpected_operation_times': total_unexpected_operation_times,
                'records': records,
                'total': paginator.count,
                'page': records_page.number,
                'page_size': int(page_size),
                'page_count': paginator.num_pages
            })
        except Exception as e:
            print("获取用户登录记录时发生错误:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAnnouncements(APIView):
    """获取公告列表"""
    def get(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        announcements = Announcement.objects.all()
        data = [
            {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'status': announcement.status,
                'publish_time': announcement.publishTime.strftime('%Y-%m-%d %H:%M:%S') if announcement.publishTime else None
            }
            for announcement in announcements
        ]
        return Response({
            'code': 200,
            'announcements': data,
        })

class UserGetAnnouncements(APIView):
    """获取公告列表"""
    def get(self, request):
        # 验证用户权限
        if not request.user.is_authenticated:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        announcements = Announcement.objects.filter(status='published').order_by('-publishTime')
        data = [
            {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'status': announcement.status,
                'publish_time': announcement.publishTime.strftime('%Y-%m-%d %H:%M:%S') if announcement.publishTime else None
            }
            for announcement in announcements
        ]
        return Response({
            'code': 200,
            'announcements': data,
        })
    

class CreateAnnouncement(APIView):
    """创建公告"""
    def post(self, request):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        announcement = Announcement.objects.create(
            title=request.data.get('title'),
            content=request.data.get('content'),
            status=request.data.get('status'),
            publishTime=request.data.get('publishTime')
        )
        return Response({
            'code': 200,
            'announcement': {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'status': announcement.status,
                'publishTime': announcement.publishTime if announcement.publishTime else None
            }
        })

class EditAnnouncement(APIView):
    """更新公告"""
    def post(self, request, announcement_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        try:
            announcement = Announcement.objects.get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Response({'error': '公告不存在'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        announcement.title = data.get('title', announcement.title)
        announcement.content = data.get('content', announcement.content)
        announcement.status = data.get('status', announcement.status)
        announcement.publishTime = data.get('publishTime', announcement.publishTime)
        announcement.save()
        
        return Response({
            'code': 200,
            'message': '公告更新成功'
        })

class DeleteAnnouncement(APIView):
    """删除公告"""
    def post(self, request, announcement_id):
        # 验证管理员权限
        if not request.user.is_admin:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

        try:
            announcement = Announcement.objects.get(id=announcement_id)
            announcement.delete()
            return Response({'code': 200,'message': '公告删除成功'})
        except Announcement.DoesNotExist:
            return Response({'error': '公告不存在'}, status=status.HTTP_404_NOT_FOUND)

class CheckAnnouncements(APIView):
    """检查公告是否更新"""
    def get(self, request):
        # 验证用户权限
        if not request.user.is_authenticated:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        user = User.objects.get(id=request.user.id)
        # 获取最新公告的发布时间
        latest_announcement = Announcement.objects.filter(status='published').order_by('-publish_time').first()
        if latest_announcement and latest_announcement.publish_time > user.last_announcement_check:
            return Response({
                'code': 200,
                'has_new_announcements': True,
                'latest_announcement_time': latest_announcement.publish_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        else :
            return Response({
                'code': 200,
                'has_new_announcements': False
            })

class Update(APIView):
    """更新最后一次看公告时间"""
    def post(self, request):
        # 验证用户权限
        if not request.user.is_authenticated:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        User.objects.filter(id=request.user.id).update(updated_at=timezone.now())

class AgentPublishView(APIView):
    """智能体发布视图"""
    
    def post(self, request):
        """发布智能体"""
        try:
            print("收到发布智能体请求")
            print("请求数据:", request.data)
            
            # 获取请求数据
            data = request.data
            name = data.get('name')
            description = data.get('description')
            model_id = data.get('modelId')
            avatar = data.get('avatar')
            knowledge_bases = data.get('knowledgeBases', [])
            workflow_id = data.get('workflowId')
            
            # 处理头像文件
            if avatar and 'temp_' in avatar:
                try:
                    # 获取文件名
                    old_filename = os.path.basename(avatar)
                    new_filename = old_filename.replace('temp_', '')
                    
                    # 构建完整的文件路径
                    old_path = os.path.join(settings.MEDIA_ROOT, 'agent_avatars', old_filename)
                    new_path = os.path.join(settings.MEDIA_ROOT, 'agent_avatars', new_filename)
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(old_path), exist_ok=True)
                    
                    # 如果源文件存在，则重命名
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        # 更新头像URL
                        avatar = f"/media/agent_avatars/{new_filename}"
                    else:
                        print(f"警告：找不到源文件 {old_path}")
                        # 如果找不到源文件，保持原始URL不变
                except Exception as e:
                    print(f"处理头像文件时出错：{str(e)}")
                    # 如果处理失败，保持原始URL不变
            
            print("解析的数据:")
            print(f"名称: {name}")
            print(f"描述: {description}")
            print(f"头像URL: {avatar}")
            print(f"模型ID: {model_id}")
            print(f"知识库: {knowledge_bases}")
            print(f"工作流ID: {workflow_id}")
            
            # 验证必填字段
            if not all([name, model_id]):
                print("缺少必要字段")
                return Response({
                    'code': 400,
                    'message': '缺少必要字段',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建智能体
            print("开始创建智能体")
            agent = PublishedAgent.objects.create(
                name=name,
                description=description,
                creator=request.user,
                status='pending',  # 默认为待审核状态
                model_id=model_id,
                avatar=avatar,
                workflow_id=workflow_id
            )
            print(f"智能体创建成功，ID: {agent.id}")
            
            # 添加知识库关联
            if knowledge_bases:
                print("添加知识库关联")
                agent.knowledge_bases.set(knowledge_bases)
            
            UserActionLog.objects.create(
                user=request.user,
                action='publish_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            # 返回成功响应
            response_data = {
                'code': 200,
                'message': '智能体发布成功，等待审核',
                'data': {
                    'id': agent.id,
                    'name': agent.name,
                    'status': agent.status,
                    'created_at': agent.created_at
                }
            }
            print("返回响应:", response_data)
            return Response(response_data)
            
        except Exception as e:
            print("发布失败，错误:", str(e))
            return Response({
                'code': 500,
                'message': f'发布失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAgentListView(APIView):
    """获取用户智能体列表接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取当前用户创建的智能体列表
            agents = PublishedAgent.objects.filter(creator=request.user)
            
            # 构建响应数据
            agent_list = []
            for agent in agents:
                # 获取关注数量
                follow_count = agent.followers.count() if hasattr(agent, 'followers') else 0
                
                # 检查当前用户是否已关注该智能体
                is_followed = False
                if hasattr(agent, 'followers'):
                    is_followed = agent.followers.filter(id=request.user.id).exists()
                
                agent_data = {
                    'id': str(agent.id),
                    'name': agent.name,
                    'description': agent.description,
                    'avatar': agent.avatar,
                    'creator': {
                        'id': agent.creator.id,
                        'username': agent.creator.username,
                        'avatar': agent.creator.avatar
                    },
                    'followCount': follow_count,
                    'isFollowed': is_followed,
                    'is_OpenSource': agent.is_OpenSource
                }
                agent_list.append(agent_data)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': agent_list
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取智能体列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserKnowledgeBaseListView(APIView):
    """获取用户知识库列表接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取当前用户创建的知识库列表
            knowledge_bases = KnowledgeBase.objects.filter(user=request.user)
            
            # 构建响应数据
            kb_list = []
            for kb in knowledge_bases:
                kb_data = {
                    'id': str(kb.id),
                    'name': kb.name,
                    'description': kb.description,
                    'creator': {
                        'id': kb.user.id,
                        'username': kb.user.username,
                        'avatar': kb.user.avatar
                    },
                    'fileCount': kb.files.count(),
                    'followCount': 0,  # 知识库模型中没有关注功能
                    'isFollowed': False  # 知识库模型中没有关注功能
                }
                kb_list.append(kb_data)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': kb_list
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取知识库列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostCreateView(APIView):
    """创建帖子视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取请求数据
            title = request.data.get('title')
            content = request.data.get('content')
            images = request.data.get('images', [])
            agents = request.data.get('agents', [])
            knowledge_bases = request.data.get('knowledgeBases', [])

            # 验证必填字段
            if not title or not content:
                return Response({
                    'code': 400,
                    'message': '标题和内容不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证标题长度
            if len(title) > 100:
                return Response({
                    'code': 400,
                    'message': '标题长度不能超过100个字符'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证内容长度
            if len(content) > 2000:
                return Response({
                    'code': 400,
                    'message': '内容长度不能超过2000个字符'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 创建帖子
            post = Post.objects.create(
                title=title,
                content=content,
                user=request.user
            )

            # 添加图片
            for image_url in images:
                PostImage.objects.create(
                    post=post,
                    image_url=image_url
                )

            # 添加关联的智能体
            if agents:
                for agent_id in agents:
                    PostAgent.objects.create(
                        post=post,
                        agent_id=agent_id
                    )

            # 添加关联的知识库
            if knowledge_bases:
                for kb_id in knowledge_bases:
                    PostKnowledgeBase.objects.create(
                        post=post,
                        knowledge_base_id=kb_id
                    )
                
            UserActionLog.objects.create(
                user=request.user,
                action='create_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '发布成功',
                'data': {
                    'postId': post.id
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'发布失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostImageUploadView(APIView):
    """上传帖子图片视图"""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            # 获取上传的文件
            files = request.FILES.getlist('files')

            # 验证文件数量
            if len(files) > 9:
                return Response({
                    'code': 400,
                    'message': '最多只能上传9张图片'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证文件大小和类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            max_size = 5 * 1024 * 1024  # 5MB

            uploaded_urls = []
            for file in files:
                # 验证文件类型
                if file.content_type not in allowed_types:
                    return Response({
                        'code': 400,
                        'message': '只支持jpg、png、gif格式的图片'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 验证文件大小
                if file.size > max_size:
                    return Response({
                        'code': 400,
                        'message': '图片大小不能超过5MB'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 生成文件名
                file_extension = file.name.split('.')[-1]
                file_name = f'post_images/{request.user.id}_{int(time.time())}_{len(uploaded_urls)}.{file_extension}'

                # 确保目录存在
                image_dir = os.path.join(settings.MEDIA_ROOT, 'post_images')
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)

                # 保存文件
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # 添加文件URL到列表
                file_url = f'{settings.MEDIA_URL}{file_name}'
                uploaded_urls.append(file_url)

            return Response({
                'code': 200,
                'message': '上传成功',
                'data': uploaded_urls
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'上传失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostLikeView(APIView):
    """帖子点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, postId):
        try:
            # 获取帖子
            post = Post.objects.get(id=postId)
            
            # 检查是否已经点赞
            if PostLike.objects.filter(post=post, user=request.user).exists():
                return Response({
                    'code': 400,
                    'message': '已经点赞过了'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建点赞记录
            PostLike.objects.create(post=post, user=request.user)
            
            # 更新帖子点赞数
            post.like_count += 1
            post.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='like_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '点赞成功',
                'data': None
            })
            
        except Post.DoesNotExist:
            return Response({
                'code': 404,
                'message': '帖子不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'点赞失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, postId):
        try:
            # 获取帖子
            post = Post.objects.get(id=postId)
            
            # 检查是否已经点赞
            like = PostLike.objects.filter(post=post, user=request.user).first()
            if not like:
                return Response({
                    'code': 400,
                    'message': '还没有点赞'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 删除点赞记录
            like.delete()
            
            # 更新帖子点赞数
            post.like_count -= 1
            post.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unlike_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '取消点赞成功',
                'data': None
            })
            
        except Post.DoesNotExist:
            return Response({
                'code': 404,
                'message': '帖子不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消点赞失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostFavoriteView(APIView):
    """帖子收藏视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, postId):
        try:
            # 获取帖子
            post = Post.objects.get(id=postId)
            
            # 检查是否已经收藏
            if PostFavorite.objects.filter(post=post, user=request.user).exists():
                return Response({
                    'code': 400,
                    'message': '已经收藏过了'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建收藏记录
            PostFavorite.objects.create(post=post, user=request.user)
            
            # 更新帖子收藏数
            post.favorite_count += 1
            post.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='favorite_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '收藏成功',
                'data': None
            })
            
        except Post.DoesNotExist:
            return Response({
                'code': 404,
                'message': '帖子不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'收藏失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, postId):
        try:
            # 获取帖子
            post = Post.objects.get(id=postId)
            
            # 检查是否已经收藏
            favorite = PostFavorite.objects.filter(post=post, user=request.user).first()
            if not favorite:
                return Response({
                    'code': 400,
                    'message': '还没有收藏'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 删除收藏记录
            favorite.delete()
            
            # 更新帖子收藏数
            post.favorite_count -= 1
            post.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unfavorite_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '取消收藏成功',
                'data': None
            })
            
        except Post.DoesNotExist:
            return Response({
                'code': 404,
                'message': '帖子不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消收藏失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostCommentView(APIView):
    """帖子评论视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, postId):
        try:
            # 获取请求数据
            content = request.data.get('content')
            
            # 验证评论内容
            if not content:
                return Response({
                    'code': 400,
                    'message': '评论内容不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证评论长度
            if len(content) > 1000:  # 假设评论最大长度为1000字符
                return Response({
                    'code': 400,
                    'message': '评论内容不能超过1000个字符'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取帖子
            try:
                post = Post.objects.get(id=postId)
            except Post.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '帖子不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 创建评论
            comment = PostComment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            
            # 更新帖子评论数
            post.comment_count += 1
            post.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='comment_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '评论成功',
                'data': {
                    'commentId': comment.id,
                    'time': comment.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'评论失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentFollowView(APIView):
    """智能体关注视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, agentId):
        try:
            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=int(agentId))
            except (PublishedAgent.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '智能体不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经关注
            if agent.followers.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '已经关注过了'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 添加关注
            agent.followers.add(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='follow_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '关注成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'关注失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, agentId):
        try:
            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=int(agentId))
            except (PublishedAgent.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '智能体不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经关注
            if not agent.followers.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '还没有关注'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 取消关注
            agent.followers.remove(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unfollow_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '取消关注成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消关注失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminGetKB(APIView):
    """获取知识库列表接口"""
    # 验证管理员权限
    permission_classes = [IsAuthenticated]

    def get(self, kb_id = None):
        try:
            # 获取所有知识库
            if kb_id:
                knowledge_bases = KnowledgeBase.objects.filter(id=kb_id).first()
            else:
                knowledge_bases = KnowledgeBase.objects.filter(status='pending').order_by('-created_at')
            
            # 构建响应数据
            kb_list = [
                {
                    'id': str(kb.id),
                    'name': kb.name,
                    'description': kb.description,
                    'creatorID': kb.user.id,
                    'fileCount': kb.files.count()
                } for kb in knowledge_bases
            ]
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': kb_list
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取知识库列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminChangeKBSataus(APIView):
    """管理员修改知识库状态接口"""
    # 验证管理员权限
    permission_classes = [IsAuthenticated]

    def post(self, request, kb_id):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=kb_id)
            except KnowledgeBase.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '知识库不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 更新知识库状态
            status = request.data.get('status')
            if status not in ['approved', 'rejected']:
                return Response({
                    'code': 400,
                    'message': '无效的状态'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            kb.status = status
            kb.save()
            
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowledgeBaseFollowView(APIView):
    """知识库关注视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, kbId):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=int(kbId))
            except (KnowledgeBase.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '知识库不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经关注
            if kb.followers.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '已经关注过了'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 添加关注
            kb.followers.add(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='follow_knowledge_base',
                target_id=kb.id,
                target_type='knowledge_base',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '关注成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'关注失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, kbId):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=int(kbId))
            except (KnowledgeBase.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '知识库不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经关注
            if not kb.followers.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '还没有关注'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 取消关注
            kb.followers.remove(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unfollow_knowledge_base',
                target_id=kb.id,
                target_type='knowledge_base',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '取消关注成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消关注失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentDetailView(APIView):
    """获取智能体详情视图"""
    def get(self, request, agentId):
        try:
            # 获取智能体信息
            agent = PublishedAgent.objects.get(id=agentId)
            
            # 获取当前用户（如果已登录）
            user = request.user if request.user.is_authenticated else None
            
            # 获取评论列表
            comments = []
            for comment in agent.agent_comments.filter(parent=None).order_by('-created_at'):
                comments.append({
                    'id': str(comment.id),
                    'user': {
                        'id': comment.user.id,
                        'username': comment.user.username,
                        'avatar': comment.user.avatar if hasattr(comment.user, 'avatar') else None
                    },
                    'time': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': comment.content,
                    'likes': comment.likes.count(),
                    'replies': [
                        {
                            'id': str(reply.id),
                            'user': {
                                'id': reply.user.id,
                                'username': reply.user.username,
                                'avatar': reply.user.avatar if hasattr(reply.user, 'avatar') else None
                            },
                            'time': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'content': reply.content,
                            'likes': reply.likes.count()
                        } for reply in comment.replies.all().order_by('created_at')
                    ]
                })
            
            # 构建响应数据
            data = {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'creator': {
                    'id': agent.creator.id,
                    'username': agent.creator.username,
                    'avatar': agent.creator.avatar if agent.creator.avatar else None
                },
                'views': agent.views,
                'likes': agent.likes.count(),
                'followers': agent.followers.count(),
                'isFollowed': user in agent.followers.all() if user else False,
                'isLiked': user in agent.likes.all() if user else False,
                'avatar': agent.avatar,
                'modelId': agent.model_id,
                'workflowId': agent.workflow_id,
                'status': agent.status,
                'createdAt': agent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updatedAt': agent.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'knowledgeBases': [
                    {
                        'id': str(kb.id),
                        'name': kb.name,
                        'description': kb.description,
                        'fileCount': kb.files.count() if hasattr(kb, 'files') else 0,
                        'followCount': kb.followers.count(),
                        'isFollowed': user in kb.followers.all() if user else False
                    } for kb in agent.knowledge_bases.all()
                ],
                'comments': comments
            }
            
            # 增加浏览量
            agent.views += 1
            agent.save()
            
            return Response({
                'code': 200,
                'message': '获取智能体详情成功',
                'data': data
            })
            
        except PublishedAgent.DoesNotExist:
            return Response({
                'code': 404,
                'message': '智能体不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取智能体详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowledgeBaseDetailView(APIView):
    """获取知识库详情视图"""
    def get(self, request, kbId):
        try:
            # 获取知识库信息
            kb = KnowledgeBase.objects.get(id=kbId)
            
            # 获取当前用户（如果已登录）
            user = request.user if request.user.is_authenticated else None
            
            # 获取知识库文件列表
            files = []
            for file in kb.files.all():
                files.append({
                    'id': str(file.id),
                    'name': file.filename,
                    'type': file.file.name.split('.')[-1] if file.file else None,
                    'size': file.size,
                    'lastUpdated': file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'isPublic': True,  # 默认公开
                    'url': file.file.url if file.file else None
                })
            
            # 构建响应数据
            data = {
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'fileCount': kb.files.count(),
                'views': 0,  # 知识库模型中没有浏览量字段
                'followers': kb.followers.count(),
                'lastUpdated': kb.created_at.strftime('%Y-%m-%d'),  # 使用创建时间作为最后更新时间
                'isFollowed': user in kb.followers.all() if user else False,
                'isLiked': user in kb.likes.all() if user else False,
                'tags': [],  # 知识库模型中没有标签字段
                'scenarios': [],  # 知识库模型中没有场景字段
                'creator': {
                    'id': kb.user.id,
                    'username': kb.user.username,
                    'avatar': kb.user.avatar if hasattr(kb.user, 'avatar') else None
                },
                'files': files,
                'relatedAgents': [],  # 知识库模型中没有关联智能体
                'comments': []  # 知识库模型中没有评论功能
            }
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': data
            })
            
        except KnowledgeBase.DoesNotExist:
            return Response({
                'code': 404,
                'message': '知识库不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取知识库详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentEditDetailView(APIView):
    """获取待编辑的智能体详情"""
    def get(self, request, agent_id):
        try:
            # 获取智能体
            agent = get_object_or_404(PublishedAgent, id=agent_id)
            print(f"获取智能体: {agent.name}")
            
            # # 检查是否是创建者
            # if request.user != agent.creator:
            #     return Response({
            #         'code': 403,
            #         'message': '您没有权限编辑该智能体',
            #         'data': None
            #     }, status=status.HTTP_403_FORBIDDEN)
            
            print("检查权限通过")
            # 组装智能体详情数据
            agent_data = {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'avatar': agent.avatar,  # 直接使用avatar字符串字段
                'status': agent.status,
                'modelId': agent.model_id,
                'workflowId': agent.workflow_id,
                'is_active': agent.is_active,
                'created_at': agent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': agent.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'knowledgeBases': [str(kb.id) for kb in agent.knowledge_bases.all()],
                # 添加模型参数字段，如果存在的话
                'modelParams': {
                    'temperature': agent.temperature if hasattr(agent, 'temperature') else None,
                    'max_tokens': agent.max_tokens if hasattr(agent, 'max_tokens') else None,
                    'top_p': agent.top_p if hasattr(agent, 'top_p') else None
                }
            }

            print("组装数据成功")
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': agent_data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取智能体详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UseAgentView(APIView):
    """获取智能体详情"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, agent_id):
        try:
            # 获取智能体
            agent = get_object_or_404(PublishedAgent, id=agent_id)
            print(f"获取智能体: {agent.name}")
            
            # 检查用户权限
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            
            # 组装智能体详情数据
            agent_data = {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'avatar': agent.avatar,  # 直接使用avatar字符串字段
                'status': agent.status,
                'modelId': agent.model_id,
                'workflowId': agent.workflow_id,
                'is_active': agent.is_active,
                'created_at': agent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': agent.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'knowledgeBases': [str(kb.id) for kb in agent.knowledge_bases.all()],
                # 添加模型参数字段，如果存在的话
                'modelParams': {
                    'temperature': agent.temperature if hasattr(agent, 'temperature') else None,
                    'max_tokens': agent.max_tokens if hasattr(agent, 'max_tokens') else None,
                    'top_p': agent.top_p if hasattr(agent, 'top_p') else None
                }
            }

            print("组装数据成功")
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': agent_data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取智能体详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OpenAgentView(APIView):
    """开源智能体"""
    def get(self, request, agent_id):
        try:
            agent = PublishedAgent.objects.get(id=agent_id)
            return Response({
                'code': 200,
                'is_OpenSource': agent.is_OpenSource,
                'message': '获取开源状态成功'
            })
        except PublishedAgent.DoesNotExist:
            return Response({
                'code': 404,
                'message': '智能体不存在',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, agent_id):
        try:
            # 获取智能体
            agent = PublishedAgent.objects.get(id=agent_id, creator =request.user)
            
            # 检查权限（只有创建者可以修改开源状态）
            if agent.creator != request.user:
                return Response({
                    'code': 403,
                    'message': '您没有权限修改此智能体的开源状态',
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取开源状态
            is_open = request.data.get('isOpen', False)
            
            # 更新开源状态
            agent.is_OpenSource = is_open
            agent.save()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='change_agent_open_source',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '开源状态更新成功',
                'is_OpenSource': agent.is_OpenSource
            })
        except PublishedAgent.DoesNotExist:
            return Response({
                'code': 404,
                'message': '智能体不存在',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFollowedAgentsView(APIView):
    """获取用户关注的智能体列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取当前用户关注的智能体
            agents = PublishedAgent.objects.filter(followers=request.user)
            
            # 构建响应数据
            agent_list = []
            for agent in agents:
                # 获取关注数量
                follow_count = agent.followers.count() if hasattr(agent, 'followers') else 0
                
                # 检查当前用户是否已关注该智能体
                is_followed = False
                if hasattr(agent, 'followers'):
                    is_followed = agent.followers.filter(id=request.user.id).exists()
                
                agent_data = {
                    'id': str(agent.id),
                    'name': agent.name,
                    'description': agent.description,
                    'avatar': agent.avatar,
                    'creator': {
                        'id': agent.creator.id,
                        'username': agent.creator.username,
                        'avatar': agent.creator.avatar
                    },
                    'followCount': follow_count,
                    'isFollowed': is_followed,
                    'is_OpenSource': agent.is_OpenSource
                }
                agent_list.append(agent_data)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': agent_list
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取智能体列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentUpdateView(APIView):
    """更新智能体"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, agent_id):
        try:
            # 获取智能体
            agent = get_object_or_404(PublishedAgent, id=agent_id)
            
            # 检查权限
            if request.user != agent.creator:
                return Response({
                    'code': 403,
                    'message': '您没有权限编辑该智能体',
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取请求数据
            data = request.data
            
            # 更新基本信息
            if 'name' in data:
                agent.name = data['name']
            if 'description' in data:
                agent.description = data['description']
            if 'modelId' in data:
                agent.model_id = data['modelId']
            
            # 更新模型参数
            if 'modelParams' in data:
                model_params = data['modelParams']
                if 'temperature' in model_params:
                    agent.temperature = model_params['temperature']
                if 'maxTokens' in model_params:
                    agent.max_tokens = model_params['maxTokens']
                if 'topP' in model_params:
                    agent.top_p = model_params['topP']
            
            # 更新工作流
            if 'workflowId' in data:
                agent.workflow_id = data['workflowId']
            
            # 更新知识库（多对多关系）
            if 'knowledgeBases' in data:
                from knowledge_base.models import KnowledgeBase
                # 清空现有关联
                agent.knowledge_bases.clear()
                # 添加新关联
                for kb_id in data['knowledgeBases']:
                    try:
                        kb = KnowledgeBase.objects.get(id=kb_id)
                        agent.knowledge_bases.add(kb)
                    except KnowledgeBase.DoesNotExist:
                        continue
            
            # 保存更改
            agent.save()
            
            return Response({
                'code': 200,
                'message': '智能体更新成功',
                'data': {'id': str(agent.id)}
            })
        
        except PublishedAgent.DoesNotExist:
            return Response({
                'code': 404,
                'message': '智能体不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新智能体失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AgentCommentView(APIView):
    """智能体评论视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, agentId):
        try:
            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=agentId)
            except PublishedAgent.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '智能体不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 获取评论内容
            content = request.data.get('content')
            if not content:
                return Response({
                    'code': 400,
                    'message': '评论内容不能为空',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证评论长度
            if len(content) > 500:
                return Response({
                    'code': 400,
                    'message': '评论内容不能超过500个字符',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 获取父评论ID
            parent_comment_id = request.data.get('parentCommentId')
            parent_comment = None
            if parent_comment_id:
                try:
                    parent_comment = AgentComment.objects.get(id=parent_comment_id, agent=agent)
                except AgentComment.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '父评论不存在',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)

            # 创建评论
            comment = AgentComment.objects.create(
                agent=agent,
                user=request.user,
                content=content,
                parent=parent_comment
            )

            # 构建响应数据
            response_data = {
                'commentId': str(comment.id),
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'avatar': request.user.avatar if hasattr(request.user, 'avatar') else None
                },
                'time': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'content': comment.content,
                'likes': 0,
                'replies': []
            }

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='comment_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '评论提交成功',
                'data': response_data
            })

        except Exception as e:
            print(f"评论提交失败: {str(e)}")  # 添加错误日志
            return Response({
                'code': 500,
                'message': f'评论提交失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentCommentLikeView(APIView):
    """智能体评论点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, commentId):
        try:
            # 获取评论
            try:
                comment = AgentComment.objects.get(id=commentId)
            except AgentComment.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '评论不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否已经点赞
            if comment.likes.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '已经点赞过了',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 添加点赞
            comment.likes.add(request.user)

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='like_comment',
                target_id=comment.id,
                target_type='comment',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '点赞成功',
                'data': {
                    'commentId': comment.id,
                    'likes': comment.likes.count()
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'点赞失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentLikeView(APIView):
    """智能体点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, agentId):
        """点赞智能体"""
        try:
            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=agentId)
            except PublishedAgent.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '智能体不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否已经点赞
            if agent.likes.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '已经点赞过了',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 添加点赞
            agent.likes.add(request.user)

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='like_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '点赞成功',
                'data': {
                    'agentId': str(agent.id),
                    'likes': agent.likes.count(),
                    'isLiked': True
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'点赞失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, agentId):
        """取消点赞智能体"""
        try:
            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=agentId)
            except PublishedAgent.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '智能体不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否已经点赞
            if not agent.likes.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '还没有点赞',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 取消点赞
            agent.likes.remove(request.user)

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unlike_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '取消点赞成功',
                'data': {
                    'agentId': str(agent.id),
                    'likes': agent.likes.count(),
                    'isLiked': False
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消点赞失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentCommentReplyView(APIView):
    """智能体评论回复视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, commentId):
        try:
            # 获取父评论
            try:
                parent_comment = AgentComment.objects.get(id=commentId)
            except AgentComment.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '评论不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 获取回复内容
            content = request.data.get('content')
            if not content:
                return Response({
                    'code': 400,
                    'message': '回复内容不能为空',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证回复长度
            if len(content) > 500:
                return Response({
                    'code': 400,
                    'message': '回复内容不能超过500个字符',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 创建回复
            reply = AgentComment.objects.create(
                agent=parent_comment.agent,
                user=request.user,
                content=content,
                parent=parent_comment
            )

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='reply_comment',
                target_id=parent_comment.id,
                target_type='comment',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            # 构建响应数据
            response_data = {
                'replyId': reply.id,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'avatar': request.user.avatar if hasattr(request.user, 'avatar') else None
                },
                'time': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'content': reply.content,
                'likes': 0
            }

            return Response({
                'code': 200,
                'message': '回复提交成功',
                'data': response_data
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'回复提交失败：{str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowledgeBaseLikeView(APIView):
    """知识库点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, kbId):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=int(kbId))
            except (KnowledgeBase.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '知识库不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经点赞
            if kb.likes.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '已经点赞过了'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 添加点赞
            kb.likes.add(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='like_knowledge_base',
                target_id=kb.id,
                target_type='knowledge_base',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '点赞成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'点赞失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, kbId):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=int(kbId))
            except (KnowledgeBase.DoesNotExist, ValueError):
                return Response({
                    'code': 404,
                    'message': '知识库不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经点赞
            if not kb.likes.filter(id=request.user.id).exists():
                return Response({
                    'code': 400,
                    'message': '还没有点赞'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 取消点赞
            kb.likes.remove(request.user)
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unlike_knowledge_base',
                target_id=kb.id,
                target_type='knowledge_base',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return Response({
                'code': 200,
                'message': '取消点赞成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消点赞失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowledgeBaseCommentView(APIView):
    """知识库评论视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, kbId):
        try:
            # 获取知识库
            try:
                kb = KnowledgeBase.objects.get(id=kbId)
            except KnowledgeBase.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '知识库不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取评论内容
            content = request.data.get('content')
            if not content:
                return Response({
                    'code': 400,
                    'message': '评论内容不能为空',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(content) > 500:
                return Response({
                    'code': 400,
                    'message': '评论内容不能超过500个字符',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建评论
            comment = KnowledgeBaseComment.objects.create(
                knowledge_base=kb,
                user=request.user,
                content=content
            )
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='comment_knowledge_base',
                target_id=kb.id,
                target_type='knowledge_base',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            # 构建响应数据
            data = {
                'commentId': comment.id,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'avatar': request.user.avatar if hasattr(request.user, 'avatar') else None
                },
                'time': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'content': comment.content,
                'likes': 0
            }
            
            return Response({
                'code': 200,
                'message': '评论提交成功',
                'data': data
            })
            
        except Exception as e:
            print(f"评论提交失败: {str(e)}")  # 添加错误日志
            return Response({
                'code': 500,
                'message': f'评论提交失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentRestoreView(APIView):
    """智能体恢复视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取智能体ID
            agent_id = request.data.get('agentId')
            if not agent_id:
                return Response({
                    'code': 400,
                    'message': '智能体ID不能为空',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 获取智能体
            try:
                agent = PublishedAgent.objects.get(id=agent_id)
            except PublishedAgent.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '智能体不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查权限（只有创建者可以恢复）
            if agent.creator != request.user:
                return Response({
                    'code': 403,
                    'message': '无权恢复该智能体',
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)

            # 获取智能体详细信息
            data = {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'creator': {
                    'id': agent.creator.id,
                    'username': agent.creator.username,
                    'avatar': agent.creator.avatar if hasattr(agent.creator, 'avatar') else None
                },
                'views': agent.views,
                'likes': agent.likes.count(),
                'followers': agent.followers.count(),
                'isFollowed': request.user in agent.followers.all(),
                'isLiked': request.user in agent.likes.all(),
                'avatar': agent.avatar,
                'modelId': agent.model_id,
                'workflowId': agent.workflow_id,
                'status': agent.status,
                'createdAt': agent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updatedAt': agent.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'knowledgeBases': [
                    {
                        'id': str(kb.id),
                        'name': kb.name,
                        'description': kb.description,
                        'fileCount': kb.files.count() if hasattr(kb, 'files') else 0,
                        'followCount': kb.followers.count(),
                        'isFollowed': request.user in kb.followers.all()
                    } for kb in agent.knowledge_bases.all()
                ],
                'comments': [
                    {
                        'id': str(comment.id),
                        'user': {
                            'id': comment.user.id,
                            'username': comment.user.username,
                            'avatar': comment.user.avatar if hasattr(comment.user, 'avatar') else None
                        },
                        'time': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'content': comment.content,
                        'likes': comment.likes.count(),
                        'replies': [
                            {
                                'id': str(reply.id),
                                'user': {
                                    'id': reply.user.id,
                                    'username': reply.user.username,
                                    'avatar': reply.user.avatar if hasattr(reply.user, 'avatar') else None
                                },
                                'time': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                                'content': reply.content,
                                'likes': reply.likes.count()
                            } for reply in comment.replies.all().order_by('created_at')
                        ]
                    } for comment in agent.agent_comments.filter(parent=None).order_by('-created_at')
                ]
            }

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='restore_agent',
                target_id=agent.id,
                target_type='agent',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '获取智能体信息成功',
                'data': data
            })

        except Exception as e:
            print(f"获取智能体信息失败: {str(e)}")  # 添加错误日志
            return Response({
                'code': 500,
                'message': f'获取智能体信息失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFollowView(APIView):
    """用户关注视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, userId):
        """关注用户"""
        try:
            # 获取目标用户
            try:
                target_user = User.objects.get(id=userId)
            except User.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '用户不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            # 检查是否是自己
            if target_user == request.user:
                return Response({
                    'code': 400,
                    'message': '不能关注自己',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 检查是否已经关注
            if request.user.is_following(target_user):
                return Response({
                    'code': 400,
                    'message': '已经关注过该用户',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 添加关注
            request.user.follow(target_user)

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='follow_user',
                target_id=target_user.id,
                target_type='user',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '关注成功',
                'data': None
            })

        except Exception as e:
            print(f"关注用户失败: {str(e)}")  # 添加错误日志
            return Response({
                'code': 500,
                'message': f'关注用户失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, userId):
        """取消关注用户"""
        try:
            # 获取目标用户
            try:
                target_user = User.objects.get(id=userId)
            except User.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '用户不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                # 取消关注
                request.user.unfollow(target_user)
            except ValueError as e:
                return Response({
                    'code': 400,
                    'message': str(e),
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"取消关注操作失败: {str(e)}")
                return Response({
                    'code': 500,
                    'message': '取消关注失败',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='unfollow_user',
                target_id=target_user.id,
                target_type='user',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return Response({
                'code': 200,
                'message': '已取消关注',
                'data': None
            })

        except Exception as e:
            print(f"取消关注用户失败: {str(e)}")  # 添加错误日志
            return Response({
                'code': 500,
                'message': f'取消关注用户失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AgentDeleteView(APIView):
    """删除智能体视图"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, agent_id):
        try:
            # 获取智能体
            agent = get_object_or_404(PublishedAgent, id=agent_id)
            
            # 验证权限（只能删除自己创建的智能体）
            if agent.creator != request.user:
                return Response({
                    'code': 403,
                    'message': '您没有权限删除此智能体',
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)
                
            # 记录删除前的头像路径（如果有的话）
            avatar_path = None
            if agent.avatar and agent.avatar.startswith('/media/'):
                avatar_path = os.path.join(settings.MEDIA_ROOT, agent.avatar.lstrip('/'))
            
            # 删除智能体
            agent_name = agent.name
            agent.delete()
            
            # 如果有头像文件，也一并删除
            if avatar_path and os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    print(f"删除智能体头像文件失败: {e}")
            
            return Response({
                'code': 200,
                'message': f'智能体 "{agent_name}" 已成功删除',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除智能体失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentDraftView(APIView):
    """智能体草稿保存与获取"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """保存草稿"""
        try:
            data = request.data
            draft_id = data.get('id')
            
            # 如果提供了草稿ID，尝试更新现有草稿
            if draft_id:
                try:
                    draft = AgentDraft.objects.get(id=draft_id, creator=request.user)
                    serializer = AgentDraftSerializer(draft, data=data, partial=True)
                except AgentDraft.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '草稿不存在或无权限'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # 创建新草稿
                serializer = AgentDraftSerializer(data=data)
            
            if serializer.is_valid():
                # 保存基本数据
                draft = serializer.save(creator=request.user)
                
                # 处理知识库关联
                knowledge_bases = data.get('knowledgeBases', [])
                if knowledge_bases:
                    draft.knowledge_bases.set(knowledge_bases)
                
                model_id = data.get('modelId')
                if model_id:
                    draft.model_id = model_id
                    draft.save()
                
                workflow_id = data.get('workflowId')
                if workflow_id:
                    draft.workflow_id = workflow_id
                    draft.save()
                
                # 记录用户行为日志
                UserActionLog.objects.create(
                    user=request.user,
                    action='save_agent_draft',
                    target_id=draft.id,
                    target_type='agent_draft',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                return Response({
                    'code': 200,
                    'message': '草稿保存成功',
                    'data': {
                        'id': draft.id,
                        'name': draft.name,
                        'updated_at': draft.updated_at
                    }
                })
            else:
                return Response({
                    'code': 400,
                    'message': '数据格式错误',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"保存草稿失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'保存失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, draft_id=None):
        """获取草稿列表或单个草稿详情"""
        try:
            # 获取单个草稿详情
            if draft_id:
                try:
                    draft = AgentDraft.objects.get(id=draft_id, creator=request.user)
                    serializer = AgentDraftSerializer(draft)
                    print(serializer.data)
                    return Response({
                        'code': 200,
                        'message': '获取草稿成功',
                        'data': serializer.data
                    })
                except AgentDraft.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '草稿不存在或无权限'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取草稿列表
            else:
                drafts = AgentDraft.objects.filter(creator=request.user)
                serializer = AgentDraftSerializer(drafts, many=True)
                
                return Response({
                    'code': 200,
                    'message': '获取草稿列表成功',
                    'data': serializer.data
                })
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取草稿失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, draft_id):
        """删除草稿"""
        try:
            try:
                draft = AgentDraft.objects.get(id=draft_id, creator=request.user)
            except AgentDraft.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '草稿不存在或无权限'
                }, status=status.HTTP_404_NOT_FOUND)
            
            draft_name = draft.name
            draft.delete()
            
            # 记录用户行为日志
            UserActionLog.objects.create(
                user=request.user,
                action='delete_agent_draft',
                target_id=draft_id,
                target_type='agent_draft',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({
                'code': 200,
                'message': f'草稿 "{draft_name}" 已删除'
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除草稿失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserProfileView(APIView):
    """获取用户个人资料接口"""
    
    def get(self, request, user_id):
        """获取用户详情"""
        try:
            # 查询目标用户
            target_user = User.objects.get(id=user_id)
            
            # 检查当前请求用户是否已登录
            current_user = request.user if request.user.is_authenticated else None
            
            # 统计智能体数量
            agent_count = PublishedAgent.objects.filter(creator=target_user).count()
            
            # 构建响应数据
            user_data = {
                'id': str(target_user.id),
                'username': target_user.username,
                'avatar': target_user.avatar,
                'bio': target_user.bio or "",
                'followersCount': target_user.get_followers_count(),
                'followingCount': target_user.get_following_count(),
                'postsCount': target_user.posts.count() if hasattr(target_user, 'posts') else 0,
                'agentsCount': agent_count,
                'isFollowed': current_user.is_following(target_user) if current_user else False
            }
            
            return Response({
                'code': 200,
                'message': '获取用户信息成功',
                'data': user_data
            })
            
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取用户信息失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserPostsView(APIView):
    """获取用户帖子列表接口"""
    
    def get(self, request, user_id):
        """获取用户发布的帖子"""
        try:
            # 查询目标用户
            target_user = User.objects.get(id=user_id)
            print(target_user)
            
            # 检查当前请求用户是否已登录
            current_user = request.user if request.user.is_authenticated else None
            
            # 获取用户发布的帖子
            posts = Post.objects.filter(user=target_user).order_by('-created_at')
            # 构建响应数据
            print(posts)
            post_list = []
            for post in posts:
                # 检查当前用户是否点赞了该帖子
                is_liked = False
                if current_user:
                    is_liked = post.likes.filter(id=current_user.id).exists() if hasattr(post, 'likes') else False
                
                # 获取评论
                comments = []
                for comment in PostComment.objects.filter(post=post).order_by('-created_at')[:10]:  # 只取前10条评论
                    comments.append({
                        'id': str(comment.id),
                        'content': comment.content,
                        'username': comment.user.username
                    })
                
                # 获取图片
                images = []
                if hasattr(post, 'images'):
                    for image in post.images.all():
                        images.append(image.image.url if hasattr(image, 'image') else '')
                
                post_data = {
                    'id': str(post.id),
                    'title': post.title,
                    'content': post.content,
                    'time': post.created_at.strftime('%Y-%m-%d %H:%M'),
                    'likes': post.likes.count() if hasattr(post, 'likes') else 0,
                    'isLiked': is_liked,
                    'comments': comments,
                    'images': images
                }
                post_list.append(post_data)
            
            return Response({
                'code': 200,
                'message': '获取帖子列表成功',
                'data': post_list
            })
            
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"获取用户帖子失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取用户帖子失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserPublicAgentsView(APIView):
    """获取用户公开智能体列表接口"""
    
    def get(self, request, user_id):
        """获取用户创建的公开智能体列表"""
        try:
            # 查询目标用户
            target_user = User.objects.get(id=user_id)
            
            # 检查当前请求用户是否已登录
            current_user = request.user if request.user.is_authenticated else None
            
            # 获取用户创建的公开智能体列表
            agents = PublishedAgent.objects.filter(
                creator=target_user,
                is_active=True      # 只获取未被禁用的
            )
            
            # 构建响应数据
            agent_list = []
            for agent in agents:
                # 获取关注数量
                follow_count = agent.followers.count() if hasattr(agent, 'followers') else 0
                
                # 检查当前用户是否已关注该智能体
                is_followed = False
                if current_user and hasattr(agent, 'followers'):
                    is_followed = agent.followers.filter(id=current_user.id).exists()
                
                agent_data = {
                    'id': str(agent.id),
                    'name': agent.name,
                    'description': agent.description,
                    'avatar': agent.avatar,
                    'followCount': follow_count,
                    'usageCount': agent.views or 0,  # 可能需要添加一个使用次数字段
                    'isFollowed': is_followed
                }
                agent_list.append(agent_data)
            
            return Response({
                'code': 200,
                'message': '获取智能体列表成功',
                'data': agent_list
            })
            
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"获取用户智能体失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取用户智能体失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserPublicKnowledgeBasesView(APIView):
    """获取用户公开知识库列表接口"""
    
    def get(self, request, user_id):
        """获取用户创建的公开知识库列表"""
        try:
            # 查询目标用户
            target_user = User.objects.get(id=user_id)
            
            # 检查当前请求用户是否已登录
            current_user = request.user if request.user.is_authenticated else None
            
            # 获取用户创建的公开知识库
            knowledge_bases = KnowledgeBase.objects.filter(user=target_user)
            
            # 构建响应数据
            kb_list = []
            for kb in knowledge_bases:
                # 获取关注数量
                follow_count = kb.followers.count() if hasattr(kb, 'followers') else 0
                
                # 检查当前用户是否已关注该知识库
                is_followed = False
                if current_user and hasattr(kb, 'followers'):
                    is_followed = kb.followers.filter(id=current_user.id).exists()
                
                kb_data = {
                    'id': str(kb.id),
                    'name': kb.name,
                    'description': kb.description,
                    'type': kb.type if hasattr(kb, 'type') else 'text',
                    'followCount': follow_count,
                    'fileCount': kb.files.count() if hasattr(kb, 'files') else 0,
                    'isFollowed': is_followed
                }
                kb_list.append(kb_data)
            
            return Response({
                'code': 200,
                'message': '获取知识库列表成功',
                'data': kb_list
            })
            
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"获取用户知识库失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取用户知识库失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostDeleteView(APIView):
    """删除帖子视图"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, postId):
        try:
            # 获取帖子
            post = Post.objects.get(id=postId)
            
            # 验证权限：只有帖子作者可以删除
            if post.user != request.user:
                return Response({
                    'code': 403,
                    'message': '您没有权限删除此帖子'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 删除相关的图片
            post.images.all().delete()
            
            # 删除相关的点赞记录
            PostLike.objects.filter(post=post).delete()
            
            # 删除相关的收藏记录
            PostFavorite.objects.filter(post=post).delete()
            
            # 删除相关的评论
            PostComment.objects.filter(post=post).delete()
            
            # 删除相关的智能体关联
            PostAgent.objects.filter(post=post).delete()
            
            # 删除相关的知识库关联
            PostKnowledgeBase.objects.filter(post=post).delete()
            
            # 记录用户行为
            UserActionLog.objects.create(
                user=request.user,
                action='delete_post',
                target_id=post.id,
                target_type='post',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            # 删除帖子本身
            post.delete()
            
            return Response({
                'code': 200,
                'message': '帖子删除成功',
                'data': None
            })
            
        except Post.DoesNotExist:
            return Response({
                'code': 404,
                'message': '帖子不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除帖子失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)