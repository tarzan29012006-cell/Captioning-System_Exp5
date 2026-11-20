/**
 * CLIPVision AI - Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('imageFileInput');
    const browseBtn = document.getElementById('browseBtn');
    const dropzonePrompt = document.getElementById('dropzonePrompt');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const captionForm = document.getElementById('captionForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const copyCaptionBtn = document.getElementById('copyCaptionBtn');
    const sampleButtons = document.querySelectorAll('.sample-btn');

    // Browse file trigger
    if (browseBtn && fileInput) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop event listeners
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('drag-over');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                handleFileSelection(fileInput.files[0]);
            }
        });
    }

    // Handle File Selection and Show Preview
    function handleFileSelection(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file (PNG, JPG, WEBP, GIF).');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            fileNameDisplay.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            dropzonePrompt.classList.add('d-none');
            previewContainer.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    }

    // Remove Image
    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            imagePreview.src = '#';
            previewContainer.classList.add('d-none');
            dropzonePrompt.classList.remove('d-none');
        });
    }

    // Form submit loading state
    if (captionForm && submitBtn) {
        captionForm.addEventListener('submit', () => {
            if (!fileInput.files || fileInput.files.length === 0) {
                return;
            }
            submitBtn.disabled = true;
            btnText.textContent = 'Analyzing image with CLIP neural network...';
            btnSpinner.classList.remove('d-none');
        });
    }

    // Copy Caption Button
    if (copyCaptionBtn) {
        copyCaptionBtn.addEventListener('click', () => {
            const captionElem = document.getElementById('generatedCaptionText');
            if (captionElem) {
                const text = captionElem.innerText.replace(/^"|"$/g, '');
                navigator.clipboard.writeText(text).then(() => {
                    const originalHtml = copyCaptionBtn.innerHTML;
                    copyCaptionBtn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                    copyCaptionBtn.classList.replace('btn-outline-primary', 'btn-success');
                    setTimeout(() => {
                        copyCaptionBtn.innerHTML = originalHtml;
                        copyCaptionBtn.classList.replace('btn-success', 'btn-outline-primary');
                    }, 2000);
                });
            }
        });
    }

    // Sample image click loader
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const imageUrl = btn.getAttribute('data-url');
            const imageName = btn.getAttribute('data-name');
            const originalText = btn.innerHTML;

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Loading...';

            try {
                const response = await fetch(imageUrl);
                const blob = await response.blob();
                const file = new File([blob], imageName, { type: blob.type || 'image/jpeg' });

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;

                handleFileSelection(file);
            } catch (err) {
                console.error("Failed to load sample image:", err);
                alert("Could not load sample image. Please select an image from your computer.");
            } finally {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        });
    });
});
