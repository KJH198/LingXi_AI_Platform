from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Post, PostImage, PostLike, PostFavorite, PostComment, PostAgent, PostKnowledgeBase
from user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from user.models import PublishedAgent
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
        agents = PublishedAgent.objects.filter(search_condition, is_active=True).order_by('-created_at')
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
        
        # 执行查询(只查询公开的知识库)
        kbs = KnowledgeBase.objects.filter(search_condition).order_by('-created_at')
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


