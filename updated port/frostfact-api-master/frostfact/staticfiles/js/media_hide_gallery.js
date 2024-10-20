document.addEventListener('DOMContentLoaded', function() {
    function toggleMediaFields() {
        var mediaChoicesField = document.getElementById('id_gallery_media_choices');
        var selectedMedia = mediaChoicesField.value;
        var imageField = document.getElementById('id_gallery_media_image').closest('.form-row');
        var videoField = document.getElementById('id_gallery_media_video').closest('.form-row');

        if (selectedMedia === 'Image') {
            imageField.style.display = 'block';
            videoField.style.display = 'none';
        } else if (selectedMedia === 'Video') {
            imageField.style.display = 'none';
            videoField.style.display = 'block';
        }
    }

    var mediaChoicesField = document.getElementById('id_gallery_media_choices');
    if (mediaChoicesField) {
        toggleMediaFields(); // Initial call on page load
        mediaChoicesField.addEventListener('change', toggleMediaFields); // Event listener for changes
    }
});
