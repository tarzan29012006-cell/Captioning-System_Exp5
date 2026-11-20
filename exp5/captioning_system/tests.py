import io
import json
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ImageCaption
from .clip_model import CANDIDATE_CAPTIONS, generate_caption


class ImageCaptionModelTest(TestCase):
    """Unit tests for the ImageCaption Django model."""

    def setUp(self):
        # Create in-memory dummy image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_file = SimpleUploadedFile("test_red.jpg", img_io.getvalue(), content_type="image/jpeg")

        self.caption_obj = ImageCaption.objects.create(
            image=img_file,
            caption="A colorful painting on a wall.",
            confidence=95.5,
            top_matches=json.dumps([
                {"caption": "A colorful painting on a wall.", "confidence": 95.5},
                {"caption": "A house surrounded by trees.", "confidence": 4.5}
            ])
        )

    def test_model_fields(self):
        self.assertEqual(self.caption_obj.caption, "A colorful painting on a wall.")
        self.assertEqual(self.caption_obj.confidence, 95.5)
        self.assertTrue(bool(self.caption_obj.image))

    def test_top_matches_property(self):
        matches = self.caption_obj.top_matches_list
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["caption"], "A colorful painting on a wall.")
        self.assertEqual(matches[0]["confidence"], 95.5)

    def test_string_representation(self):
        self.assertIn("Caption #", str(self.caption_obj))
        self.assertIn("A colorful painting", str(self.caption_obj))


class ViewAndRoutingTest(TestCase):
    """Unit tests for web views and HTTP status codes."""

    def setUp(self):
        self.client = Client()

    def test_index_view_get(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'captioning_system/index.html')
        self.assertIn('form', response.context)

    def test_history_view_get(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'captioning_system/history.html')
        self.assertIn('page_obj', response.context)

    def test_api_docs_view_get(self):
        response = self.client.get(reverse('api_docs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'captioning_system/api_docs.html')

    def test_api_caption_post_missing_image(self):
        response = self.client.post(reverse('api_caption'), {})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_api_history_get(self):
        response = self.client.get(reverse('api_history'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('results', data)


class ClipModelTest(TestCase):
    """Unit tests for CLIP model configuration and inference logic."""

    def test_candidate_captions_list(self):
        self.assertGreater(len(CANDIDATE_CAPTIONS), 10)
        self.assertIn("A dog playing in a garden.", CANDIDATE_CAPTIONS)

    def test_generate_caption_with_custom_candidates(self):
        # Create a small green image
        img = Image.new('RGB', (64, 64), color='green')
        custom = [
            "A tree in a green forest.",
            "A red car parked on a road.",
            "An airplane in the blue sky."
        ]
        result = generate_caption(img, custom_candidates=custom, top_k=2)
        self.assertIn("caption", result)
        self.assertIn("confidence", result)
        self.assertIn("top_matches", result)
        self.assertEqual(len(result["top_matches"]), 2)
        self.assertIn(result["caption"], custom)
