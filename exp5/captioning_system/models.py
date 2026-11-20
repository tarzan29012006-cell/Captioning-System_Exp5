from django.db import models
import json


class ImageCaption(models.Model):
    """
    Model representing an uploaded image and its CLIP-generated caption.
    """
    # Uploaded image file
    image = models.ImageField(
        upload_to='uploaded_images/',
        help_text="Uploaded image file"
    )

    # Generated primary caption
    caption = models.TextField(
        blank=True,
        null=True,
        help_text="Best matching caption predicted by CLIP"
    )

    # Confidence score (0 to 100 percentage)
    confidence = models.FloatField(
        blank=True,
        null=True,
        help_text="Confidence percentage for the primary caption"
    )

    # JSON-encoded top candidate matches and probabilities
    top_matches = models.TextField(
        blank=True,
        null=True,
        help_text="JSON-serialized top candidate matches with confidence scores"
    )

    # Upload timestamp
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        caption_preview = (self.caption[:35] + '...') if self.caption and len(self.caption) > 35 else (self.caption or "No caption")
        return f"Caption #{self.id}: {caption_preview}"

    @property
    def top_matches_list(self):
        """Returns deserialized top matches list."""
        if self.top_matches:
            try:
                return json.loads(self.top_matches)
            except Exception:
                return []
        return []

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Image Caption"
        verbose_name_plural = "Image Captions"
