const productsDiv = document.getElementById("products");

async function fetchProducts() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/products");
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

fetchProducts();