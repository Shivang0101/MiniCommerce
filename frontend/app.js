// MiniCommerce V2 SPA Client
const API_BASE = "http://localhost:8000/api/v1";

// State
let token = localStorage.getItem("token") || null;
let currentUser = null;
let cart = { cart_items: [] };
let products = [];
let orders = [];

// V2 Catalog State
let currentPage = 1;
const pageSize = 6;
let sortBy = "name";
let sortOrder = "asc";
let minPrice = null;
let maxPrice = null;

// DOM Elements
const authButtons = document.getElementById("auth-buttons");
const userProfile = document.getElementById("user-profile");
const userEmail = document.getElementById("user-email");
const logoutBtn = document.getElementById("logout-btn");
const ordersBtn = document.getElementById("orders-btn");
const openLoginBtn = document.getElementById("open-login-btn");

const productsGrid = document.getElementById("products-grid");
const productCount = document.getElementById("product-count");
const sortBySelect = document.getElementById("sort-by-select");
const sortOrderSelect = document.getElementById("sort-order-select");
const minPriceInput = document.getElementById("min-price-input");
const maxPriceInput = document.getElementById("max-price-input");
const applyFilterBtn = document.getElementById("apply-filter-btn");

const prevPageBtn = document.getElementById("prev-page-btn");
const nextPageBtn = document.getElementById("next-page-btn");
const pageIndicator = document.getElementById("page-indicator");

const cartToggleBtn = document.getElementById("cart-toggle-btn");
const cartBadge = document.getElementById("cart-badge");
const cartDrawer = document.getElementById("cart-drawer");
const cartOverlay = document.getElementById("cart-overlay");
const closeCartBtn = document.getElementById("close-cart-btn");
const cartItemsContainer = document.getElementById("cart-items-container");
const cartTotalPrice = document.getElementById("cart-total-price");
const checkoutBtn = document.getElementById("checkout-btn");

const authModal = document.getElementById("auth-modal");
const closeAuthBtn = document.getElementById("close-auth-btn");
const authForm = document.getElementById("auth-form");
const authEmail = document.getElementById("auth-email");
const authPassword = document.getElementById("auth-password");
const authSubmitBtn = document.getElementById("auth-submit-btn");
const authError = document.getElementById("auth-error");
const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");

const ordersModal = document.getElementById("orders-modal");
const closeOrdersBtn = document.getElementById("close-orders-btn");
const ordersListContainer = document.getElementById("orders-list-container");

const toastContainer = document.getElementById("toast-container");

let authMode = "login"; // "login" | "register"

// Utility: API Fetcher
async function apiRequest(endpoint, method = "GET", body = null, useAuth = true, extraHeaders = {}) {
  const headers = { "Content-Type": "application/json", ...extraHeaders };
  if (useAuth && token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options = { method, headers };
  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const data = await response.json();
    if (!response.ok) {
      const msg = data.error ? data.error.message : (data.detail || "API Request failed");
      throw new Error(msg);
    }
    return data;
  } catch (err) {
    throw err;
  }
}

// Toast Notifications
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerText = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// App Initialization
async function initApp() {
  await fetchProducts();
  if (token) {
    await fetchCurrentUser();
  } else {
    renderUserUI();
  }
  setupEventListeners();
}

// UI State Renders
function renderUserUI() {
  if (currentUser) {
    authButtons.classList.add("hidden");
    userProfile.classList.remove("hidden");
    userEmail.innerText = currentUser.email;
    fetchCart();
  } else {
    authButtons.classList.remove("hidden");
    userProfile.classList.add("hidden");
    cart = { cart_items: [] };
    renderCart();
  }
}

// Products with Pagination & Filtering
async function fetchProducts() {
  try {
    let query = `/products?page=${currentPage}&page_size=${pageSize}&sort_by=${sortBy}&sort_order=${sortOrder}`;
    if (minPrice !== null && minPrice !== "") query += `&min_price=${minPrice}`;
    if (maxPrice !== null && maxPrice !== "") query += `&max_price=${maxPrice}`;

    products = await apiRequest(query, "GET", null, false);
    renderProducts();
  } catch (err) {
    productCount.innerText = "Error loading products";
    showToast("Failed to load products. Is backend running?", "error");
  }
}

function renderProducts() {
  productCount.innerText = `Page ${currentPage} (${products.length} Items)`;
  pageIndicator.innerText = `Page ${currentPage}`;
  prevPageBtn.disabled = (currentPage === 1);
  nextPageBtn.disabled = (products.length < pageSize);

  productsGrid.innerHTML = "";

  if (products.length === 0) {
    productsGrid.innerHTML = "<p style='grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem 0;'>No products found matching filters.</p>";
    return;
  }

  products.forEach(p => {
    const card = document.createElement("div");
    card.className = "product-card";

    let stockClass = "in-stock";
    let stockText = `${p.stock} in stock`;
    if (p.stock === 0) {
      stockClass = "out-stock";
      stockText = "Out of stock";
    } else if (p.stock <= 5) {
      stockClass = "low-stock";
      stockText = `Only ${p.stock} left!`;
    }

    card.innerHTML = `
      <div>
        <div class="product-icon">📦</div>
        <h3 class="product-title">${escapeHtml(p.name)}</h3>
        <p class="product-desc">${escapeHtml(p.description || "")}</p>
      </div>
      <div>
        <div class="product-meta">
          <span class="product-price">$${parseFloat(p.price).toFixed(2)}</span>
          <span class="stock-tag ${stockClass}">${stockText}</span>
        </div>
        <button class="btn btn-primary btn-block add-to-cart-btn" 
                data-id="${p.id}" ${p.stock === 0 ? "disabled" : ""}>
          ${p.stock === 0 ? "Out of Stock" : "Add to Cart"}
        </button>
      </div>
    `;
    productsGrid.appendChild(card);
  });
}

// Cart
async function fetchCart() {
  if (!token) return;
  try {
    cart = await apiRequest("/cart", "GET", true);
    renderCart();
  } catch (err) {
    console.error("Cart error:", err);
  }
}

function renderCart() {
  const items = cart.cart_items || [];
  const totalCount = items.reduce((sum, item) => sum + item.quantity, 0);
  cartBadge.innerText = totalCount;

  cartItemsContainer.innerHTML = "";

  if (items.length === 0) {
    cartItemsContainer.innerHTML = "<p style='text-align:center; color: var(--text-muted); padding: 2rem 0;'>Your cart is empty.</p>";
    cartTotalPrice.innerText = "$0.00";
    checkoutBtn.disabled = true;
    return;
  }

  let grandTotal = 0;
  items.forEach(item => {
    const itemTotal = parseFloat(item.product.price) * item.quantity;
    grandTotal += itemTotal;

    const div = document.createElement("div");
    div.className = "cart-item";
    div.innerHTML = `
      <div class="cart-item-info">
        <h4>${escapeHtml(item.product.name)}</h4>
        <div class="cart-item-price">$${parseFloat(item.product.price).toFixed(2)} x ${item.quantity} = $${itemTotal.toFixed(2)}</div>
      </div>
      <div class="cart-item-actions">
        <button class="qty-btn dec-btn" data-id="${item.id}" data-qty="${item.quantity - 1}">-</button>
        <span class="qty-val">${item.quantity}</span>
        <button class="qty-btn inc-btn" data-id="${item.id}" data-qty="${item.quantity + 1}">+</button>
        <button class="btn-remove del-btn" data-id="${item.id}">&times;</button>
      </div>
    `;
    cartItemsContainer.appendChild(div);
  });

  cartTotalPrice.innerText = `$${grandTotal.toFixed(2)}`;
  checkoutBtn.disabled = false;
}

// Add to Cart
async function handleAddToCart(productId) {
  if (!currentUser) {
    openAuthModal();
    showToast("Please login first to add items to cart", "info");
    return;
  }

  try {
    cart = await apiRequest("/cart/items", "POST", { product_id: productId, quantity: 1 });
    renderCart();
    showToast("Item added to cart", "success");
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Cart Quantity / Remove
async function handleCartUpdate(cartItemId, newQty) {
  if (newQty <= 0) {
    await handleCartRemove(cartItemId);
    return;
  }
  try {
    cart = await apiRequest(`/cart/items/${cartItemId}`, "PATCH", { quantity: newQty });
    renderCart();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function handleCartRemove(cartItemId) {
  try {
    cart = await apiRequest(`/cart/items/${cartItemId}`, "DELETE");
    renderCart();
    showToast("Item removed from cart", "info");
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Atomic Idempotent Checkout
async function handleCheckout() {
  if (!token) return;
  checkoutBtn.disabled = true;
  checkoutBtn.innerText = "Processing Checkout...";

  const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  try {
    const order = await apiRequest("/orders", "POST", null, true, { "Idempotency-Key": idempotencyKey });
    showToast(`Order #${order.id.slice(0, 8)} confirmed! Total: $${parseFloat(order.total_amount).toFixed(2)}`, "success");
    await fetchCart();
    await fetchProducts(); // Refresh stock
    toggleCartDrawer(false);
    openOrdersModal();
  } catch (err) {
    showToast(`Checkout error: ${err.message}`, "error");
  } finally {
    checkoutBtn.disabled = false;
    checkoutBtn.innerText = "⚡ Atomic Checkout";
  }
}

// Auth Logic
async function fetchCurrentUser() {
  try {
    currentUser = await apiRequest("/auth/me", "GET", null, true);
    renderUserUI();
  } catch (err) {
    localStorage.removeItem("token");
    token = null;
    currentUser = null;
    renderUserUI();
  }
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  authError.classList.add("hidden");

  const email = authEmail.value.trim();
  const password = authPassword.value;

  try {
    if (authMode === "register") {
      await apiRequest("/auth/register", "POST", { email, password }, false);
      showToast("Registration successful! Logging in...", "success");
    }

    const tokenData = await apiRequest("/auth/login", "POST", { email, password }, false);
    token = tokenData.access_token;
    localStorage.setItem("token", token);
    await fetchCurrentUser();
    closeAuthModal();
    showToast("Logged in successfully", "success");
  } catch (err) {
    authError.innerText = err.message;
    authError.classList.remove("hidden");
  }
}

// Orders
async function openOrdersModal() {
  if (!token) return;
  ordersModal.classList.remove("hidden");
  ordersListContainer.innerHTML = "<p>Loading orders...</p>";

  try {
    orders = await apiRequest("/orders", "GET");
    renderOrders();
  } catch (err) {
    ordersListContainer.innerHTML = `<p class='form-error'>${err.message}</p>`;
  }
}

function renderOrders() {
  ordersListContainer.innerHTML = "";
  if (orders.length === 0) {
    ordersListContainer.innerHTML = "<p style='color: var(--text-muted); text-align: center; padding: 2rem 0;'>No orders placed yet.</p>";
    return;
  }

  orders.forEach(o => {
    const card = document.createElement("div");
    card.className = "order-card";

    const itemsHtml = o.order_items.map(item => `
      <div class="order-item-row">
        <span>${item.product ? escapeHtml(item.product.name) : 'Product'} x ${item.quantity}</span>
        <span>$${parseFloat(item.price).toFixed(2)}</span>
      </div>
    `).join("");

    const dateStr = new Date(o.created_at).toLocaleString();

    card.innerHTML = `
      <div class="order-header">
        <div>
          <span class="order-id">Order #${o.id.slice(0, 8)}</span>
          ${o.idempotency_key ? `<span class="badge badge-info" style="margin-left: 0.5rem;">Idempotent</span>` : ''}
          <div style="font-size: 0.75rem; color: var(--text-muted);">${dateStr}</div>
        </div>
        <span class="order-status">${o.status}</span>
      </div>
      <div>${itemsHtml}</div>
      <div class="order-total-row">
        <span>Total Amount:</span>
        <span style="color: var(--accent-cyan);">$${parseFloat(o.total_amount).toFixed(2)}</span>
      </div>
    `;
    ordersListContainer.appendChild(card);
  });
}

// Modal & Drawer Controllers
function openAuthModal() {
  authModal.classList.remove("hidden");
}
function closeAuthModal() {
  authModal.classList.add("hidden");
  authError.classList.add("hidden");
  authEmail.value = "";
  authPassword.value = "";
}

function toggleCartDrawer(open) {
  if (open) {
    cartDrawer.classList.remove("hidden");
    cartOverlay.classList.remove("hidden");
  } else {
    cartDrawer.classList.add("hidden");
    cartOverlay.classList.add("hidden");
  }
}

// Quick Test User Login Handler
async function handleQuickLogin(email) {
  authEmail.value = email;
  authPassword.value = "Password123!";
  authMode = "login";
  tabLogin.click();
  authForm.dispatchEvent(new Event("submit"));
}

// Global Event Listeners
function setupEventListeners() {
  openLoginBtn.addEventListener("click", () => {
    authMode = "login";
    tabLogin.click();
    openAuthModal();
  });
  closeAuthBtn.addEventListener("click", closeAuthModal);

  tabLogin.addEventListener("click", () => {
    authMode = "login";
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
    authSubmitBtn.innerText = "Login";
  });

  tabRegister.addEventListener("click", () => {
    authMode = "register";
    tabRegister.classList.add("active");
    tabLogin.classList.remove("active");
    authSubmitBtn.innerText = "Register Account";
  });

  authForm.addEventListener("submit", handleAuthSubmit);

  logoutBtn.addEventListener("click", () => {
    token = null;
    currentUser = null;
    localStorage.removeItem("token");
    renderUserUI();
    showToast("Logged out", "info");
  });

  cartToggleBtn.addEventListener("click", () => toggleCartDrawer(true));
  closeCartBtn.addEventListener("click", () => toggleCartDrawer(false));
  cartOverlay.addEventListener("click", () => toggleCartDrawer(false));

  checkoutBtn.addEventListener("click", handleCheckout);

  ordersBtn.addEventListener("click", openOrdersModal);
  closeOrdersBtn.addEventListener("click", () => ordersModal.classList.add("hidden"));

  // Catalog Filter & Sort Event Handlers
  sortBySelect.addEventListener("change", () => {
    sortBy = sortBySelect.value;
    currentPage = 1;
    fetchProducts();
  });

  sortOrderSelect.addEventListener("change", () => {
    sortOrder = sortOrderSelect.value;
    currentPage = 1;
    fetchProducts();
  });

  applyFilterBtn.addEventListener("click", () => {
    minPrice = minPriceInput.value ? parseFloat(minPriceInput.value) : null;
    maxPrice = maxPriceInput.value ? parseFloat(maxPriceInput.value) : null;
    currentPage = 1;
    fetchProducts();
  });

  prevPageBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      fetchProducts();
    }
  });

  nextPageBtn.addEventListener("click", () => {
    currentPage++;
    fetchProducts();
  });

  // Delegated events on product grid & cart
  productsGrid.addEventListener("click", e => {
    if (e.target.classList.contains("add-to-cart-btn")) {
      const prodId = e.target.getAttribute("data-id");
      handleAddToCart(prodId);
    }
  });

  cartItemsContainer.addEventListener("click", e => {
    const id = e.target.getAttribute("data-id");
    if (!id) return;

    if (e.target.classList.contains("dec-btn") || e.target.classList.contains("inc-btn")) {
      const newQty = parseInt(e.target.getAttribute("data-qty"));
      handleCartUpdate(id, newQty);
    } else if (e.target.classList.contains("del-btn")) {
      handleCartRemove(id);
    }
  });

  // Quick Login Buttons
  document.querySelectorAll(".quick-user-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const email = btn.getAttribute("data-email");
      handleQuickLogin(email);
    });
  });
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, match => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[match]));
}

// Start app
document.addEventListener("DOMContentLoaded", initApp);
