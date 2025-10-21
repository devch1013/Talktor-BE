from django.db import models

from api.user.models import User


class Project(models.Model):
    """
    Project
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects", verbose_name="User"
    )
    name = models.CharField(max_length=100, verbose_name="Name")
    color = models.CharField(
        max_length=7, default="#3B82F6", verbose_name="Color"
    )  # hex color
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "projects"
        ordering = ["-updated_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.name} ({self.user.username})"
