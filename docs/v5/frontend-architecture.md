# 🖥️ MiniCommerce V5 Documentation — Frontend Architecture & Store Manager Portal

Version 5 updates the React 18 SPA with automatic token rotation interceptors, role-aware navigation, and a Store Manager Catalog Management Portal.

---

## 🔄 1. Automatic 401 Token Refresh Interceptor (`api.js`)

The API client layer intercepts `HTTP 401 Unauthorized` responses and automatically attempts token rotation before failing requests:

```javascript
// Catch 401 unauthorized and attempt automatic token rotation refresh
if (response.status === 401 && requireAuth && endpoint !== "/auth/refresh" && endpoint !== "/auth/login") {
  try {
    const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin"
    });
    if (refreshRes.ok) {
      const refreshData = await refreshRes.json();
      if (refreshData && refreshData.access_token) {
        localStorage.setItem("token", refreshData.access_token);
        headers["Authorization"] = `Bearer ${refreshData.access_token}`;
        response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
      }
    }
  } catch (_) {}
}
```

### User Experience Benefit:
When an Access Token expires after 15 minutes, background background API calls automatically refresh the token using the `HttpOnly` Refresh Cookie without logging out the user or interrupting active shopping flows.

---

## 🏬 2. Store Manager Catalog Portal (`StoreManagerDashboard.jsx`)

Accounts with `STORE_MANAGER` or `SRE_ADMIN` roles gain access to the Store Manager Portal:

### Features:
- **Product Creation Form**: Add new items with `name`, `description`, `price`, and `stock`.
- **Inventory Stock Overview**: Real-time table displaying current stock counts, ID basenames, and active/deleted status pills.
- **Soft Delete Action**: Soft delete products from the catalog (`DELETE /api/v1/products/{id}`).
- **Catalog Invalidation**: Automatically triggers backend Redis cache purging (`products:*`).
