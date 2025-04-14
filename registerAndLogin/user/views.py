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
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings
import time

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
                })

            # 通过手机号查找用户
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })

            # 验证密码
            if not user.check_password(password):
                return JsonResponse({
                    'success': False,
                    'message': '密码错误'
                })

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # 登录用户
            login(request, user)

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
    """用户管理视图，提供以下功能：
    1. 获取用户列表及统计信息
    2. 获取单个用户详情
    3. 封禁用户
    4. 解封用户
    """
    def get(self, request, user_id=None):
        # 验证管理员权限
        if not request.user.is_staff:
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
        serializer = UserSerializer(users, many=True)
        
        return Response({
            'users': serializer.data,
            'total': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'banned_users': User.objects.filter(is_active=False).count(),
            'message': '获取用户列表成功'
        })

    def post(self, request):
        """封禁用户"""
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', '违反社区规定')
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.ban_reason = reason
            user.save()
            
            return Response({
                'success': True,
                'message': '用户封禁成功'
            })
            
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """解封用户"""
        # 验证管理员权限
        if not request.user.is_staff:
            return Response({'error': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.ban_reason = None
            user.ban_until = None
            user.save()
            
            return Response({
                'success': True,
                'message': '用户解封成功'
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

            # 验证当前用户ID是否匹配
            if request.user.id != user_id:
                return Response({
                    'success': False,
                    'message': '无权操作其他用户的关注'
                }, status=status.HTTP_403_FORBIDDEN)

            # 获取目标用户ID
            target_user_id = request.data.get('target_user_id')
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

            # 验证当前用户ID是否匹配
            if request.user.id != user_id:
                return Response({
                    'success': False,
                    'message': '无权操作其他用户的关注'
                }, status=status.HTTP_403_FORBIDDEN)

            # 获取目标用户ID
            target_user_id = request.data.get('target_user_id')
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