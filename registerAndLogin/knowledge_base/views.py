from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import KnowledgeBase, KnowledgeBaseFile
from .serializers import KnowledgeBaseSerializer, KnowledgeBaseFileSerializer

class KnowledgeBaseListView(generics.ListAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KnowledgeBase.objects.filter(user=self.request.user)

class KnowledgeBaseCreateView(generics.CreateAPIView):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class KnowledgeBaseUploadView(generics.CreateAPIView):
    serializer_class = KnowledgeBaseFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        knowledge_base_id = kwargs.get('knowledgeBaseId')
        try:
            knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id, user=request.user)
        except KnowledgeBase.DoesNotExist:
            return Response(
                {"error": "Knowledge base not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        files = request.FILES.getlist('files')
        if not files:
            return Response(
                {"error": "No files provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_files = []
        for file in files:
            serializer = self.get_serializer(data={'file': file, 'knowledge_base': knowledge_base.id})
            if serializer.is_valid():
                serializer.save()
                created_files.append(serializer.data)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(created_files, status=status.HTTP_201_CREATED)

class KnowledgeBaseDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        kb_id = kwargs.get('kb_id')
        try:
            knowledge_base = KnowledgeBase.objects.get(id=kb_id, user=request.user)
            knowledge_base.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KnowledgeBase.DoesNotExist:
            return Response(
                {"error": "Knowledge base not found"},
                status=status.HTTP_404_NOT_FOUND
            ) 