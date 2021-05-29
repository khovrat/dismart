function openUsers() {
    document.getElementById('users-form').style.display = 'initial';
    document.getElementById('users-enter').style.display = 'none';
    document.getElementById('users-cancel').style.display = 'initial';
}

function closeUsers() {
    document.getElementById('users-form').style.display = 'none';
    document.getElementById('users-enter').style.display = 'initial';
    document.getElementById('users-cancel').style.display = 'none';
}