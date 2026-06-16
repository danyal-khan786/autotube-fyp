from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class VideoAnalysis(models.Model):
    # Relational Link
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    
    # Input & Video Metadata
    youtube_url = models.URLField(max_length=500)
    video_title = models.CharField(max_length=300, blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    transcript = models.TextField(blank=True, null=True)
    
    # AI Generated Outputs
    summary = models.TextField(blank=True, null=True)
    tone_analysis = models.CharField(max_length=150, blank=True, null=True)
    target_audience = models.CharField(max_length=300, blank=True, null=True)
    
    # JSON Fields for structured data (Lists of strings)
    suggested_titles = models.JSONField(default=list, blank=True, null=True)
    seo_tags = models.JSONField(default=list, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Ensures newest videos show up first on the dashboard
        verbose_name_plural = "Video Analyses"

    def __str__(self):
        # Fallback string representation if title hasn't been fetched yet
        if self.video_title:
            return f"{self.user.username} - {self.video_title[:50]}"
        return f"{self.user.username} - {self.youtube_url}"