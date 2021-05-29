function checkBlock() {
    let weakIndicator = document.getElementById('strength-weak').style.display === 'none';
    let policyIndicator = document.getElementById('customCheckRegister').checked;
    let confirmIndicator = document.getElementById('password').value === document.getElementById('confirm-password').value;
    document.getElementById('submit-button').disabled = !(weakIndicator && policyIndicator && confirmIndicator);

}