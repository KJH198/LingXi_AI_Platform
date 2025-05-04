from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Post, PostImage, PostLike, PostFavorite, PostComment, PostAgent, PostKnowledgeBase
from user.models import User

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


