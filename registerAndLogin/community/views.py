from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination

from .models import Post, PostImage, PostLike, PostFavorite, PostComment, PostAgent, PostKnowledgeBase
from .serializers import HotAgentSerializer, HotKnowledgeBaseSerializer
from user.models import User, PublishedAgent, AgentDraft
from knowledge_base.models import KnowledgeBase

User = get_user_model()

# Create your views here.

def get_post_list(request):
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    sort = request.GET.get('sort', '1')
    
    # 获取当前用户
    current_user = request.user if request.user.is_authenticated else None
    
    # 基础查询集
    posts = Post.objects.all()
    
    # 根据排序方式处理
    if sort == '1':  # 首页/推荐
        # 这里可以实现推荐算法，暂时按最新排序
        posts = posts.order_by('-created_at')
    elif sort == '2':  # 热门
        # 按点赞数和评论数排序
        posts = posts.order_by('-like_count', '-comment_count', '-created_at')
    elif sort == '3':  # 最新
        posts = posts.order_by('-created_at')
    
    # 分页
    paginator = Paginator(posts, size)
    page_obj = paginator.get_page(page)
    
    # 构建响应数据
    items = []
    for post in page_obj:
        # 获取帖子图片
        images = [image.image_url for image in post.images.all()]
        
        # 获取帖子评论
        comments = []
        for comment in post.postcomment_set.all():
            comments.append({
                'id': comment.id,
                'userId': comment.user.id,
                'username': comment.user.username,
                'avatar': comment.user.avatar,
                'content': comment.content,
                'time': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # 获取关联的智能体
        agents = []
        for post_agent in post.postagent_set.all():
            agent = post_agent.agent
            agents.append({
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'avatar': agent.avatar,
                'creator': {
                    'id': agent.creator.id,
                    'username': agent.creator.username,
                    'avatar': agent.creator.avatar
                },
                'followCount': agent.followers.count() if hasattr(agent, 'followers') else 0,
                'isFollowed': current_user in agent.followers.all() if current_user else False
            })
        
        # 获取关联的知识库
        knowledge_bases = []
        for post_kb in post.postknowledgebase_set.all():
            kb = post_kb.knowledge_base
            knowledge_bases.append({
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'creator': {
                    'id': kb.user.id,
                    'username': kb.user.username,
                    'avatar': kb.user.avatar
                },
                'fileCount': kb.files.count(),
                'followCount': kb.followers.count() if hasattr(kb, 'followers') else 0,
                'isFollowed': current_user in kb.followers.all() if current_user else False
            })
        
        # 检查当前用户是否点赞、收藏、关注
        is_liked = False
        is_favorited = False
        is_followed = False
        if current_user:
            is_liked = PostLike.objects.filter(post=post, user=current_user).exists()
            is_favorited = PostFavorite.objects.filter(post=post, user=current_user).exists()
            is_followed = current_user.following.filter(id=post.user.id).exists()
        
        items.append({
            'id': post.id,
            'userId': post.user.id,
            'username': post.user.username,
            'avatar': post.user.avatar,
            'time': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'title': post.title,
            'content': post.content,
            'images': images,
            'likes': post.like_count,
            'isLiked': is_liked,
            'isFavorited': is_favorited,
            'isFollowed': is_followed,
            'comments': comments,
            'agents': agents,
            'knowledgeBases': knowledge_bases
        })
    
    return JsonResponse({
        'code': 200,
        'data': {
            'items': items,
            'total': paginator.count,
            'page': page,
            'size': size,
            'pageCount': paginator.num_pages
        }
    })

class SearchView(APIView):
    """
    综合搜索视图，支持搜索帖子、用户、智能体和知识库
    """
    
    def get(self, request):
        try:
            # 获取搜索参数
            query = request.query_params.get('q', '').strip()
            search_type = request.query_params.get('type', 'all')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))
            
            # 验证参数
            if not query:
                return Response({
                    'code': 400,
                    'message': '搜索关键词不能为空',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 计算分页参数
            offset = (page - 1) * size
            limit = offset + size
            
            # 获取当前用户(用于检查关注状态)
            current_user = request.user if request.user.is_authenticated else None
            
            result = {}
            
            # 根据搜索类型执行不同的搜索
            if search_type == 'all' or search_type == 'posts':
                posts_data = self._search_posts(query, offset, limit, current_user)
                if search_type == 'all':
                    result['posts'] = posts_data
                else:
                    result = posts_data
                    
            if search_type == 'all' or search_type == 'users':
                users_data = self._search_users(query, offset, limit, current_user)
                if search_type == 'all':
                    result['users'] = users_data
                else:
                    result = users_data
                    
            if search_type == 'all' or search_type == 'agents':
                agents_data = self._search_agents(query, offset, limit, current_user)
                if search_type == 'all':
                    result['agents'] = agents_data
                else:
                    result = agents_data
                    
            if search_type == 'all' or search_type == 'kb':
                kb_data = self._search_knowledge_bases(query, offset, limit, current_user)
                if search_type == 'all':
                    result['kb'] = kb_data
                else:
                    result = kb_data
                    
            return Response({
                'code': 200,
                'message': 'success',
                'data': result
            })
            
        except ValueError as e:
            return Response({
                'code': 400,
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f"搜索错误详情: {str(e)}")
            traceback.print_exc()  # 打印完整的错误堆栈
            return Response({
                'code': 500,
                'message': f'搜索失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _search_posts(self, query, offset, limit, current_user):
        """搜索帖子"""
        # 构建搜索条件
        search_condition = Q(title__icontains=query) | Q(content__icontains=query)
        
        # 执行查询(只查询审核通过的帖子)
        posts = Post.objects.filter(search_condition)
        # 如果有状态字段，添加过滤
        if 'status' in [field.name for field in Post._meta.fields]:
            posts = posts.filter(status='active')  # Post模型中状态默认值为'active'
        
        posts = posts.order_by('-created_at')
        total = posts.count()
        posts = posts[offset:limit]
        
        # 格式化结果
        items = []
        for post in posts:
            # 检查当前用户是否点赞
            is_liked = False
            if current_user:
                is_liked = PostLike.objects.filter(post=post, user=current_user).exists()
            
            # 获取评论 - 使用正确的模型名称
            formatted_comments = []
            post_comments = post.postcomment_set.all()[:3]  # 使用正确的反向关系名
            for comment in post_comments:
                formatted_comments.append({
                    'id': comment.id,
                    'content': comment.content[:100],  # 截取前100个字符
                    'username': comment.user.username
                })
            
            # 获取图片URLs - 正确地从关系管理器获取
            images = [image.image_url for image in post.images.all()]
            
            # 添加帖子到结果列表 - 修正字段名称
            items.append({
                'id': post.id,
                'userId': post.user.id,  # 使用正确的字段名 user 而不是 creator
                'username': post.user.username,
                'avatar': post.user.avatar if hasattr(post.user, 'avatar') else None,
                'time': post.created_at.strftime('%Y-%m-%d %H:%M'),
                'title': post.title,
                'content': post.content[:200],  # 截取前200个字符
                'images': images,
                'likes': post.like_count,  # 使用正确的字段名 like_count 而不是 likes_count
                'comments': formatted_comments,
                'isLiked': is_liked
            })
        
        return {
            'items': items,
            'total': total
        }
    
    def _search_users(self, query, offset, limit, current_user):
        """搜索用户"""
        try:
            # 构建搜索条件
            search_condition = Q(username__icontains=query)
            if hasattr(User, 'bio'):
                search_condition |= Q(bio__icontains=query)
            
            # 执行查询(只查询活跃的用户)
            users = User.objects.filter(search_condition, is_active=True).order_by('-created_at')
            total = users.count()
            users = users[offset:limit]
            
            # 格式化结果
            items = []
            for user in users:
                # 检查当前用户是否关注
                is_followed = False
                if current_user and hasattr(current_user, 'following'):
                    is_followed = current_user.following.filter(id=user.id).exists()
                
                # 获取粉丝数量
                followers_count = user.followers.count() if hasattr(user, 'followers') else 0
                
                # 修复这里: 使用正确的字段名 'user' 而不是 'creator'
                posts_count = Post.objects.filter(user=user).count()
                
                # 获取智能体数量
                agents_count = PublishedAgent.objects.filter(creator=user).count()
                # 只统计已审核通过的智能体
                if 'status' in [f.name for f in PublishedAgent._meta.fields]:
                    agents_count = PublishedAgent.objects.filter(creator=user, status='approved').count()
                
                items.append({
                    'id': user.id,
                    'username': user.username,
                    'avatar': user.avatar if hasattr(user, 'avatar') else None,
                    'bio': user.bio if hasattr(user, 'bio') else None,
                    'followersCount': followers_count,
                    'followingCount': user.following.count() if hasattr(user, 'following') else 0,
                    'postsCount': posts_count,
                    'agentsCount': agents_count,
                    'isFollowed': is_followed
                })
            
            return {
                'items': items,
                'total': total
            }
        except Exception as e:
            # 添加详细的错误日志
            import traceback
            print(f"搜索用户错误: {str(e)}")
            traceback.print_exc() 
            return {
                'items': [],
                'total': 0
            }
    
    def _search_agents(self, query, offset, limit, current_user):
        """搜索智能体"""
        # 构建搜索条件
        search_condition = Q(name__icontains=query) | Q(description__icontains=query)
        
        # 执行查询(只查询审核通过的智能体)
        agents = PublishedAgent.objects.filter(search_condition, status='approved').order_by('-created_at')
        print(f"搜索智能体: {query}, 条件: {search_condition}, 数量: {agents.count()}")
        total = agents.count()
        agents = agents[offset:limit]
        
        # 格式化结果
        items = []
        for agent in agents:
            # 检查当前用户是否关注
            is_followed = False
            if current_user and hasattr(agent, 'followers'):
                is_followed = agent.followers.filter(id=current_user.id).exists()
            
            # 获取关注数量
            follow_count = agent.followers.count() if hasattr(agent, 'followers') else 0
            
            items.append({
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description[:200],  # 截取前200个字符
                'avatar': agent.avatar if agent.avatar else None,
                'creator': {
                    'id': agent.creator.id,
                    'username': agent.creator.username,
                    'avatar': agent.creator.avatar if hasattr(agent.creator, 'avatar') else None
                },
                'followCount': follow_count,
                'isFollowed': is_followed
            })
        
        return {
            'items': items,
            'total': total
        }
    
    def _search_knowledge_bases(self, query, offset, limit, current_user):
        """搜索知识库"""
        # 构建搜索条件
        search_condition = Q(name__icontains=query) | Q(description__icontains=query)
        
        # 执行查询
        kbs = KnowledgeBase.objects.filter(search_condition, status='approved').order_by('-created_at')
        total = kbs.count()
        kbs = kbs[offset:limit]
        
        # 格式化结果
        items = []
        for kb in kbs:
            # 检查当前用户是否关注
            is_followed = False
            if current_user and hasattr(kb, 'followers'):
                is_followed = kb.followers.filter(id=current_user.id).exists()
            
            # 获取关注数量
            follow_count = kb.followers.count() if hasattr(kb, 'followers') else 0
            
            # 获取文件数量
            file_count = kb.files.count() if hasattr(kb, 'files') else 0
            
            items.append({
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description[:200],  # 截取前200个字符
                'creator': {
                    'id': kb.user.id,
                    'username': kb.user.username,
                    'avatar': kb.user.avatar if hasattr(kb.user, 'avatar') else None
                },
                'fileCount': file_count,
                'followCount': follow_count,
                'isFollowed': is_followed
            })
        
        return {
            'items': items,
            'total': total
        }

class HotItemsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100

# 热门智能体视图
class HotAgentsView(generics.ListAPIView):
    serializer_class = HotAgentSerializer
    pagination_class = HotItemsPagination
    
    def get_queryset(self):
        # 只获取已审核通过的智能体
        return PublishedAgent.objects.filter(
            status='approved'
        ).annotate(
            # 计算热度分数：浏览量 + 点赞数*2 + 关注者数*4
            popularity_score=F('views') + Count('likes')*2 + Count('followers')*4
        ).order_by('-popularity_score', '-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            # 标记当前用户是否已关注
            user = request.user
            if user.is_authenticated:
                for agent in page:
                    agent.is_followed = agent.followers.filter(id=user.id).exists()
            
            serializer = self.get_serializer(page, many=True)
            return Response({
                "code": 200,
                "message": "success",
                "data": {
                    "items": serializer.data,
                    "total": self.paginator.page.paginator.count
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "success",
            "data": {
                "items": serializer.data,
                "total": len(serializer.data)
            }
        })

# 开源智能体视图
class OpenAgentsView(generics.ListAPIView):
    serializer_class = HotAgentSerializer
    pagination_class = HotItemsPagination
    
    def get_queryset(self):
        # 只获取已审核通过的智能体
        return PublishedAgent.objects.filter(
            status='approved', is_OpenSource=True
        ).annotate(
            # 计算热度分数：浏览量 + 点赞数*2 + 关注者数*4
            popularity_score=F('views') + Count('likes')*2 + Count('followers')*4
        ).order_by('-popularity_score', '-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            # 标记当前用户是否已关注
            user = request.user
            if user.is_authenticated:
                for agent in page:
                    agent.is_followed = agent.followers.filter(id=user.id).exists()
            
            serializer = self.get_serializer(page, many=True)
            return Response({
                "code": 200,
                "message": "success",
                "data": {
                    "items": serializer.data,
                    "total": self.paginator.page.paginator.count
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "success",
            "data": {
                "items": serializer.data,
                "total": len(serializer.data)
            }
        })

# 热门知识库视图
class HotKnowledgeBasesView(generics.ListAPIView):
    serializer_class = HotKnowledgeBaseSerializer
    pagination_class = HotItemsPagination
    
    def get_queryset(self):
        # 热门知识库排序逻辑
        return KnowledgeBase.objects.filter(
            status='approved'  # 只获取已审核通过的知识库
        ).annotate(
            # 文件数量
            file_count=Count('files'),
            # 关注者数量
            follower_count=Count('followers'),
            # 计算热度分数
            popularity_score=Count('followers')*2 + Count('likes')*4
        ).order_by('-popularity_score', '-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            # 标记当前用户是否已关注
            user = request.user
            if user.is_authenticated:
                for kb in page:
                    kb.is_followed = kb.followers.filter(id=user.id).exists()
            
            serializer = self.get_serializer(page, many=True)
            return Response({
                "code": 200,
                "message": "success",
                "data": {
                    "items": serializer.data,
                    "total": self.paginator.page.paginator.count
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "success",
            "data": {
                "items": serializer.data,
                "total": len(serializer.data)
            }
        })

class PostDetailView(APIView):
    """帖子详情视图"""
    
    def get(self, request, post_id):
        try:
            # 获取帖子对象
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '帖子不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 增加浏览量
            post.view_count += 1
            post.save(update_fields=['view_count'])
            
            # 获取当前用户
            current_user = request.user if request.user.is_authenticated else None
            
            # 检查用户是否点赞、收藏
            is_liked = False
            is_favorited = False
            
            if current_user:
                is_liked = PostLike.objects.filter(post=post, user=current_user).exists()
                is_favorited = PostFavorite.objects.filter(post=post, user=current_user).exists()
            
            # 获取帖子图片
            images = [image.image_url for image in post.images.all()]
            
            # 获取帖子评论
            comments = []
            for comment in PostComment.objects.filter(post=post).order_by('-created_at'):
                comments.append({
                    'id': comment.id,
                    'userId': comment.user.id,
                    'username': comment.user.username,
                    'avatar': comment.user.avatar if hasattr(comment.user, 'avatar') else None,
                    'content': comment.content,
                    'time': comment.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            # 获取关联的智能体
            agents = []
            for post_agent in PostAgent.objects.filter(post=post):
                agent = post_agent.agent
                is_agent_followed = False
                if current_user and hasattr(agent, 'followers'):
                    is_agent_followed = agent.followers.filter(id=current_user.id).exists()
                
                agents.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'description': agent.description,
                    'avatar': agent.avatar,
                    'creator': {
                        'id': agent.creator.id,
                        'username': agent.creator.username,
                        'avatar': agent.creator.avatar if hasattr(agent.creator, 'avatar') else None
                    },
                    'followCount': agent.followers.count() if hasattr(agent, 'followers') else 0,
                    'isFollowed': is_agent_followed
                })
            
            # 获取关联的知识库
            knowledge_bases = []
            for post_kb in PostKnowledgeBase.objects.filter(post=post):
                kb = post_kb.knowledge_base
                is_kb_followed = False
                if current_user and hasattr(kb, 'followers'):
                    is_kb_followed = kb.followers.filter(id=current_user.id).exists()
                
                knowledge_bases.append({
                    'id': str(kb.id),
                    'name': kb.name,
                    'description': kb.description,
                    'creator': {
                        'id': kb.user.id,
                        'username': kb.user.username,
                        'avatar': kb.user.avatar if hasattr(kb.user, 'avatar') else None
                    },
                    'fileCount': kb.files.count() if hasattr(kb, 'files') else 0,
                    'followCount': kb.followers.count() if hasattr(kb, 'followers') else 0,
                    'isFollowed': is_kb_followed
                })
            
            # 获取作者信息
            author = {
                'id': post.user.id,
                'username': post.user.username,
                'avatar': post.user.avatar if hasattr(post.user, 'avatar') else None,
                'bio': post.user.bio if hasattr(post.user, 'bio') else None
            }
            
            # 检查当前用户是否关注了作者
            is_author_followed = False
            if current_user and hasattr(current_user, 'following'):
                is_author_followed = current_user.following.filter(id=post.user.id).exists()
            
            # 构建响应数据
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'time': post.created_at.strftime('%Y-%m-%d %H:%M'),
                'updateTime': post.updated_at.strftime('%Y-%m-%d %H:%M'),
                'author': author,
                'isAuthorFollowed': is_author_followed,
                'images': images,
                'likes': post.like_count,
                'favorites': post.favorite_count,
                'comments': comments,
                'commentCount': post.comment_count,
                'viewCount': post.view_count,
                'isLiked': is_liked,
                'isFavorited': is_favorited,
                'agents': agents,
                'knowledgeBases': knowledge_bases
            }
            
            return Response({
                'code': 200,
                'message': '获取帖子详情成功',
                'data': post_data
            })
            
        except Exception as e:
            # 输出详细错误信息
            import traceback
            print(f"获取帖子详情失败: {str(e)}")
            traceback.print_exc()
            
            return Response({
                'code': 500,
                'message': f'获取帖子详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostCommentsView(APIView):
    """帖子评论列表视图"""
    
    def get(self, request, post_id):
        try:
            # 获取帖子
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '帖子不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取分页参数
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 20))
            
            # 计算偏移量
            offset = (page - 1) * size
            limit = offset + size
            
            # 获取评论
            comments = PostComment.objects.filter(post=post).order_by('-created_at')
            total = comments.count()
            comments = comments[offset:limit]
            
            # 格式化评论数据
            items = []
            for comment in comments:
                items.append({
                    'id': comment.id,
                    'userId': comment.user.id,
                    'username': comment.user.username,
                    'avatar': comment.user.avatar if hasattr(comment.user, 'avatar') else None,
                    'content': comment.content,
                    'time': comment.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            return Response({
                'code': 200,
                'message': '获取评论成功',
                'data': {
                    'items': items,
                    'total': total
                }
            })
            
        except Exception as e:
            import traceback
            print(f"获取帖子评论失败: {str(e)}")
            traceback.print_exc()
            
            return Response({
                'code': 500,
                'message': f'获取帖子评论失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRecentEditedView(APIView):
    """获取用户最近编辑的内容"""
    def get(self, request):
        try:
            # 获取查询参数
            limit = int(request.query_params.get('limit', 5))
            
            # 获取最近编辑的智能体
            recent_agents = []
            # 获取最近编辑的发布智能体
            user_agents = PublishedAgent.objects.filter(
                creator=request.user
            ).order_by('-updated_at')[:limit]
            
            for agent in user_agents:
                recent_agents.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'type': 'agent',
                    'isDraft': False,
                    'lastEditTime': agent.updated_at.strftime('%Y-%m-%d %H:%M')
                })
            
            # 获取最近编辑的智能体草稿
            user_drafts = AgentDraft.objects.filter(
                creator=request.user
            ).order_by('-updated_at')[:limit]
            
            for draft in user_drafts:
                recent_agents.append({
                    'id': str(draft.id),
                    'name': draft.name or '未命名智能体',
                    'type': 'agent',
                    'isDraft': True,
                    'lastEditTime': draft.updated_at.strftime('%Y-%m-%d %H:%M')
                })
            
            # 获取最近编辑的知识库
            user_kbs = KnowledgeBase.objects.filter(
                user=request.user,status='approved'  # 只获取已审核通过的知识库
            ).order_by('-updated_at' if hasattr(KnowledgeBase, 'updated_at') else '-created_at')[:limit]
            
            for kb in user_kbs:
                recent_agents.append({
                    'id': str(kb.id),
                    'name': kb.name,
                    'type': 'kb',
                    'lastEditTime': (kb.updated_at if hasattr(kb, 'updated_at') else kb.created_at).strftime('%Y-%m-%d %H:%M')
                })
            
            # 按最近编辑时间排序并限制返回数量
            from operator import itemgetter
            sorted_items = sorted(recent_agents, key=lambda x: x['lastEditTime'], reverse=True)[:limit]
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': sorted_items
            })
            
        except Exception as e:
            print(f"获取最近编辑内容失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取最近编辑内容失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserFavoritePostsView(APIView):
    """获取用户收藏的帖子列表"""
    def get(self, request):
        try:
            # 获取查询参数
            limit = int(request.query_params.get('limit', 10))
            
            # 获取用户收藏的帖子
            # 通过PostFavorite模型查询，按收藏时间倒序排列
            favorites = PostFavorite.objects.filter(
                user=request.user
            ).select_related('post').order_by('-created_at')[:limit]
            
            # 构建响应数据
            post_list = []
            for favorite in favorites:
                post = favorite.post
                post_list.append({
                    'id': post.id,
                    'title': post.title,
                    'favoriteTime': favorite.created_at.strftime('%Y-%m-%d'),
                    'content': post.content[:100],  # 截取前100个字符作为预览
                    'authorId': post.user.id,
                    'authorName': post.user.username,
                    'likeCount': post.like_count,
                    'commentCount': post.comment_count,
                })
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': post_list
            })
            
        except ValueError as e:
            return Response({
                'code': 400,
                'message': f'参数错误: {str(e)}',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 详细记录错误信息
            import traceback
            print(f"获取收藏帖子失败: {str(e)}")
            traceback.print_exc()
            
            return Response({
                'code': 500,
                'message': f'获取收藏帖子失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)