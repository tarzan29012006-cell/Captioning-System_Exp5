import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from .models import ImageCaption
from .forms import ImageUploadForm
from .clip_model import generate_caption, CANDIDATE_CAPTIONS


def index(request):
    """
    Main dashboard view:
    Handles image uploads, triggers CLIP caption inference,
    stores the results, and displays confidence rankings.
    """
    result = None
    caption_record = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the image record first to obtain file on disk
            caption_record = form.save(commit=False)
            caption_record.save()

            custom_candidates = form.cleaned_data.get('custom_candidates')
            image_path = caption_record.image.path

            try:
                # Generate CLIP caption
                result = generate_caption(
                    image_path=image_path,
                    custom_candidates=custom_candidates,
                    top_k=5
                )

                # Update the database record with model predictions
                caption_record.caption = result["caption"]
                caption_record.confidence = result["confidence"]
                caption_record.top_matches = json.dumps(result["top_matches"])
                caption_record.save()

                messages.success(request, f"Caption generated successfully with {result['confidence']}% confidence!")

            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f"Error generating caption: {str(e)}")
        else:
            messages.error(request, "Please provide a valid image file.")
    else:
        form = ImageUploadForm()

    # Retrieve recent captions for the sidebar / recent activity section
    recent_captions = ImageCaption.objects.all()[:6]

    context = {
        'form': form,
        'result': result,
        'caption_record': caption_record,
        'recent_captions': recent_captions,
        'default_candidates_count': len(CANDIDATE_CAPTIONS),
        'sample_candidates': CANDIDATE_CAPTIONS[:10],
    }
    return render(request, 'captioning_system/index.html', context)


def history_view(request):
    """
    History & Gallery view:
    Browse all previously analyzed images, search captions, and filter/sort.
    """
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    captions = ImageCaption.objects.all()

    if query:
        captions = captions.filter(caption__icontains=query)

    if sort_by == 'oldest':
        captions = captions.order_by('created_at')
    elif sort_by == 'confidence_high':
        captions = captions.order_by('-confidence')
    elif sort_by == 'confidence_low':
        captions = captions.order_by('confidence')
    else:
        captions = captions.order_by('-created_at')

    # Pagination: 9 items per page
    paginator = Paginator(captions, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'total_count': captions.count()
    }
    return render(request, 'captioning_system/history.html', context)


def detail_view(request, pk):
    """
    Detailed inspection view for a single captioned image record.
    """
    caption_record = get_object_or_404(ImageCaption, pk=pk)
    context = {
        'record': caption_record,
        'top_matches': caption_record.top_matches_list
    }
    return render(request, 'captioning_system/detail.html', context)


@require_POST
def delete_caption(request, pk):
    """
    Delete a captioned image and its file from storage.
    """
    caption_record = get_object_or_404(ImageCaption, pk=pk)
    
    # Safely remove file from disk if it exists
    if caption_record.image and os.path.isfile(caption_record.image.path):
        try:
            os.remove(caption_record.image.path)
        except OSError:
            pass

    caption_record.delete()
    messages.success(request, f"Caption #{pk} and associated image deleted successfully.")
    return redirect('history')


@csrf_exempt
@require_http_methods(["POST"])
def api_caption(request):
    """
    REST API Endpoint:
    POST /api/caption/
    Body (multipart/form-data):
        - image: (file)
        - custom_candidates: (optional text or JSON array)
        - save_to_db: (optional 'true'/'false', default 'true')
    """
    if 'image' not in request.FILES:
        return JsonResponse({
            'status': 'error',
            'message': 'No image file provided in request.FILES under key "image".'
        }, status=400)

    uploaded_file = request.FILES['image']
    custom_candidates = request.POST.get('custom_candidates', None)
    save_to_db = request.POST.get('save_to_db', 'true').lower() in ('true', '1', 'yes')

    # If JSON array passed in custom_candidates
    if custom_candidates:
        try:
            parsed = json.loads(custom_candidates)
            if isinstance(parsed, list):
                custom_candidates = parsed
        except Exception:
            pass

    try:
        # Create record to store file
        record = ImageCaption.objects.create(image=uploaded_file)
        
        result = generate_caption(
            image_path=record.image.path,
            custom_candidates=custom_candidates,
            top_k=5
        )

        record.caption = result["caption"]
        record.confidence = result["confidence"]
        record.top_matches = json.dumps(result["top_matches"])
        record.save()

        if not save_to_db:
            # Delete if client asked not to save
            if os.path.isfile(record.image.path):
                os.remove(record.image.path)
            record.delete()
            record_id = None
            image_url = None
        else:
            record_id = record.id
            image_url = record.image.url

        return JsonResponse({
            'status': 'success',
            'data': {
                'id': record_id,
                'caption': result["caption"],
                'confidence': result["confidence"],
                'top_matches': result["top_matches"],
                'image_url': image_url,
                'device': result["device"],
                'candidates_evaluated': result["total_candidates"]
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def api_history(request):
    """
    REST API Endpoint:
    GET /api/history/
    Returns list of recent generated captions in JSON format.
    """
    limit = min(int(request.GET.get('limit', 20)), 100)
    captions = ImageCaption.objects.all()[:limit]

    data = [
        {
            'id': c.id,
            'image_url': c.image.url if c.image else None,
            'caption': c.caption,
            'confidence': c.confidence,
            'top_matches': c.top_matches_list,
            'created_at': c.created_at.isoformat()
        }
        for c in captions
    ]
    return JsonResponse({'status': 'success', 'count': len(data), 'results': data})


def api_docs(request):
    """
    Interactive API documentation view.
    """
    return render(request, 'captioning_system/api_docs.html')
