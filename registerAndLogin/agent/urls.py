# agents/urls.py
from django.urls import path
from .views import WorkflowSaveView, GetWorkflowsView, DeleteWorkflowView, WorkflowRetrieveView

urlpatterns = [
    path('workflowSave/', WorkflowSaveView.as_view(), name='workflow-save'),
    path('workflows/', GetWorkflowsView.as_view(), name='workflow-list'),
    path('deleteworkflow/<int:workflow_id>', DeleteWorkflowView.as_view(), name='workflow-delete'),
    path('workflowLoad/<int:workflowId>/', WorkflowRetrieveView.as_view(), name='workflow-load'),

]