// Redirect if not authenticated
const token = localStorage.getItem("token");
if (!token) {
    window.location.href = "auth.html";
}

document.addEventListener("DOMContentLoaded", () => {

    const productsDiv = document.getElementById("products");
    const form = document.getElementById("product-form");

    async function fetchProducts() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/products", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error("Failed to fetch products");
            }

            const products = await response.json();
            productsDiv.innerHTML = "";

            products.forEach(product => {
                const productEl = document.createElement("div");
                productEl.classList.add("product");

                productEl.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>Price: GHS ${product.price}</p>
                    <p>Stock: ${product.stock}</p>
                `;

                productsDiv.appendChild(productEl);
            });
        } catch (error) {
            productsDiv.innerHTML = "Failed to load products";
            console.error(error);
        }
    }

    async function addProduct(name, price, stock) {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/products", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ name, price, stock })
            });

            if (!response.ok) {
                throw new Error("Failed to add product");
            }

            fetchProducts(); // refresh list
        } catch (error) {
            console.error(error);
            alert("Could not add product");
        }
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const name = document.getElementById("name").value;
        const price = Number(document.getElementById("price").value);
        const stock = Number(document.getElementById("stock").value);

        addProduct(name, price, stock);
        form.reset();
    });

    // Load products on page load
    fetchProducts();
});
