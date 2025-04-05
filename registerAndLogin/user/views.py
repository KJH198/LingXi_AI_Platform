from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json
from .models import User
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
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
    GET: 返回登录页面
    POST: 处理登录请求
    """
    if request.method == 'GET':
        # 返回简单登录表单
        return HttpResponse('''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>用户登录</title>
            </head>
            <body>
            </body>
            </html>
            <form method="post">
                <h2>用户登录</h2>
                <div>
                    <label>手机号:</label>
                    <input type="text" name="phone_number" required>
                </div>
                <div>
                    <label>密码:</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">登录</button>
            </form>
        ''', content_type='text/html')

    elif request.method == 'POST':
        try:
            # 处理表单提交和JSON请求
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

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

class AdminView(ViewSet):
    """
    管理员专用视图
    需要管理员权限才能访问
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """
        获取所有用户信息(管理员专用)
        """
        users = User.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        封禁/解封用户
        请求参数:
        {
            "user_id": 用户ID,
            "ban_type": "7days"/"10days"/"permanent"/"remove"
        }
        """
        serializer = BanUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer.update_ban_status(user)
        return Response({'message': '操作成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        管理员仪表盘数据
        返回:
        - 用户总数
        - 活跃用户数
        - 被封禁用户数
        - 最近7天注册用户数
        """
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        banned_users = User.objects.filter(ban_status__in=['7days', '10days', 'permanent']).count()
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()

        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'banned_users': banned_users,
            'recent_users': recent_users
        })

    @action(detail=False, methods=['get', 'post'])
    def agent_reviews(self, request):
        """
        智能体评价管理
        GET: 获取所有智能体评价
        POST: 删除违规评价
        """
        if request.method == 'GET':
            # 获取所有智能体评价
            reviews = AgentReview.objects.all()
            serializer = AgentReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        # POST请求处理删除评价
        review_id = request.data.get('review_id')
        try:
            review = AgentReview.objects.get(id=review_id)
            review.delete()
            return Response({'message': '评价已删除'})
        except AgentReview.DoesNotExist:
            return Response({'error': '评价不存在'}, status=404)

    @action(detail=False, methods=['get', 'post', 'delete'])
    def knowledge_base(self, request):
        """
        知识库管理
        GET: 获取所有知识库条目
        POST: 创建新知识库条目
        DELETE: 删除知识库条目
        """
        if request.method == 'GET':
            articles = KnowledgeBase.objects.all()
            serializer = KnowledgeBaseSerializer(articles, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = KnowledgeBaseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        
        elif request.method == 'DELETE':
            article_id = request.data.get('article_id')
            try:
                article = KnowledgeBase.objects.get(id=article_id)
                article.delete()
                return Response({'message': '知识库条目已删除'})
            except KnowledgeBase.DoesNotExist:
                return Response({'error': '知识库条目不存在'}, status=404)