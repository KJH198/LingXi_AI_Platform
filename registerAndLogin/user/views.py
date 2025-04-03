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