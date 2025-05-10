document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".buy-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const container = button.parentElement;
      const productId = container.dataset.productId;
      container.innerHTML = `
        <div class="d-flex justify-content-center align-items-center">
          <button class="btn btn-sm btn-outline-secondary minus">−</button>
          <span class="mx-3 quantity">1</span>
          <button class="btn btn-sm btn-outline-secondary plus">+</button>
        </div>
        <button class="btn btn-sm btn-success mt-2 confirm">Добавить</button>
      `;

      let quantity = 1;
      const minus = container.querySelector(".minus");
      const plus = container.querySelector(".plus");
      const quantitySpan = container.querySelector(".quantity");
      const confirm = container.querySelector(".confirm");

      minus.addEventListener("click", () => {
        if (quantity > 1) quantitySpan.textContent = --quantity;
      });
      plus.addEventListener("click", () => {
        quantitySpan.textContent = ++quantity;
      });

      confirm.addEventListener("click", () => {
        fetch("/add-to-cart", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: productId, quantity }),
        })
          .then((res) => res.json())
          .then((data) => {
            alert(data.message);
          });
      });
    });
  });
});
