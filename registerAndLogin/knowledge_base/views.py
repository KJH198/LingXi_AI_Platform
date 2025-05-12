from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
from .models import KnowledgeBase, KnowledgeBaseFile
from .serializers import KnowledgeBaseSerializer, KnowledgeBaseFileSerializer
import os
import requests
from bs4 import BeautifulSoup
import uuid
from urllib.parse import urlparse
import mimetypes

# 添加分页类
class KnowledgeBasePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'size'
    max_page_size = 100

class KnowledgeBaseListView(generics.ListAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KnowledgeBase.objects.filter(user=self.request.user)

class KnowledgeBaseCreateView(generics.CreateAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "code": 400,
            "message": "创建失败",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class KnowledgeBaseDetailView(generics.RetrieveAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        knowledge_base_id = self.kwargs.get('knowledgeBaseId')
        return get_object_or_404(KnowledgeBase, id=knowledge_base_id, user=self.request.user)

class KnowledgeBaseUploadView(generics.CreateAPIView):
    serializer_class = KnowledgeBaseFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        knowledge_base_id = kwargs.get('knowledgeBaseId')
        try:
            knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id, user=request.user)
        except KnowledgeBase.DoesNotExist:
            return Response({
                "code": 404,
                "message": "知识库不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('files')
        if not files:
            return Response({
                "code": 400,
                "message": "请选择要上传的文件"
            }, status=status.HTTP_400_BAD_REQUEST)

        created_files = []
        errors = []
        for file in files:
            serializer = self.get_serializer(data={
                'file': file,
                'knowledge_base': knowledge_base.id,
                'filename': file.name,
                'size': file.size
            })
            if serializer.is_valid():
                serializer.save()
                created_files.append(serializer.data)
            else:
                errors.append({
                    "filename": file.name,
                    "errors": serializer.errors
                })

        if errors:
            return Response({
                "code": 400,
                "message": "部分文件上传失败",
                "errors": errors,
                "success_files": created_files
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "code": 201,
            "message": "文件上传成功",
            "data": created_files
        }, status=status.HTTP_201_CREATED)

class KnowledgeBaseDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        kb_id = kwargs.get('knowledgeBaseId')
        try:
            knowledge_base = KnowledgeBase.objects.get(id=kb_id, user=request.user)
            knowledge_base.delete()
            return Response({
                "code": 200,
                "message": "删除成功"
            }, status=status.HTTP_200_OK)
        except KnowledgeBase.DoesNotExist:
            return Response(
                {"error": "Knowledge base not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class FileContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, knowledgeBaseId, fileId):
        try:
            file = KnowledgeBaseFile.objects.get(
                id=fileId,
                knowledge_base_id=knowledgeBaseId,
                knowledge_base__user=request.user
            )
            
            if not os.path.exists(file.file.path):
                return Response(
                    {"error": "File not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取文件名和MIME类型
            file_name = os.path.basename(file.file.path)
            content_type, encoding = mimetypes.guess_type(file.file.path)
            
            # 如果无法确定类型，使用通用二进制类型
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # 打开文件并准备响应
            response = FileResponse(
                open(file.file.path, 'rb'),
                content_type=content_type
            )
            
            # 设置内容处理方式：inline表示在浏览器中打开
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            
            # 如果是大文件，可以设置分块传输
            if os.path.getsize(file.file.path) > 1024 * 1024 * 5:  # 5MB
                response['Transfer-Encoding'] = 'chunked'
            
            return response
            
        except KnowledgeBaseFile.DoesNotExist:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error accessing file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FileDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, knowledgeBaseId, fileId):
        try:
            file = KnowledgeBaseFile.objects.get(
                id=fileId,
                knowledge_base_id=knowledgeBaseId,
                knowledge_base__user=request.user
            )
            file.delete()
            return Response({
                "code": 200,
                "message": "文件删除成功"
            }, status=status.HTTP_200_OK)
        except KnowledgeBaseFile.DoesNotExist:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND
            )

# 添加用户知识库列表视图
class MyKnowledgeBaseListView(generics.ListAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = KnowledgeBasePagination

    def get_queryset(self):
        # 获取用户所有知识库，并附加文件数量统计
        return KnowledgeBase.objects.filter(user=self.request.user).annotate(
            file_count=Count('files')
        ).order_by('-created_at')  # 最新创建的排在前面

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                "code": 200,
                "message": "成功",
                "data": {
                    "items": serializer.data,
                    "total": self.paginator.page.paginator.count
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "成功",
            "data": {
                "items": serializer.data,
                "total": len(serializer.data)
            }
        })

class KnowledgeBaseUrlUploadView(APIView):
    """URL 上传到知识库"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, knowledgeBaseId):
        try:
            # 验证知识库存在并且用户有权限
            try:
                knowledge_base = KnowledgeBase.objects.get(id=knowledgeBaseId)
                if knowledge_base.user != request.user:
                    return Response({
                        'code': 403,
                        'message': '您没有权限上传到该知识库',
                        'data': None
                    }, status=status.HTTP_403_FORBIDDEN)
            except KnowledgeBase.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '知识库不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 验证知识库类型
            if knowledge_base.type != 'text':
                return Response({
                    'code': 400,
                    'message': 'URL 上传仅支持文本知识库',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取 URLs 和处理方式
            urls = request.data.get('urls', [])
            process_type = request.data.get('processType', 'auto')  # 'auto', 'webpage', 'file'
            
            if not urls or not isinstance(urls, list):
                return Response({
                    'code': 400,
                    'message': '请提供至少一个有效的 URL',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理每个 URL
            processed_files = []
            failed_urls = []
            
            for url in urls:
                try:
                    # 验证 URL 格式
                    parsed_url = urlparse(url)
                    if not parsed_url.scheme or not parsed_url.netloc:
                        failed_urls.append({
                            'url': url,
                            'error': '无效的 URL 格式'
                        })
                        continue
                    
                    # 发送 HEAD 请求检查资源类型
                    try:
                        head_response = requests.head(url, timeout=10, allow_redirects=True)
                        content_type = head_response.headers.get('Content-Type', '')
                    except:
                        # 如果 HEAD 请求失败，使用 GET 请求尝试
                        content_type = ''
                    
                    # 确定处理方式
                    if process_type == 'auto':
                        # 自动判断：如果是 HTML 或文本类型，处理为网页；否则处理为文件
                        if 'text/html' in content_type or 'text/plain' in content_type:
                            current_process = 'webpage'
                        else:
                            current_process = 'file'
                    else:
                        current_process = process_type
                    
                    # 根据处理方式执行不同的逻辑
                    if current_process == 'webpage':
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        }
                        
                        response = requests.get(url, headers=headers, timeout=30)
                        response.raise_for_status()
                        
                        # 解析网页内容
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        title = "未知标题"
                        title_tag = soup.find('title')
                        if title_tag and title_tag.text:
                            title = title_tag.text.strip()
                        elif soup.find('h1'):
                            title = soup.find('h1').get_text().strip()
                        
                        title = title[:100] if len(title) > 100 else title
                        
                        sanitized_title = ''.join(c for c in title if c.isalnum() or c in ' -_.')[:50]
                        if not sanitized_title or sanitized_title.isspace():
                            sanitized_title = f"webpage_{uuid.uuid4().hex[:8]}"
                        filename = f"{sanitized_title}.txt"
                        
                        meta_description = ""
                        meta_tag = soup.find('meta', attrs={'name': 'description'})
                        if meta_tag:
                            meta_description = meta_tag.get('content', '')
                        
                        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                            element.decompose()
                        
                        main_content = ""
                        main_elements = soup.select('article, .article, .content, .post, main, #content, .post-content')
                        
                        if main_elements:
                            main_content = main_elements[0].get_text(separator='\n', strip=True)
                        else:
                            main_content = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
                        
                        content = f"""URL: {url}
标题: {title}
描述: {meta_description}
日期: {response.headers.get('Last-Modified', '未知')}
内容:
{main_content}
"""
                        
                        print(f"处理URL: {url}")
                        print(f"提取到的标题: {title}")
                        print(f"内容长度: {len(main_content)} 字符")
                        
                        file_path = f"knowledge_base/{knowledge_base.id}/{filename}"
                        path = default_storage.save(file_path, ContentFile(content.encode('utf-8')))
                        
                        file_record = KnowledgeBaseFile.objects.create(
                            knowledge_base=knowledge_base,
                            filename=filename,
                            file=path,
                            size=len(content),
                            status='processed'
                        )
                        
                        processed_files.append({
                            'id': str(file_record.id),
                            'filename': filename,
                            'size': file_record.size,
                            'processType': current_process
                        })
                    
                    else:
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        
                        content_disposition = response.headers.get('Content-Disposition')
                        if content_disposition and 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"\'')
                        else:
                            path = parsed_url.path
                            filename = os.path.basename(path)
                            if not filename:
                                filename = f"file_{uuid.uuid4().hex[:8]}"
                            
                            if 'pdf' in content_type:
                                if not filename.endswith('.pdf'):
                                    filename += '.pdf'
                            elif 'text/plain' in content_type:
                                if not filename.endswith('.txt'):
                                    filename += '.txt'
                            elif 'application/msword' in content_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                                if not filename.endswith('.docx') and not filename.endswith('.doc'):
                                    filename += '.docx'
                            elif 'text/markdown' in content_type:
                                if not filename.endswith('.md'):
                                    filename += '.md'
                            else:
                                if '.' not in filename:
                                    filename += '.txt'
                        
                        max_size = 10 * 1024 * 1024
                        if len(response.content) > max_size:
                            failed_urls.append({
                                'url': url,
                                'error': '文件大小超过 10MB 限制'
                            })
                            continue
                        
                        file_path = f"knowledge_base/{knowledge_base.id}/{filename}"
                        path = default_storage.save(file_path, ContentFile(response.content))
                        
                        file_record = KnowledgeBaseFile.objects.create(
                            knowledge_base=knowledge_base,
                            filename=filename,
                            file=path,
                            size=len(response.content),
                            status='pending'
                        )
                    
                        processed_files.append({
                            'id': str(file_record.id),
                            'filename': filename,
                            'size': file_record.size,
                            'processType': current_process
                        })
                    
                except Exception as e:
                    import traceback
                    print(f"处理URL失败: {url}")
                    traceback.print_exc()
                    failed_urls.append({
                        'url': url,
                        'error': str(e)
                    })
            
            return Response({
                'code': 200,
                'message': f'成功处理 {len(processed_files)} 个 URL，失败 {len(failed_urls)} 个',
                'data': {
                    'processed_files': processed_files,
                    'failed_urls': failed_urls
                }
            })
            
        except Exception as e:
            import traceback
            print(f"处理 URL 上传失败: {str(e)}")
            traceback.print_exc()
            
            return Response({
                'code': 500,
                'message': f'处理 URL 上传失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)