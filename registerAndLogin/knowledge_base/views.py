from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import KnowledgeBase, KnowledgeBaseFile
from .serializers import KnowledgeBaseSerializer, KnowledgeBaseFileSerializer
import os

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
            
            with open(file.file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response({
                "code": 200,
                "data": {
                    "content": content
                }
            })
        except KnowledgeBaseFile.DoesNotExist:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND
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