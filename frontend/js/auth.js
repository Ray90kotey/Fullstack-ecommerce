const authMessage = document.getElementById("auth-message");

/* REGISTER */
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    try {
        const res = await fetch("http://127.0.0.1:5000/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error);

        authMessage.textContent = "Registration successful. You can now log in.";
    } catch (err) {
        authMessage.textContent = err.message;
    }
});

/* LOGIN */
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
        const res = await fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error);

        localStorage.setItem("token", data.access_token);
        window.location.href = "index.html";
    } catch (err) {
        authMessage.textContent = err.message;
    }
});
