document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("usernameForm");

    form.addEventListener("submit", function (e) {
        Swal.fire({
            title: 'Submitting...',
            text: 'Please wait while we process your request.',
            allowEscapeKey: false,
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    });
});