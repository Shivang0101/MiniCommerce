import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import CategoryBar from './components/CategoryBar';
import ControlBar from './components/ControlBar';
import ProductGrid from './components/ProductGrid';
import Pagination from './components/Pagination';
import CartDrawer from './components/CartDrawer';
import AuthModal from './components/AuthModal';
import ProfileModal from './components/ProfileModal';
import Toast from './components/Toast';
import { apiRequest, getUser, getToken, clearAuth, setAuth } from './api';

export default function App() {
  // Catalog State
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [totalCount, setTotalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  // Products Map (id -> Product object for fast cart & order rendering)
  const [productsMap, setProductsMap] = useState({});

  // Cart, Auth & Profile State
  const [cart, setCart] = useState({ cart_items: [] });
  const [user, setUser] = useState(getUser());
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [addingId, setAddingId] = useState(null);

  // Toast State
  const [toast, setToast] = useState(null);

  // Show Toast helper
  const showToast = (type, title, message, orderId = null) => {
    setToast({ type, title, message, orderId });
  };

  // Fetch Products from Backend API
  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      let query = `?page=${page}&page_size=${pageSize}&sort_by=${sortBy}&sort_order=${sortOrder}`;
      if (search.trim()) query += `&search=${encodeURIComponent(search.trim())}`;
      if (selectedCategory && selectedCategory.toLowerCase() !== 'all') {
        query += `&category=${encodeURIComponent(selectedCategory)}`;
      }
      if (minPrice) query += `&min_price=${minPrice}`;
      if (maxPrice) query += `&max_price=${maxPrice}`;

      const { data, totalCount: count } = await apiRequest(`/products${query}`);
      setProducts(data || []);
      if (count !== null) setTotalCount(count);

      // Build product map cache
      setProductsMap((prev) => {
        const next = { ...prev };
        (data || []).forEach((p) => { next[p.id] = p; });
        return next;
      });

    } catch (err) {
      showToast('error', 'Failed to Load Catalog', err.message);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, sortBy, sortOrder, search, selectedCategory, minPrice, maxPrice]);

  // Fetch User's Shopping Cart
  const fetchCart = useCallback(async () => {
    if (!getToken()) return;
    try {
      const { data } = await apiRequest('/cart', 'GET', null, true);
      setCart(data || { cart_items: [] });
    } catch (_) {
      // Cart fetch fail
    }
  }, []);

  // Sync user profile on mount if token exists but user object missing
  useEffect(() => {
    const token = getToken();
    const existingUser = getUser();
    if (token && !existingUser) {
      apiRequest('/auth/me', 'GET', null, true)
        .then(({ data }) => {
          setAuth(token, data);
          setUser(data);
        })
        .catch(() => {
          clearAuth();
          setUser(null);
        });
    }
  }, []);

  // Initial Load & Query Debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProducts();
    }, 250);
    return () => clearTimeout(timer);
  }, [fetchProducts]);

  useEffect(() => {
    if (user || getToken()) {
      fetchCart();
    }
  }, [user, fetchCart]);

  // Reset page to 1 when filters change
  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setPage(1);
  };

  const handleSearchChange = (term) => {
    setSearch(term);
    setPage(1);
  };

  // Ensure user is authenticated before adding to cart
  const ensureAuthenticated = async () => {
    const existingUser = getUser();
    const token = getToken();
    if (existingUser && token) return true;

    // Attempt auto-login as Alice (demo account) if no user logged in
    try {
      const { data: tokenData } = await apiRequest('/auth/login', 'POST', {
        email: 'alice@example.com',
        password: 'Password123!'
      });
      const newTok = tokenData.access_token;
      localStorage.setItem("token", newTok);

      const { data: userProfile } = await apiRequest('/auth/me', 'GET', null, true);
      setAuth(newTok, userProfile);
      setUser(userProfile);
      showToast('success', 'Logged in as Demo User', 'Session authenticated as alice@example.com');
      return true;
    } catch (_) {
      setIsAuthOpen(true);
      return false;
    }
  };

  // Add Item to Cart
  const handleAddToCart = async (productId) => {
    const authenticated = await ensureAuthenticated();
    if (!authenticated) return;

    setAddingId(productId);
    try {
      await apiRequest('/cart/items', 'POST', { product_id: productId, quantity: 1 }, true);
      await fetchCart();
      showToast('success', 'Item Added', 'Product successfully added to your cart.');
    } catch (err) {
      showToast('error', 'Add to Cart Failed', err.message);
    } finally {
      setAddingId(null);
    }
  };

  // Update Cart Item Quantity
  const handleUpdateQuantity = async (itemId, newQuantity) => {
    if (newQuantity <= 0) {
      return handleRemoveItem(itemId);
    }
    try {
      await apiRequest(`/cart/items/${itemId}`, 'PATCH', { quantity: newQuantity }, true);
      await fetchCart();
    } catch (err) {
      showToast('error', 'Quantity Update Failed', err.message);
    }
  };

  // Remove Item from Cart
  const handleRemoveItem = async (itemId) => {
    try {
      await apiRequest(`/cart/items/${itemId}`, 'DELETE', null, true);
      await fetchCart();
    } catch (err) {
      showToast('error', 'Item Removal Failed', err.message);
    }
  };

  // Atomic Idempotent Checkout Execution
  const handleCheckout = async () => {
    if (!cart?.cart_items || cart.cart_items.length === 0) {
      showToast('error', 'Empty Cart', 'Please add products to your cart before checking out.');
      return;
    }

    setIsCheckingOut(true);
    const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    try {
      const { data: order } = await apiRequest(
        '/orders',
        'POST',
        null,
        true,
        { 'Idempotency-Key': idempotencyKey }
      );

      // Reset cart locally & refetch products to update stock numbers
      setCart({ cart_items: [] });
      setIsCartOpen(false);
      await fetchProducts();

      showToast(
        'success',
        '⚡ Atomic Checkout Confirmed!',
        `Order confirmed with Idempotency-Key: ${idempotencyKey}. Total: $${parseFloat(order.total_amount).toFixed(2)}`,
        order.id
      );

    } catch (err) {
      showToast('error', 'Checkout Execution Failed', err.message);
    } finally {
      setIsCheckingOut(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    setCart({ cart_items: [] });
    setIsProfileOpen(false);
    showToast('success', 'Logged Out', 'You have been logged out.');
  };

  const cartItemCount = (cart?.cart_items || []).reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      
      {/* Top Navbar */}
      <Navbar
        search={search}
        setSearch={handleSearchChange}
        cartCount={cartItemCount}
        user={user}
        onOpenCart={() => setIsCartOpen(true)}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenProfile={() => setIsProfileOpen(true)}
        onLogout={handleLogout}
      />

      {/* Category Pills Bar */}
      <CategoryBar
        selectedCategory={selectedCategory}
        onSelectCategory={handleCategorySelect}
      />

      {/* Main Body Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Control Bar: Price Filters, Sort, Page Size */}
        <ControlBar
          minPrice={minPrice}
          setMinPrice={(v) => { setMinPrice(v); setPage(1); }}
          maxPrice={maxPrice}
          setMaxPrice={(v) => { setMaxPrice(v); setPage(1); }}
          sortBy={sortBy}
          setSortBy={setSortBy}
          sortOrder={sortOrder}
          setSortOrder={setSortOrder}
          pageSize={pageSize}
          setPageSize={(s) => { setPageSize(s); setPage(1); }}
          totalCount={totalCount}
        />

        {/* Product Cards Grid */}
        <ProductGrid
          products={products}
          loading={loading}
          onAddToCart={handleAddToCart}
          addingId={addingId}
        />

        {/* Pagination Bar */}
        <Pagination
          page={page}
          pageSize={pageSize}
          totalCount={totalCount}
          onPageChange={(newPage) => { setPage(newPage); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
        />

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 text-center text-xs text-slate-500">
        <p>MiniCommerce V2 Laboratory — Built with FastAPI, PostgreSQL (Supabase), SQLAlchemy 2.x & React Vite SPA</p>
      </footer>

      {/* Cart Drawer */}
      <CartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cart={cart}
        productsMap={productsMap}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onCheckout={handleCheckout}
        isCheckingOut={isCheckingOut}
        user={user}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLoginSuccess={(u) => { setUser(u); fetchCart(); }}
      />

      {/* User Profile & Order History Modal */}
      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        user={user}
        productsMap={productsMap}
      />

      {/* Toast Notification */}
      <Toast toast={toast} onClose={() => setToast(null)} />

    </div>
  );
}
