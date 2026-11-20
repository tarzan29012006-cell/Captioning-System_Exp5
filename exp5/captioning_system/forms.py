from django import forms
from .models import ImageCaption


class ImageUploadForm(forms.ModelForm):
    """
    Form for uploading an image and optionally providing custom candidate captions.
    """
    custom_candidates = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': "Optional: Enter candidate captions (one per line) to evaluate.\nExample:\nA golden retriever catching a frisbee\nA cat napping in the sunlight\nA modern red sports car on a highway\nA delicious slice of pizza",
            'id': 'customCandidatesInput'
        }),
        help_text="Enter custom candidate captions (one per line). If left empty, the standard candidate list will be used."
    )

    class Meta:
        model = ImageCaption
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control visually-hidden',
                'accept': 'image/*',
                'id': 'imageFileInput',
                'required': True
            })
        }
