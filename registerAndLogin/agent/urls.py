# agents/urls.py
from django.urls import path
from .views import (
    AgentGetInputAndOutputCountView, GetSelectedWorkflowView, WorkflowSaveView, GetWorkflowsView, DeleteWorkflowView,
    WorkflowRetrieveView, GetInputAndOutputCountView, AgentAvatarUploadView,
    CleanupTempResourcesView
)
from .workflow import submit_static_inputs,submit_dynamic_input
from .agent import start_preview, check_next_input

urlpatterns = [
    path('workflowSave/', WorkflowSaveView.as_view(), name='workflow-save'),
    path('workflows/', GetWorkflowsView.as_view(), name='workflow-list'),
    path('workflow/<int:workflow_id>/', GetSelectedWorkflowView.as_view(), name='workflow-list'),
    path('deleteworkflow/<int:workflow_id>', DeleteWorkflowView.as_view(), name='workflow-delete'),
    path('workflowLoad/<int:workflowId>/', WorkflowRetrieveView.as_view(), name='workflow-load'),
    path('staticInputCount/<int:workflow_id>', GetInputAndOutputCountView.as_view(), name='input-num'),  # 处理没有参数的情况
    path('AgentstaticInputCount/<int:agent_id>', AgentGetInputAndOutputCountView.as_view(), name='input-num'),  # 处理没有参数的情况
    path('staticInput', submit_static_inputs, name='submit-static-input'),
    path('staticInput/<int:workflow_id0>', submit_static_inputs, name='submit-static-input'),
    path('dynamicInput', submit_dynamic_input, name='submit-dynamic-input'),
    path('checkNextInput', check_next_input, name='check-next-input'),
    #path('chat', AgentChatView.as_view(), name='agent-chat'),
    path('upload_avatar', AgentAvatarUploadView.as_view(), name='agent-avatar-upload'),
    path('cleanup_temp_resources', CleanupTempResourcesView.as_view(), name='cleanup-temp-resources'),
    path('start_preview/', start_preview, name='start-preview'),
    path('cleanup_temp_resources', CleanupTempResourcesView.as_view(), name='cleanup-temp-resources'),
]