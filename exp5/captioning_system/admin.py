from django.contrib import admin
from django.utils.html import format_html
from .models import ImageCaption


@admin.register(ImageCaption)
class ImageCaptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail_preview', 'short_caption', 'confidence_badge', 'created_at')
    list_display_links = ('id', 'short_caption')
    list_filter = ('created_at',)
    search_fields = ('caption',)
    readonly_fields = ('created_at', 'large_image_preview', 'top_matches_display')
    ordering = ('-created_at',)

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 55px; height: 55px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = "Image Preview"

    def short_caption(self, obj):
        if not obj.caption:
            return "-"
        return obj.caption[:60] + "..." if len(obj.caption) > 60 else obj.caption
    short_caption.short_description = "Caption"

    def confidence_badge(self, obj):
        if obj.confidence is None:
            return "-"
        color = "#10b981" if obj.confidence >= 50 else ("#f59e0b" if obj.confidence >= 20 else "#ef4444")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 0.82rem;">{:.2f}%</span>',
            color, obj.confidence
        )
    confidence_badge.short_description = "Confidence"

    def large_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);" />',
                obj.image.url
            )
        return "No Image Available"
    large_image_preview.short_description = "Uploaded Image"

    def top_matches_display(self, obj):
        matches = obj.top_matches_list
        if not matches:
            return "No match details available"
        rows = "".join([
            f"<li><strong>{m.get('caption', '')}</strong> — <span style='color: #2563eb; font-weight: 600;'>{m.get('confidence', 0)}%</span></li>"
            for m in matches
        ])
        return format_html(f"<ol style='padding-left: 20px; line-height: 1.8;'>{rows}</ol>")
    top_matches_display.short_description = "Top Candidate Rankings"
