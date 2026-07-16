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
    cartDrawer.style.right = '-420px';
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
  // Render Cart UI
  function renderCart(cart) {
    const progressCard = document.getElementById('CartProgressCard');
    const progressRemaining = document.getElementById('CartProgressRemaining');
    const progressBar = document.getElementById('CartProgressBar');
    const progressText = document.getElementById('CartProgressText');
    
    const summarySubtotal = document.getElementById('CartSummarySubtotal');
    const summaryDelivery = document.getElementById('CartSummaryDelivery');
    const drawerFooter = document.getElementById('CartDrawerFooter');

    // Update cart badge icon
    if (cart.item_count > 0) {
      cartItemCount.style.display = 'inline-block';
      cartItemCount.innerText = cart.item_count;
    } else {
      cartItemCount.style.display = 'none';
    }

    // Handle Empty State
    if (cart.items.length === 0) {
      if (progressCard) progressCard.style.display = 'none';
      if (drawerFooter) drawerFooter.style.display = 'none';
      cartDrawerItems.innerHTML = `
        <div style="text-align: center; padding: 40px 0;">
          <p style="color: #8c867e; font-size: 14px; margin-bottom: 20px;">Your basket is empty.</p>
          <a href="/collections/all" style="display: inline-block; background: #4A5D4E; color: #fff; text-decoration: none; padding: 10px 24px; border-radius: 50px; font-size: 13px; font-weight: 700; transition: opacity 0.2s;">Shop Products</a>
        </div>
      `;
      return;
    }

    // Free Shipping Progress Calculations (Threshold: £30.00)
    if (progressCard) {
      progressCard.style.display = 'block';
      const threshold = 3000; // in cents/pence
      const total = cart.total_price;
      
      if (total < threshold) {
        const remaining = (threshold - total) / 100;
        const pct = (total / threshold) * 100;
        progressRemaining.innerText = '£' + remaining.toFixed(2) + ' away';
        progressBar.style.width = pct + '%';
        progressText.innerText = `Add £${remaining.toFixed(2)} more to unlock free delivery!`;
      } else {
        progressRemaining.innerText = 'Unlocked!';
        progressBar.style.width = '100%';
        progressText.innerText = 'You have unlocked free delivery!';
      }
    }

    // Subtotal and Delivery Calculation
    const deliveryThreshold = 3000;
    const isFreeDelivery = cart.total_price >= deliveryThreshold;
    const deliveryCost = isFreeDelivery ? 0 : 299; // £2.99 standard delivery
    const totalAmount = cart.total_price + deliveryCost;

    if (summarySubtotal) summarySubtotal.innerText = '£' + (cart.total_price / 100).toFixed(2);
    if (summaryDelivery) summaryDelivery.innerText = isFreeDelivery ? 'FREE' : '£' + (deliveryCost / 100).toFixed(2);
    
    // Update Totals (both the big sticky total and generic)
    document.querySelectorAll('#CartDrawerTotal').forEach(el => {
      el.innerText = '£' + (totalAmount / 100).toFixed(2);
    });

    if (drawerFooter) drawerFooter.style.display = 'block';

    // Render Items
    let html = '';
    cart.items.forEach(item => {
      const variantStr = (item.variant_title && item.variant_title !== 'Default Title') ? item.variant_title : '';
      
      html += `
        <div class="cart-item-card">
          <button onclick="changeItemQty('${item.key}', 0)" class="cart-card-remove" aria-label="Remove item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
          
          <img src="${item.image}" alt="${item.title}" class="cart-card-img" />
          
          <div class="cart-card-info-wrap">
            <div>
              <a href="${item.url}" class="cart-card-title">${item.product_title}</a>
              ${variantStr ? `<p class="cart-card-variant">${variantStr}</p>` : ''}
            </div>
            
            <div class="cart-card-bottom">
              <span class="cart-card-price">£${(item.price / 100).toFixed(2)}</span>
              
              <div class="cart-card-qty">
                <button onclick="changeItemQty('${item.key}', ${item.quantity - 1})" class="cart-qty-btn-card" aria-label="Decrease quantity">−</button>
                <span class="cart-qty-val-card">${item.quantity}</span>
                <button onclick="changeItemQty('${item.key}', ${item.quantity + 1})" class="cart-qty-btn-card" aria-label="Increase quantity">+</button>
              </div>
            </div>
          </div>
        </div>
      `;
    });
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
