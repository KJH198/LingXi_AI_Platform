# agents/urls.py
from django.urls import path
from .views import WorkflowSaveView, GetWorkflowsView, DeleteWorkflowView, WorkflowRetrieveView, GetInputCountView
from .node import submit_static_inputs,submit_dynamic_input

urlpatterns = [
    path('workflowSave/', WorkflowSaveView.as_view(), name='workflow-save'),
    path('workflows/', GetWorkflowsView.as_view(), name='workflow-list'),
    path('deleteworkflow/<int:workflow_id>', DeleteWorkflowView.as_view(), name='workflow-delete'),
    path('workflowLoad/<int:workflowId>/', WorkflowRetrieveView.as_view(), name='workflow-load'),
    path('staticInputCount/<int:workflow_id>', GetInputCountView.as_view(), name='input-num'),  # 处理没有参数的情况
    path('staticInput', submit_static_inputs, name='submit-static-input'),
    path('dynamicInput', submit_dynamic_input, name='submit-dynamic-input'),
    #path('chat', AgentChatView.as_view(), name='agent-chat'),
]