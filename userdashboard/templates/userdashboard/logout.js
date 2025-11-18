
document.getElementById("logoutBtn")?.addEventListener("click", function (e) {
    e.preventDefault();

    // Remove tokens
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh");

    // Redirect to login page
    window.location.href = "/login/";
});

