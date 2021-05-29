let timeout;

let password = document.getElementById('password');
let strengthBadgeStrong = document.getElementById('strength-strong');
let strengthBadgeMedium = document.getElementById('strength-medium');
let strengthBadgeWeak = document.getElementById('strength-weak');

let strongPassword = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
let mediumPassword = new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");

function StrengthChecker(PasswordParameter) {
    if (strongPassword.test(PasswordParameter)) {
        strengthBadgeStrong.style.display = 'initial';
        strengthBadgeMedium.style.display = 'none';
        strengthBadgeWeak.style.display = 'none';
    } else if (mediumPassword.test(PasswordParameter)) {
        strengthBadgeStrong.style.display = 'none';
        strengthBadgeMedium.style.display = 'initial';
        strengthBadgeWeak.style.display = 'none';
    } else {
        strengthBadgeStrong.style.display = 'none';
        strengthBadgeMedium.style.display = 'none';
        strengthBadgeWeak.style.display = 'initial';
    }
    if (password.value.length === 0) {
        strengthBadgeStrong.style.display = 'none';
        strengthBadgeMedium.style.display = 'none';
        strengthBadgeWeak.style.display = 'none';
    }
    checkBlock();
}

password.addEventListener("input", () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => StrengthChecker(password.value), 100);
});