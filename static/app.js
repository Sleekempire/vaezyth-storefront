/*
  VAEZYTH – Shopify‑style React Storefront
  -------------------------------------------------
  This file has been rewritten to use the Shopify‑style CSS classes
  defined in styles.css (shop‑*). It includes a slide‑in cart drawer,
  a sticky navigation bar, hero carousel, trust bar, product grid,
  product detail page, newsletter banner, and footer.
*/

const { useState, useEffect } = React;

// -------------------------------------------------------------------
// Icons
// -------------------------------------------------------------------
const StarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="#FFA800" stroke="#FFA800" strokeWidth="2.5" style={{ marginRight: "1px" }}>
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);

// -------------------------------------------------------------------
// Cart Drawer Component
// -------------------------------------------------------------------
const CartDrawer = ({ isOpen, items, onClose, onRemove, onQtyChange }) => {
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', 
      backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999, 
      opacity: isOpen ? 1 : 0, pointerEvents: isOpen ? 'auto' : 'none', 
      transition: 'opacity 0.3s ease'
    }}>
      <div style={{
        position: 'absolute', top: 0, right: isOpen ? 0 : '-400px', 
        width: '100%', maxWidth: '400px', height: '100%', 
        backgroundColor: '#fff', boxShadow: '-5px 0 15px rgba(0,0,0,0.1)', 
        transition: 'right 0.3s ease', display: 'flex', flexDirection: 'column'
      }}>
        <div style={{ padding: '24px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '20px' }}>Your Cart</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>✕</button>
        </div>
        <div style={{ padding: '24px', flex: 1, overflowY: 'auto' }}>
          {items.length === 0 ? (
            <p style={{ color: '#777' }}>Your cart is empty.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {items.map((it, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                  <img src={it.image_url} alt={it.title} style={{ width: '60px', height: '60px', objectFit: 'contain', background: '#f5f5f5', borderRadius: '8px' }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>{it.title}</div>
                    <div style={{ color: '#555', fontSize: '14px', marginBottom: '8px' }}>£{it.price}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <button onClick={() => onQtyChange(idx, Math.max(1, it.qty - 1))} style={{ background: '#eee', border: 'none', width: '24px', height: '24px', borderRadius: '4px', cursor: 'pointer' }}>-</button>
                      <span>{it.qty}</span>
                      <button onClick={() => onQtyChange(idx, it.qty + 1)} style={{ background: '#eee', border: 'none', width: '24px', height: '24px', borderRadius: '4px', cursor: 'pointer' }}>+</button>
                    </div>
                  </div>
                  <button onClick={() => onRemove(idx)} style={{ background: 'none', border: 'none', fontSize: '16px', cursor: 'pointer', color: '#999' }}>🗑</button>
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={{ padding: '24px', borderTop: '1px solid #eee', background: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            <span>Total</span>
            <span>£{total.toFixed(2)}</span>
          </div>
          <button style={{ width: '100%', padding: '16px', background: '#1c1917', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', textTransform: 'uppercase' }} onClick={() => alert('Proceed to checkout')}>Checkout</button>
        </div>
      </div>
    </div>
  );
};

// -------------------------------------------------------------------
// Main App
// -------------------------------------------------------------------
const App = () => {
  // Routing state
  const [view, setView] = useState('home');
  const [selectedProductId, setSelectedProductId] = useState(null);

  // Data state
  const [products, setProducts] = useState([]);
  const [profile, setProfile] = useState({ store_name: 'Vaezyth', email: 'support@vaezyth.com' });
  const [loading, setLoading] = useState(true);

  // UI state
  const [showModal, setShowModal] = useState(false);
  const [modalEmail, setModalEmail] = useState('');
  const [modalSuccess, setModalSuccess] = useState(false);

  // Home page specific state
  const [heroSlide, setHeroSlide] = useState(0);
  const [d3Category, setD3Category] = useState('All'); // retained name for filter logic
  const [d3Ship, setD3Ship] = useState('Free');
  const [d3NewsEmail, setD3NewsEmail] = useState('');

  // Product detail state
  const [activeTab, setActiveTab] = useState('desc');
  const [activeImage, setActiveImage] = useState('');
  const [selectedSize, setSelectedSize] = useState('Medium');
  const [qty, setQty] = useState(1);

  // FAQ state
  const [faqSearch, setFaqSearch] = useState('');

  // Cart state
  const [cartOpen, setCartOpen] = useState(false);
  const [cartItems, setCartItems] = useState([]);

  // -----------------------------------------------------------------
  // Bootstrap & data loading
  // -----------------------------------------------------------------
  useEffect(() => {
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    document.body.style.background = '#FAF7F2';
    fetchData();
    const t = setTimeout(() => setShowModal(true), 4000);
    return () => clearTimeout(t);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dealsRes, profileRes] = await Promise.all([
        fetch('/api/deals'),
        fetch('/api/profile')
      ]);
      if (dealsRes.ok) setProducts(await dealsRes.json());
      if (profileRes.ok) setProfile(await profileRes.json());
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleNewsletterSubmit = async (e, email) => {
    e.preventDefault();
    if (!email) return false;
    try {
      const res = await fetch('/api/opt-in', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      return res.ok;
    } catch { return false; }
  };

  const openProduct = (id) => {
    const prod = products.find(p => p.id === id);
    if (prod) {
      setSelectedProductId(id);
      setActiveImage(prod.image_url);
      setActiveTab('desc');
      setQty(1);
      setView('product_detail');
      window.scrollTo(0, 0);
    }
  };

  // -----------------------------------------------------------------
  // Cart helpers
  // -----------------------------------------------------------------
  const addToCart = (product, qty, size) => {
    const existingIdx = cartItems.findIndex(i => i.id === product.id && i.size === size);
    let newCart;
    if (existingIdx >= 0) {
      newCart = [...cartItems];
      newCart[existingIdx].qty += qty;
    } else {
      newCart = [...cartItems, { ...product, qty, size }];
    }
    setCartItems(newCart);
    setCartOpen(true);
    alert(`✓ Added ${qty}× ${product.title} (${size}) to cart!`);
  };

  const removeCartItem = (idx) => {
    const newCart = cartItems.filter((_, i) => i !== idx);
    setCartItems(newCart);
  };

  const changeCartQty = (idx, newQty) => {
    const newCart = cartItems.map((it, i) => i === idx ? { ...it, qty: newQty } : it);
    setCartItems(newCart);
  };

  // -----------------------------------------------------------------
  // Loading screen
  // -----------------------------------------------------------------
  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f7f7f7', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
      <div style={{ textAlign: 'center', color: '#555' }}>
        <div style={{ width: '36px', height: '36px', border: '3px solid #e0e0e0', borderTop: '3px solid #3b82f6', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }}></div>
        Loading Vaezyth...
      </div>
    </div>
  );

  // -----------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------
  const selectedProduct = products.find(p => p.id === selectedProductId) || {};
  const heroSlides = [
    { tag: 'BESTSELLER', title: 'SMART WALK', desc: 'Retractable dog leash with integrated LED flashlight, built-in poop bag dispenser and 360° tangle‑free swivel.', img: '/leash_luxury_hero.jpg', key: 'Leash' },
    { tag: 'PREMIUM COMFORT', title: 'SMART HOME', desc: 'Double‑layer honeycomb cat litter trapping mat with waterproof base — keeps your floors spotless effortlessly.', img: '/mat_lifestyle_bg.jpg', key: 'Mat' },
    { tag: 'TRAVEL ESSENTIAL', title: 'SMART TRAVEL', desc: '2‑in‑1 portable dog water bottle with a 300ml drinking cup and 120g food compartment for every adventure.', img: '/bottle_lifestyle.jpg', key: 'Bottle' }
  ];
  const cats = [
    { label: 'Dog Leashes', img: '/leash_luxury_hero.jpg' },
    { label: 'Cat Mats', img: '/mat_cat_nobg.jpg' },
    { label: 'Water Bottles', img: '/bottle_1.jpg' },
    { label: 'Poop Bags', img: '/poop_bags.jpg' },
    { label: 'Accessories', img: '/leash_1.jpg' },
    { label: 'Bundles', img: '/mat_lifestyle_bg.jpg' }
  ];
  const filtered = products.filter(p => d3Category === 'All' || p.category === d3Category);
  const padded = [...filtered, ...Array(Math.max(0, 6 - filtered.length)).fill(null)].slice(0, 6);

  // -----------------------------------------------------------------
  // Shared Navbar (used on inner pages)
  // -----------------------------------------------------------------
  const InnerNav = () => (
    <nav className="shop-nav">
      <div className="shop-logo" onClick={() => setView('home')}>vaezyth</div>
      <div className="shop-nav-links">
        {['HOME', 'SHOP', 'ABOUT', 'CONTACT', 'FAQ'].map(label => (
          <span key={label.toLowerCase()} className={"shop-nav-link " + (view === label.toLowerCase() ? "active" : "")} onClick={() => setView(label.toLowerCase())}>{label}</span>
        ))}
      </div>
      <div className="shop-nav-icons">
        <div className="shop-nav-icon" onClick={() => setCartOpen(true)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
          {cartItems.reduce((s, i) => s + i.qty, 0) > 0 && (
            <span className="shop-cart-badge">{cartItems.reduce((s, i) => s + i.qty, 0)}</span>
          )}
        </div>
        <div className="shop-nav-icon">C</div>
      </div>
    </nav>
  );

  // -----------------------------------------------------------------
  // Page wrapper for inner pages
  // -----------------------------------------------------------------
  const PageWrap = ({ children }) => (
    <div className="shop-wrapper">
      <InnerNav />
      <div className="shop-section" style={{ maxWidth: '1280px', margin: '0 auto', padding: '40px' }}>
        {children}
      </div>
    </div>
  );

  // -----------------------------------------------------------------
  // Swatch helper (kept for consistency)
  // -----------------------------------------------------------------
  const Swatches = ({ title }) => {
    const sets = title?.includes('Leash') ? ['#0F172A', '#F472B6', '#38BDF8', '#4ADE80'] :
                title?.includes('Bottle') ? ['#A7F3D0', '#0F172A'] : ['#0F172A', '#94A3B8'];
    return (
      <div style={{ display: 'flex', gap: '4px', margin: '8px 0' }}>
        {sets.map(c => <span key={c} style={{ width: '10px', height: '10px', borderRadius: '50%', background: c, display: 'inline-block' }}></span>)}
      </div>
    );
  };

  // -----------------------------------------------------------------
  // Home View – Shopify style
  // -----------------------------------------------------------------
  if (view === 'home') {
    return (
      <div className="app-container fade-in">
        <div className="header-wrapper">
          <div className="top-navbar">
            <div className="brand-logo-group" onClick={() => setView('home')}>
              <div className="brand-logo-text">Vaezyth</div>
            </div>
            <div className="nav-links" style={{ background: '#fff', borderRadius: '50px', padding: '6px 20px', border: '1px solid #e0e0e0', display: 'flex', gap: '24px' }}>
              <span className="nav-link active" onClick={() => setView('home')}>Home</span>
              <span className="nav-link" onClick={() => setView('shop')}>Shop</span>
              <span className="nav-link" onClick={() => setView('about')}>Our Mission</span>
              <span className="nav-link" onClick={() => setView('faq')}>FAQ Help</span>
            </div>
            <div className="nav-actions">
              <button className="btn-nav-action" onClick={() => setCartOpen(true)}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                {cartItems.reduce((s, i) => s + i.qty, 0) > 0 && <span className="badge-cart-count">{cartItems.reduce((s, i) => s + i.qty, 0)}</span>}
              </button>
              <button className="btn-nav-action">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
          </div>
        </div>
        <div className="template-hero">
          <div className="hero-left-panel">
            <h1>Vaezyth</h1>
            <button className="btn-hero-cta" onClick={() => setView('shop')} style={{ background: '#222', color: '#fff', borderRadius: '50px', border: '1px solid #444', padding: '10px 24px', letterSpacing: '1px', textTransform: 'uppercase', fontSize: '11px', fontWeight: 'bold' }}>
              SHOP COLLECTION ↗
            </button>
            <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
              {['Premium Grade *', 'Ergonomic *', 'Auto-Brake *', '360 Swivel *'].map(tag => (
                <span key={tag} style={{ border: '1px solid rgba(255,255,255,0.2)', padding: '6px 14px', borderRadius: '50px', fontSize: '10px', color: '#fff' }}>{tag}</span>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', height: '100%' }}>
            <p style={{ color: '#fff', fontSize: '14px', maxWidth: '300px', textAlign: 'right', marginBottom: '40px', lineHeight: '1.6' }}>
              Discover elegant, modern, and highly durable pet gear crafted to elevate every walk and complement your home.
            </p>
            <div className="hero-right-media" style={{ position: 'relative', borderRadius: '16px', overflow: 'hidden', width: '100%', height: '300px' }}>
              <img src="/leash_luxury_hero.jpg" alt="Leash" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              <div style={{ position: 'absolute', bottom: '20px', right: '20px', background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)', padding: '16px', borderRadius: '12px', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' }}>
                <div style={{ fontSize: '9px', fontWeight: 'bold', letterSpacing: '1px', marginBottom: '4px' }}>5.0M NYLON TAPE</div>
                <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>Integrated Dispenser & LED</div>
                <div style={{ fontSize: '16px', fontWeight: 'bold' }}>£24.99</div>
              </div>
            </div>
          </div>
        </div>

        <div className="section-title-wrapper">
          <h3 style={{ textTransform: 'uppercase', letterSpacing: '1px', fontSize: '16px', marginBottom: '20px' }}>CATEGORIES</h3>
        </div>
        <div className="mini-products-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '40px' }}>
          {[
            { label: 'Cat Litter Mats', icon: '▦' },
            { label: 'Retractable Leashes', icon: '⏱' },
            { label: 'Travel Bottles', icon: '0' },
            { label: 'All Collections', icon: '⬡' }
          ].map(cat => (
            <div key={cat.label} className="mini-product-card" onClick={() => setView('shop')} style={{ background: '#fff', border: '1px solid #eee', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }}>
              <div className="mini-product-image" style={{ width: '48px', height: '48px', background: '#f5f5f5', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', marginBottom: '16px' }}>{cat.icon}</div>
              <div className="mini-product-title" style={{ fontSize: '12px', fontWeight: 'bold' }}>{cat.label}</div>
            </div>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '60px' }}>
          <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: '12px', padding: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'Cormorant Garamond', marginBottom: '8px' }}>NEW ARRIVAL</div>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '20px' }}>Vaezyth 2-in-1 Hydration Bottle</div>
              <button className="btn-hero-cta" style={{ background: '#fff', color: '#000', border: '1px solid #ddd', borderRadius: '50px', padding: '8px 20px', fontSize: '10px' }} onClick={() => setView('shop')}>CHECK OUT ↗</button>
            </div>
            <img src="/bottle_1.jpg" alt="Bottle" style={{ height: '120px', objectFit: 'contain' }} />
          </div>
          <div style={{ background: '#1c1917', color: '#fff', borderRadius: '12px', padding: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'Cormorant Garamond', marginBottom: '8px' }}>SPECIAL DEAL</div>
              <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '20px' }}>Double-Layer Litter Trapper</div>
              <button className="btn-hero-cta" style={{ background: '#1c1917', color: '#fff', border: '1px solid #444', borderRadius: '50px', padding: '8px 20px', fontSize: '10px' }} onClick={() => setView('shop')}>CHECK OUT ↗</button>
            </div>
            <div style={{ background: '#fff', padding: '10px', borderRadius: '8px' }}>
              <img src="/mat_1.jpg" alt="Mat" style={{ height: '100px', objectFit: 'contain', mixBlendMode: 'multiply' }} />
            </div>
          </div>
        </div>

        <div className="section-title-wrapper" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h3 style={{ fontFamily: 'Cormorant Garamond', fontSize: '32px', fontStyle: 'italic', fontWeight: 'normal' }}>Best Sellers</h3>
          <button style={{ background: 'transparent', border: '1px solid #ddd', padding: '8px 24px', borderRadius: '50px', fontSize: '10px', fontWeight: 'bold', cursor: 'pointer' }} onClick={() => setView('shop')}>SHOP COLLECTION ↗</button>
        </div>
        
        <div className="products-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
          {padded.slice(0, 3).map((prod, i) => prod ? (
            <div key={prod.id} className="product-card luxury-card vertical-dark-card" onClick={() => openProduct(prod.id)} style={{ background: '#1c1917', color: '#fff', borderRadius: '16px', padding: '24px' }}>
              <div className="luxury-card-media" style={{ background: '#fff', borderRadius: '12px', height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
                <img src={prod.image_url} alt={prod.title} style={{ maxHeight: '160px', objectFit: 'contain' }} />
              </div>
              <div className="product-card-title" style={{ color: '#fff', fontSize: '16px' }}>{prod.title}</div>
              <div className="product-card-price-row" style={{ marginTop: 'auto' }}>
                <span className="product-card-price" style={{ color: '#fff' }}>£{prod.price}</span>
              </div>
            </div>
          ) : (
             <div key={i} className="product-card luxury-card" style={{ background: '#fff', borderRadius: '16px', padding: '24px', border: '1px solid #eee' }}>
              <div className="luxury-card-media" style={{ background: '#f9f9f9', borderRadius: '12px', height: '200px', marginBottom: '20px' }}></div>
              <div style={{ height: '16px', background: '#f0f0f0', width: '80%', marginBottom: '8px' }}></div>
              <div style={{ height: '20px', background: '#f0f0f0', width: '40%' }}></div>
             </div>
          ))}
        </div>
        
        {/* Footer */}
        <div style={{ textAlign: 'center', padding: '40px 0', borderTop: '1px solid #ddd', marginTop: '60px', color: '#777', fontSize: '12px' }}>
          © {new Date().getFullYear()} Vaezyth Pet Brand. All Rights Reserved.
        </div>
        
        {/* Cart Drawer */}
        <CartDrawer isOpen={cartOpen} items={cartItems} onClose={() => setCartOpen(false)} onRemove={removeCartItem} onQtyChange={changeCartQty} />
      </div>
    );
  }

  // -----------------------------------------------------------------
  // Shop Page
  // -----------------------------------------------------------------
  if (view === 'shop') {
    return (
      <PageWrap>
        <h2 style={{ fontSize: '28px', fontWeight: 800, color: '#1a1a1a', margin: 0 }}>The Premium Collection</h2>
        <p style={{ color: '#777', marginTop: '8px', fontSize: '14px' }}>Crafted for design, longevity, and happy pets.</p>
        <div className="shop-products-grid" style={{ marginTop: '32px' }}>
          {products.map(prod => (
            <div key={prod.id} className="shop-product-card" onClick={() => openProduct(prod.id)}>
              <div className="shop-product-img-wrap">
                <img src={prod.image_url} alt={prod.title} />
                <div className="shop-product-atc">Add to Cart</div>
              </div>
              <Swatches title={prod.title} />
              <div className="shop-product-title">{prod.title}</div>
              <div className="shop-product-price-row">
                <span className="shop-product-price">£{prod.price}</span>
                {prod.original_price && <span className="shop-product-compare">£{prod.original_price}</span>}
              </div>
            </div>
          ))}
        </div>
        {/* Cart Drawer */}
        <CartDrawer isOpen={cartOpen} items={cartItems} onClose={() => setCartOpen(false)} onRemove={removeCartItem} onQtyChange={changeCartQty} />
      </PageWrap>
    );
  }

  // -----------------------------------------------------------------
  // Product Detail Page
  // -----------------------------------------------------------------
  if (view === 'product_detail') {
    return (
      <PageWrap>
        {/* Breadcrumb */}
        <div style={{ display: 'flex', gap: '6px', fontSize: '12px', color: '#aaa', marginBottom: '28px', alignItems: 'center' }}>
          <span style={{ cursor: 'pointer' }} onClick={() => setView('home')}>Home</span>
          <span>/</span>
          <span style={{ cursor: 'pointer' }} onClick={() => setView('shop')}>Shop</span>
          <span>/</span>
          <span style={{ color: '#333', fontWeight: 600 }}>{selectedProduct.title}</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '60px', alignItems: 'start' }}>
          {/* Gallery */}
          <div>
            <div style={{ background: '#fff', border: '1px solid #e8e8e8', borderRadius: '3px', overflow: 'hidden', marginBottom: '12px', height: '380px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <img src={activeImage} alt={selectedProduct.title} style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {((selectedProduct.image_urls || selectedProduct.image_url || '').split(',')).map((img, i) => (
                <div key={i} onClick={() => setActiveImage(img)} style={{ width: '72px', height: '72px', background: '#fff', border: activeImage === img ? '2px solid #1a1a1a' : '1px solid #e8e8e8', borderRadius: '3px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', padding: '4px' }}>
                  <img src={img} alt="" style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                </div>
              ))}
            </div>
          </div>
          {/* Info */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#888', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: '8px' }}>{selectedProduct.category}</div>
            <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#1a1a1a', margin: '0 0 12px', lineHeight: 1.2 }}>{selectedProduct.title}</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
              {'★★★★★'.split('').map((s, j) => <span key={j} style={{ color: '#f59e0b', fontSize: '13px' }}>{s}</span>)}
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#555' }}>5.0</span>
              <span style={{ fontSize: '12px', color: '#aaa' }}>| 64 Reviews</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: '#1a1a1a' }}>£{selectedProduct.price}</span>
              {selectedProduct.original_price && <span style={{ fontSize: '18px', color: '#aaa', textDecoration: 'line-through' }}>£{selectedProduct.original_price}</span>}
              <span style={{ background: '#dcfce7', color: '#16a34a', fontSize: '11px', fontWeight: 800, padding: '3px 10px', borderRadius: '20px' }}>In Stock</span>
            </div>
            {/* Size selector */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: '#555', marginBottom: '10px' }}>Size</div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {['Small','Medium','Large'].map(sz => (
                  <button key={sz} onClick={() => setSelectedSize(sz)} style={{ padding: '8px 18px', border: selectedSize === sz ? '2px solid #1a1a1a' : '1px solid #ddd', background: selectedSize === sz ? '#1a1a1a' : '#fff', color: selectedSize === sz ? '#fff' : '#555', fontSize: '12px', fontWeight: 600, cursor: 'pointer', borderRadius: '2px', transition: 'all 0.15s' }}>{sz}</button>
                ))}
              </div>
            </div>
            {/* Qty + Add to Cart */}
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #ddd', borderRadius: '2px', background: '#fff' }}>
                <button onClick={() => setQty(Math.max(1, qty - 1))} style={{ width: '38px', height: '46px', background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer', color: '#555' }}>−</button>
                <span style={{ width: '40px', textAlign: 'center', fontSize: '14px', fontWeight: 600 }}>{qty}</span>
                <button onClick={() => setQty(qty + 1)} style={{ width: '38px', height: '46px', background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer', color: '#555' }}>+</button>
              </div>
              <button onClick={() => addToCart(selectedProduct, qty, selectedSize)} style={{ flex: 1, background: '#1a1a1a', color: '#fff', border: 'none', fontSize: '12px', fontWeight: 800, letterSpacing: '1.5px', cursor: 'pointer', borderRadius: '2px', textTransform: 'uppercase', transition: 'background 0.2s' }}>Add to Cart</button>
            </div>
            <button onClick={() => alert('Redirecting to Shop Pay checkout...')} style={{ width: '100%', padding: '14px', background: '#5a31f4', color: '#fff', border: 'none', fontSize: '12px', fontWeight: 800, letterSpacing: '1px', cursor: 'pointer', borderRadius: '2px', textTransform: 'uppercase', marginBottom: '20px' }}>Buy with Shop Pay</button>
            {/* Trust badges */}
            <div style={{ background: '#f9f9f9', border: '1px solid #e8e8e8', borderRadius: '3px', padding: '16px 20px', display: 'grid', gap: '10px' }}>
              {['✓ 30-Day Money-Back Guarantee','✓ Free UK Delivery — Royal Mail Tracked 48','✓ Secure Checkout — Shopify Payments'].map(t => (<div key={t} style={{ fontSize: '12px', color: '#444', fontWeight: 600 }}>{t}</div>))}
            </div>
            {/* Accordion for description, features, specs */}
            <div style={{ marginTop: '24px', borderTop: '1px solid #e8e8e8' }}>
              {['desc','features','specs'].map(key => {
                const labelMap = { desc: 'Product Description', features: 'Key Benefits', specs: 'Specifications' };
                const label = labelMap[key];
                return (
                  <div key={key} style={{ borderBottom: '1px solid #e8e8e8' }}>
                    <div onClick={() => setActiveTab(activeTab === key ? '' : key)} style={{ padding: '14px 0', display: 'flex', justifyContent: 'space-between', cursor: 'pointer', fontSize: '13px', fontWeight: 700, color: '#1a1a1a' }}>
                      <span>{label}</span>
                      <span>{activeTab === key ? '−' : '+'}</span>
                    </div>
                    {activeTab === key && (
                      <div style={{ padding: '0 0 16px', fontSize: '13px', color: '#555', lineHeight: 1.7 }}>
                        {key === 'desc' && <p style={{ margin: 0 }}>{selectedProduct.description}</p>}
                        {key === 'features' && <ul style={{ margin: 0, paddingLeft: '16px' }}>{(selectedProduct.features || '').split(';').map((f,i) => <li key={i} style={{ marginBottom: '6px' }}>{f}</li>)}</ul>}
                        {key === 'specs' && (
                          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <tbody>{Object.entries(JSON.parse(selectedProduct.specifications || '{}')).map(([k,v]) => (
                              <tr key={k}>
                                <td style={{ fontWeight: 700, padding: '6px 0', borderBottom: '1px solid #f0f0f0', width: '40%' }}>{k}</td>
                                <td style={{ color: '#777', padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>{v}</td>
                              </tr>
                            ))}</tbody>
                          </table>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        {/* Cart Drawer */}
        <CartDrawer isOpen={cartOpen} items={cartItems} onClose={() => setCartOpen(false)} onRemove={removeCartItem} onQtyChange={changeCartQty} />
      </PageWrap>
    );
  }

  // -----------------------------------------------------------------
  // About Page
  // -----------------------------------------------------------------
  if (view === 'about') {
    return (
      <PageWrap>
        <h2 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>Design‑Led Pet Products</h2>
        <p style={{ color: '#777', marginBottom: '32px', fontSize: '14px' }}>The team behind Vaezyth shares a single belief: Pets are family.</p>
        <div style={{ height: '300px', borderRadius: '4px', overflow: 'hidden', marginBottom: '32px' }}>
          <img src="https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800" style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="Dog lifestyle" />
        </div>
        <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '14px' }}>Our Mission</h3>
        <p style={{ color: '#555', lineHeight: 1.8, maxWidth: '640px', fontSize: '14px' }}>We set out to redesign dog and cat essentials from the ground up — merging smart functionality with premium materials and modern aesthetics. Every Vaezyth product is built to last, tested by real pet owners, and designed to complement any home.</p>
      </PageWrap>
    );
  }

  // -----------------------------------------------------------------
  // FAQ Page
  // -----------------------------------------------------------------
  if (view === 'faq') {
    return (
      <PageWrap>
        <h2 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>Frequently Asked Questions</h2>
        <p style={{ color: '#777', marginBottom: '28px', fontSize: '14px' }}>Quick answers about orders, delivery, and guarantees.</p>
        <input placeholder="Search questions..." value={faqSearch} onChange={e => setFaqSearch(e.target.value)} style={{ width: '100%', maxWidth: '400px', padding: '12px 16px', border: '1px solid #ddd', borderRadius: '2px', fontSize: '13px', marginBottom: '24px', outline: 'none', boxSizing: 'border-box' }} />
        <div style={{ maxWidth: '680px' }}>
          {[
            { q: 'How long does shipping take?', a: 'Free UK delivery via Royal Mail Tracked 48 — typically 2 business days. International orders take 7–12 business days.' },
            { q: 'What is your return policy?', a: '30-day no‑questions‑asked money‑back guarantee. Return in original packaging for a full refund.' },
            { q: 'Are your products safe for pets?', a: 'Yes. All materials are pet‑safe, BPA‑free, and tested to UK & EU standards.' },
            { q: 'Do you ship internationally?', a: 'Yes — we ship worldwide. International delivery is £4.99 and takes 7–12 business days.' },
            { q: 'How do I track my order?', a: 'You will receive a Royal Mail tracking number by email once your order is dispatched.' }
          ].filter(item => item.q.toLowerCase().includes(faqSearch.toLowerCase())).map((item, i) => (
            <div key={i} style={{ borderBottom: '1px solid #e8e8e8' }}>
              <div onClick={() => setActiveTab(activeTab === `faq_${i}` ? '' : `faq_${i}`)} style={{ padding: '16px 0', display: 'flex', justifyContent: 'space-between', cursor: 'pointer', fontSize: '14px', fontWeight: 700, color: '#1a1a1a' }}>
                <span>{item.q}</span>
                <span>{activeTab === `faq_${i}` ? '−' : '+'}</span>
              </div>
              {activeTab === `faq_${i}` && <p style={{ margin: '0 0 16px', fontSize: '13px', color: '#555', lineHeight: 1.7 }}>{item.a}</p>}
            </div>
          ))}
        </div>
      </PageWrap>
    );
  }

  // -----------------------------------------------------------------
  // Contact Page
  // -----------------------------------------------------------------
  if (view === 'contact') {
    return (
      <PageWrap>
        <h2 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>We're Here to Help</h2>
        <p style={{ color: '#777', marginBottom: '36px', fontSize: '14px' }}>Get in touch with our friendly UK support team.</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '60px', alignItems: 'start' }}>
          <div style={{ background: '#fff', border: '1px solid #e8e8e8', borderRadius: '3px', padding: '28px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, marginBottom: '20px' }}>Contact Information</h3>
            {[
              ['📧', 'Email', profile.email || 'support@vaezyth.com'],
              ['📍', 'Address', 'Vaezyth Brand LTD, London, UK'],
              ['🕐', 'Support Hours', 'Mon–Fri, 9am–5pm GMT']
            ].map(([icon, label, val]) => (
              <div key={label} style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '4px' }}>{icon} {label}</div>
                <div style={{ fontSize: '13px', color: '#666' }}>{val}</div>
              </div>
            ))}
          </div>
          <form onSubmit={e => { e.preventDefault(); alert('✓ Message sent! We reply within 24 hours.'); e.target.reset(); }} style={{ display: 'grid', gap: '16px' }}>
            {[
              ['text','Your Name','John Smith'],
              ['email','Email Address','john@example.com'],
              ['tel','Phone (optional)','+44 7700 900000']
            ].map(([type, label, ph]) => (
              <div key={label}>
                <label style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '1px', color: '#555', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>{label}</label>
                <input type={type} placeholder={ph} style={{ width: '100%', padding: '12px 14px', border: '1px solid #ddd', borderRadius: '2px', fontSize: '13px', outline: 'none', boxSizing: 'border-box', background: '#fff' }} />
              </div>
            ))}
            <div>
              <label style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '1px', color: '#555', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>Message</label>
              <textarea placeholder="How can we help?" rows="5" style={{ width: '100%', padding: '12px 14px', border: '1px solid #ddd', borderRadius: '2px', fontSize: '13px', outline: 'none', boxSizing: 'border-box', resize: 'vertical', background: '#fff' }}></textarea>
            </div>
            <button type="submit" style={{ padding: '14px', background: '#1a1a1a', color: '#fff', border: 'none', fontSize: '11px', fontWeight: 800, letterSpacing: '2px', cursor: 'pointer', borderRadius: '2px', textTransform: 'uppercase' }}>Send Message</button>
          </form>
        </div>
      </PageWrap>
    );
  }

  return null;
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
