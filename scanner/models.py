from django.db import models
from django.conf import settings


class ScanHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scan_history'
    )

    url = models.URLField(max_length=2048)
    prediction = models.CharField(max_length=20)
    phishing_probability = models.FloatField()
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']
        verbose_name_plural = 'Scan Histories'

    def __str__(self):
        return f"{self.url} - {self.prediction}"