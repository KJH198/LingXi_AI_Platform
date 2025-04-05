from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from .admin_models import UserBanRecord, AgentRating, KnowledgeBase
from .admin_serializers import (
    UserSerializer, 
    UserBanRecordSerializer,
    AgentRatingSerializer,
    KnowledgeBaseSerializer
)
from datetime import datetime, timedelta

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return Response({"message": "欢迎来到管理员控制台"})

class UserListView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserBanView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        ban_data = {
            'user': user.id,
            'ban_duration': request.data.get('ban_duration'),
            'reason': request.data.get('reason')
        }
        
        serializer = UserBanRecordSerializer(data=ban_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentRatingView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        ratings = AgentRating.objects.all()
        serializer = AgentRatingSerializer(ratings, many=True)
        return Response(serializer.data)

class KnowledgeBaseView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = KnowledgeBaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, kb_id):
        try:
            kb = KnowledgeBase.objects.get(id=kb_id)
            kb.is_deleted = True
            kb.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KnowledgeBase.DoesNotExist:
            return Response({"error": "知识库不存在"}, status=status.HTTP_404_NOT_FOUND)
            
    def put(self, request, kb_id):
        try:
            kb = KnowledgeBase.objects.get(id=kb_id)
            serializer = KnowledgeBaseSerializer(kb, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except KnowledgeBase.DoesNotExist:
            return Response({"error": "知识库不存在"}, status=status.HTTP_404_NOT_FOUND)

class UserBanStatusView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            active_bans = UserBanRecord.objects.filter(
                user=user,
                ban_start__lte=timezone.now(),
                ban_start__gte=timezone.now() - timedelta(days=1000)
            ).exists()
            return Response({"is_banned": active_bans})
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)