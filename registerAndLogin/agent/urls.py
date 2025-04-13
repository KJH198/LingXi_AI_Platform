# agents/urls.py
from django.urls import path
from .views import WorkflowSaveView, WorkflowRetrieveView

urlpatterns = [
    path('workflowSave/', WorkflowSaveView.as_view(), name='workflow-save'),
    path('workflowGet/', WorkflowRetrieveView.as_view(), name='workflow-get'),
]