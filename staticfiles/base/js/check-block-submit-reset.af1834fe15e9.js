function checkBlock() {
    let weakIndicator = document.getElementById('strength-weak').style.display === 'none';
    let confirmIndicator = document.getElementById('password').value === document.getElementById('confirm-password').value;
    document.getElementById('submit-button').disabled = !(weakIndicator && confirmIndicator);
}