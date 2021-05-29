function openResetPassword() {
    document.getElementById("reset-password-cancel").style.display = 'initial';
    document.getElementById("reset-password-enter").style.display = 'none';
    document.getElementById("reset-password-form").style.display = 'initial';
}

function closeResetPassword() {
    document.getElementById("reset-password-cancel").style.display = 'none';
    document.getElementById("reset-password-enter").style.display = 'initial';
    document.getElementById("reset-password-form").style.display = 'none';
}