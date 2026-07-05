document.addEventListener('DOMContentLoaded', () => {
  const cartDrawerOverlay = document.getElementById('CartDrawerOverlay');
  const cartDrawer = document.getElementById('CartDrawer');
  const cartDrawerItems = document.getElementById('CartDrawerItems');
  const cartDrawerTotal = document.getElementById('CartDrawerTotal');
  const cartItemCount = document.getElementById('cart-item-count');

  // Open Cart Drawer
  document.querySelectorAll('.cart-toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openCartDrawer();
    });
  });

  // Close Cart Drawer
  document.querySelectorAll('.cart-close-btn').forEach(btn => {
    btn.addEventListener('click', closeCartDrawer);
  });
  
  cartDrawerOverlay.addEventListener('click', (e) => {
    if (e.target === cartDrawerOverlay) closeCartDrawer();
  });

  function openCartDrawer() {
    cartDrawerOverlay.style.opacity = '1';
    cartDrawerOverlay.style.pointerEvents = 'auto';
    cartDrawer.style.right = '0';
    fetchCart();
  }

  function closeCartDrawer() {
    cartDrawerOverlay.style.opacity = '0';
    cartDrawerOverlay.style.pointerEvents = 'none';
    cartDrawer.style.right = '-400px';
  }

  // Fetch Cart from Shopify API
  function fetchCart() {
    fetch('/cart.js')
      .then(res => res.json())
      .then(cart => {
        renderCart(cart);
      });
  }

  // Render Cart UI
  function renderCart(cart) {
    cartDrawerTotal.innerHTML = Shopify.formatMoney ? Shopify.formatMoney(cart.total_price) : '£' + (cart.total_price / 100).toFixed(2);
    
    if (cart.item_count > 0) {
      cartItemCount.style.display = 'inline-block';
      cartItemCount.innerText = cart.item_count;
    } else {
      cartItemCount.style.display = 'none';
    }

    if (cart.items.length === 0) {
      cartDrawerItems.innerHTML = '<p style="color: #777;">Your cart is empty.</p>';
      return;
    }

    let html = '<div style="display: flex; flex-direction: column; gap: 16px;">';
    cart.items.forEach(item => {
      html += `
        <div style="display: flex; gap: 16px; align-items: center;">
          <img src="${item.image}" alt="${item.title}" style="width: 60px; height: 60px; object-fit: contain; background: #f5f5f5; border-radius: 8px;" />
          <div style="flex: 1;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${item.product_title}</div>
            <div style="color: #555; font-size: 14px; margin-bottom: 8px;">£${(item.price / 100).toFixed(2)}</div>
            <div style="display: flex; align-items: center; gap: 12px;">
              <button onclick="changeItemQty('${item.key}', ${item.quantity - 1})" style="background: #eee; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer;">-</button>
              <span>${item.quantity}</span>
              <button onclick="changeItemQty('${item.key}', ${item.quantity + 1})" style="background: #eee; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer;">+</button>
            </div>
          </div>
          <button onclick="changeItemQty('${item.key}', 0)" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #999;">🗑</button>
        </div>
      `;
    });
    html += '</div>';
    cartDrawerItems.innerHTML = html;
  }

  // AJAX Add to Cart (for forms with class ajax-add-to-cart)
  document.querySelectorAll('.ajax-add-to-cart').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const form = btn.closest('form');
      const formData = new FormData(form);
      
      fetch('/cart/add.js', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(() => {
        openCartDrawer();
      })
      .catch(err => {
        console.error('Error adding to cart', err);
      });
    });
  });

  // Global change qty
  window.changeItemQty = function(key, qty) {
    fetch('/cart/change.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: key, quantity: qty })
    })
    .then(res => res.json())
    .then(cart => {
      renderCart(cart);
    });
  }

  // Initial fetch to update badge
  fetchCart();
});
