// static/js/cart.js
document.addEventListener('DOMContentLoaded', function() {
    const updateCartItem = async (productId, quantity) => {
        try {
            const response = await fetch(`/cart/update_cart_item/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ quantity })
            });

            if (!response.ok) {
                throw new Error('Failed to update cart item');
            }

            const data = await response.json();
            if (data.success) {
                updateCart();
            }
        } catch (error) {
            console.error('Error updating cart item:', error);
        }
    };

    const updateCart = () => {
        // Logic to update the cart items and total dynamically
        let total = 0;
        document.querySelectorAll('.cart-item').forEach(item => {
            const quantity = parseInt(item.querySelector('.quantity').value, 10);
            const price = parseFloat(item.querySelector('span').textContent.replace('$', ''));
            const itemTotal = price * quantity;
            total += itemTotal;
            item.querySelector('.quantity').setAttribute('data-total', itemTotal.toFixed(2));
        });
        document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
    };

    document.getElementById('cartModal').addEventListener('click', function(e) {
        const cartItem = e.target.closest('.cart-item');
        if (cartItem) {
            const productId = cartItem.getAttribute('data-product-id');
            const quantityInput = cartItem.querySelector('.quantity');
            let quantity = parseInt(quantityInput.value, 10);

            if (e.target.classList.contains('increment')) {
                quantity += 1;
                quantityInput.value = quantity;
                updateCartItem(productId, quantity);
            } else if (e.target.classList.contains('decrement')) {
                if (quantity > 1) {
                    quantity -= 1;
                    quantityInput.value = quantity;
                    updateCartItem(productId, quantity);
                }
            }

            updateCart();
        }
    });

    const deleteButtons = document.querySelectorAll('.delete-item');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-product-id');

            fetch(`/cart/delete_cart_item/${productId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar el carrito en la interfaz
                    this.closest('.cart-item').remove();
                    updateCartTotal();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    function updateCartTotal() {
        // Aquí puedes recalcular el total del carrito y actualizarlo en la interfaz
        let total = 0;
        const cartItems = document.querySelectorAll('.cart-item');
        cartItems.forEach(item => {
            const price = parseFloat(item.querySelector('span').textContent.replace('$', ''));
            const quantity = parseInt(item.querySelector('.quantity').value);
            total += price * quantity;
        });

        document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
    }
});
