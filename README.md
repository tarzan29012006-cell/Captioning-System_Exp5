# AI Image Captioning System using OpenAI CLIP (Experiment 5)

An end-to-end full-stack AI Image Captioning Web Application powered by **OpenAI CLIP (Contrastive Language-Image Pretraining - ViT-B/32)**, **Django**, and **Bootstrap 5**.

---

## 🌟 Key Features

- **Zero-Shot Image Captioning**: Leverages OpenAI's Vision Transformer (`ViT-B/32`) and Text Transformer to match uploaded images against candidate text descriptions.
- **Top-5 Confidence Breakdown**: Displays real-time softmax probability distribution and confidence percentages across candidate matches with progress bars.
- **Custom Candidate Support**: Allows users to input custom candidate captions to test arbitrary zero-shot image classification and captioning scenarios.
- **Interactive UI**:
  - Modern, responsive interface built with Bootstrap 5.3, Bootstrap Icons, and glassmorphic card elements.
  - Drag-and-drop file upload zone with live image preview.
  - One-click sample test images for immediate demonstration.
  - One-click copy caption button.
- **History & Gallery**:
  - Browse past generated captions and uploaded images.
  - Search history by caption text.
  - Sort by newest, oldest, highest confidence, or lowest confidence.
  - Modal confirmation for safe record and image file deletion.
- **Full-featured Django Admin**:
  - Customized admin list display with thumbnail image previews, color-coded confidence badges, search, and date filters.
- **RESTful API**:
  - `POST /api/caption/`: Upload an image and receive JSON predictions with top matches and confidence scores.
  - `GET /api/history/`: Retrieve JSON list of recently generated captions.
  - Interactive API documentation page at `/api-docs/`.

---

## 🏗️ Architecture & How It Works

```
Uploaded Image                     Candidate Captions
      │                                    │
      ▼                                    ▼
[Vision Transformer]              [Text Transformer]
(ViT-B/32 Image Encoder)          (Text Encoder)
      │                                    │
      ▼                                    ▼
Image Embedding (512-dim)         Text Embeddings (512-dim)
      │                                    │
      └──────────────┬─────────────────────┘
                     ▼
             Cosine Similarity
                     │
                     ▼
          Softmax Probabilities
                     │
                     ▼
      Best Caption + Top-K Matches
```

1. **Visual Encoding**: The input image is converted to RGB, resized, normalized, and encoded into a 512-dimensional continuous latent vector using CLIP's Vision Transformer.
2. **Text Encoding**: Candidate captions (either the 30 built-in descriptions or custom user prompts) are tokenized and encoded into 512-dimensional vectors in the shared multi-modal latent space.
3. **Similarity & Softmax**: The cross-modal dot product between the image vector and all text vectors is computed and scaled. A softmax function normalizes these scores into a probability distribution summing to 100%.
4. **Ranking**: The candidate caption with the highest cosine similarity is selected as the primary caption, accompanied by its top-k ranked alternatives.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ (Tested up to Python 3.15)
- PyTorch
- Hugging Face Transformers

### Installation

1. Navigate to the project directory:
   ```bash
   cd exp5
   ```

2. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create an admin superuser (optional, for accessing Django Admin):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your web browser and navigate to:
   - Web App: `http://127.0.0.1:8000/`
   - History & Gallery: `http://127.0.0.1:8000/history/`
   - REST API Docs: `http://127.0.0.1:8000/api-docs/`
   - Django Admin: `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Unit Tests

Run the automated test suite with:

```bash
python manage.py test captioning_system
```

---

## 📡 REST API Examples

### Generate Caption via cURL

```bash
curl -X POST http://127.0.0.1:8000/api/caption/ \
  -F "image=@/path/to/image.jpg" \
  -F "custom_candidates=A dog playing in the garden\nA cat sleeping on a sofa"
```

### JSON Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "caption": "A dog playing in the garden",
    "confidence": 92.4,
    "top_matches": [
      { "caption": "A dog playing in the garden", "confidence": 92.4 },
      { "caption": "A cat sleeping on a sofa", "confidence": 7.6 }
    ],
    "image_url": "/media/uploaded_images/image.jpg",
    "device": "cpu",
    "candidates_evaluated": 2
  }
}
```

---

## 📂 Project Structure

```
EXP_5/
├── requirements.txt
├── README.md
└── exp5/
    ├── manage.py
    ├── db.sqlite3
    ├── exp5/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    └── captioning_system/
        ├── admin.py
        ├── apps.py
        ├── clip_model.py
        ├── forms.py
        ├── models.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        ├── static/captioning_system/
        │   ├── css/style.css
        │   └── js/main.js
        └── templates/captioning_system/
            ├── base.html
            ├── index.html
            ├── history.html
            ├── detail.html
            └── api_docs.html
```
