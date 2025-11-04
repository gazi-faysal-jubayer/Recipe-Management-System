"""
Models for chatbot app
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ChatHistory(models.Model):
    """Chat history model matching Supabase schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_history')
    message = models.TextField()
    response = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    recommended_recipes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}..."
