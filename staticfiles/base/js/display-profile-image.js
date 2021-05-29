function readURL(input) {
    if (input.files && input.files[0]) {
        document.getElementById('old-image-profile').src = document.getElementById('image-profile').src;
        document.getElementById('image-profile').src = URL.createObjectURL(input.files[0]);
        document.getElementById('image-button-profile-save').style.display = 'initial';
        document.getElementById('image-button-profile-cancel').style.display = 'initial';
    }
}

function cancelUpload() {
    document.getElementById('image-profile').src = document.getElementById('old-image-profile').src;
    document.getElementById('image-button-profile-save').style.display = 'none';
    document.getElementById('image-button-profile-cancel').style.display = 'none';
}

function readButtonURL(input) {
    if (input.files && input.files[0]) {
        document.getElementById('image-profile').src = URL.createObjectURL(input.files[0]);
        document.getElementById('submit-modal-form').disabled = false
    }
}