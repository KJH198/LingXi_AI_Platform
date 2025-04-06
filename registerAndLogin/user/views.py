from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json
from .models import User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError

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

        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            email=email
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
                }, status=400)

            # 通过手机号查找用户
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                }, status=401)

            # 验证密码
            if not user.check_password(password):
                return JsonResponse({
                    'success': False,
                    'message': '密码错误'
                }, status=401)

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # 登录用户
            login(request, user)

            return JsonResponse({
                'success': True,
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
def update_user_info(request):
    """
    Update user information.

    Request body may contain:
    - username: The new username of the user.
    - phone_number: The new phone number of the user.
    - email: The new email address of the user.

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
        
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'email' in data:
            user.email = data['email']
            
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
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 返回操作台基本信息
        data = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'banned_users': User.objects.filter(is_active=False).count()
        }
        return Response(data)

class UserManagementView(APIView):
    """用户管理视图"""
    def get(self, request):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 获取所有用户信息
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request, user_id=None):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 根据ID查询单个用户
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 查询所有用户
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
        
        # 封禁用户
        user_id = request.data.get('user_id')
        ban_days = request.data.get('ban_days')  # 7, 10, -1(永久)
        reason = request.data.get('reason', '违反社区规定')
        
        try:
            user = User.objects.get(id=user_id)
            
            # 永久封禁
            if ban_days == -1:
                user.is_active = False
                user.ban_reason = reason
                user.ban_until = None
                user.save()
                return Response({'message': '用户已永久封禁'})
            
            # 临时封禁
            elif ban_days in [7, 10]:
                from datetime import datetime, timedelta
                from django.utils.timezone import make_aware
                
                ban_until = make_aware(datetime.now() + timedelta(days=ban_days))
                user.is_active = False
                user.ban_reason = reason
                user.ban_until = ban_until
                user.save()
                
                # 实际项目中应该使用celery定时任务在ban_until时间解封
                return Response({
                    'message': f'用户已封禁{ban_days}天',
                    'ban_until': ban_until
                })
            
            else:
                return Response({'error': '无效的封禁天数'}, status=status.HTTP_400_BAD_REQUEST)
                
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

class KnowledgeBaseView(APIView):
    """知识库管理"""
    def post(self, request):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        title = request.data.get('title')
        content = request.data.get('content')
        
        # 实际项目中应该保存到知识库模型
        return Response({'message': '知识库创建成功'})

    def delete(self, request, kb_id):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        # 实际项目中应该删除知识库记录
        return Response({'message': '知识库删除成功'})

    def put(self, request, kb_id):
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        content = request.data.get('content')
        # 实际项目中应该更新知识库内容
        return Response({'message': '知识库更新成功'})