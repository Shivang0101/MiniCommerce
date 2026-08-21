import React, { useState, useEffect } from 'react';
import { apiRequest } from '../api';

export default function StoreManagerDashboard({ onClose, onNotification }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // New Product Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiRequest('/products?page=1&page_size=50', 'GET');
      setProducts(res.data || []);
    } catch (err) {
      setError(err.message || 'Failed to load catalog');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    if (!name || !price || !stock) {
      alert('Please fill out Name, Price, and Stock');
      return;
    }
    try {
      setCreating(true);
      await apiRequest('/products', 'POST', {
        name,
        description: description || 'High-performance e-commerce item',
        price: parseFloat(price),
        stock: parseInt(stock, 10)
      }, true);

      setName('');
      setDescription('');
      setPrice('');
      setStock('');
      if (onNotification) onNotification(`Product '${name}' created successfully!`);
      await fetchProducts();
    } catch (err) {
      alert(`Failed to create product: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const handleSoftDelete = async (productId, productName) => {
    if (!window.confirm(`Are you sure you want to soft-delete '${productName}'?`)) return;
    try {
      await apiRequest(`/products/${productId}`, 'DELETE', null, true);
      if (onNotification) onNotification(`Soft-deleted product '${productName}'`);
      await fetchProducts();
    } catch (err) {
      alert(`Soft delete failed: ${err.message}`);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.container}>
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>🏬 Store Manager Catalog Portal</h2>
            <span style={styles.badge}>Scoped RBAC: STORE_MANAGER</span>
          </div>
          <button style={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div style={styles.body}>
          {/* Create Product Card */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>➕ Add New Catalog Product</h3>
            <form onSubmit={handleCreateProduct} style={styles.formGrid}>
              <div>
                <label style={styles.label}>Product Name</label>
                <input
                  style={styles.input}
                  type="text"
                  placeholder="e.g. Ergonomic Mechanical Keyboard"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={styles.label}>Price ($)</label>
                <input
                  style={styles.input}
                  type="number"
                  step="0.01"
                  placeholder="149.99"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={styles.label}>Stock Quantity</label>
                <input
                  style={styles.input}
                  type="number"
                  placeholder="50"
                  value={stock}
                  onChange={(e) => setStock(e.target.value)}
                  required
                />
              </div>
              <div style={{ gridColumn: 'span 3' }}>
                <label style={styles.label}>Description</label>
                <input
                  style={styles.input}
                  type="text"
                  placeholder="e.g. RGB Backlit Hotswappable Mechanical Switches"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div style={{ gridColumn: 'span 3', textAlign: 'right' }}>
                <button type="submit" style={styles.submitBtn} disabled={creating}>
                  {creating ? 'Creating Product...' : '✨ Publish Product to Catalog'}
                </button>
              </div>
            </form>
          </div>

          {/* Catalog Management Table */}
          <div style={styles.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={styles.cardTitle}>📦 Current Store Inventory ({products.length} Items)</h3>
              <button style={styles.refreshBtn} onClick={fetchProducts}>🔄 Refresh List</button>
            </div>

            {loading ? (
              <p style={{ color: '#94a3b8' }}>Loading product inventory...</p>
            ) : error ? (
              <p style={{ color: '#ef4444' }}>{error}</p>
            ) : (
              <div style={styles.tableWrapper}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Name</th>
                      <th style={styles.th}>Price</th>
                      <th style={styles.th}>Stock</th>
                      <th style={styles.th}>Status</th>
                      <th style={styles.th}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <tr key={p.id} style={styles.tr}>
                        <td style={styles.td}>
                          <strong>{p.name}</strong>
                          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>ID: {p.id.slice(0, 8)}...</div>
                        </td>
                        <td style={styles.td}>${parseFloat(p.price).toFixed(2)}</td>
                        <td style={styles.td}>
                          <span style={{
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: '600',
                            backgroundColor: p.stock > 10 ? '#10b98122' : '#f59e0b22',
                            color: p.stock > 10 ? '#34d399' : '#fbbf24'
                          }}>
                            {p.stock} units
                          </span>
                        </td>
                        <td style={styles.td}>
                          <span style={{ color: p.is_deleted ? '#ef4444' : '#10b981', fontWeight: '600', fontSize: '0.8rem' }}>
                            {p.is_deleted ? 'DELETED' : 'ACTIVE'}
                          </span>
                        </td>
                        <td style={styles.td}>
                          <button
                            style={styles.deleteBtn}
                            onClick={() => handleSoftDelete(p.id, p.name)}
                          >
                            🗑️ Soft Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(15, 23, 42, 0.85)',
    backdropFilter: 'blur(8px)',
    zIndex: 9999,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px'
  },
  container: {
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    borderRadius: '16px',
    width: '95%',
    maxWidth: '1000px',
    maxHeight: '90vh',
    overflowY: 'auto',
    color: '#f8fafc',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
  },
  header: {
    padding: '20px 24px',
    borderBottom: '1px solid #1e293b',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  title: { margin: 0, fontSize: '1.4rem', fontWeight: '700', color: '#f8fafc' },
  badge: {
    display: 'inline-block',
    fontSize: '0.75rem',
    fontWeight: '700',
    color: '#38bdf8',
    backgroundColor: '#0284c722',
    border: '1px solid #0284c755',
    borderRadius: '6px',
    padding: '2px 8px',
    marginTop: '4px'
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: '#94a3b8',
    fontSize: '1.5rem',
    cursor: 'pointer'
  },
  body: { padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: '12px',
    padding: '20px',
    border: '1px solid #334155'
  },
  cardTitle: { margin: '0 0 16px 0', fontSize: '1.1rem', color: '#38bdf8' },
  formGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' },
  label: { display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '6px' },
  input: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    borderRadius: '8px',
    color: '#f8fafc',
    fontSize: '0.9rem'
  },
  submitBtn: {
    backgroundColor: '#2563eb',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 20px',
    fontWeight: '600',
    cursor: 'pointer'
  },
  refreshBtn: {
    backgroundColor: '#334155',
    color: '#f8fafc',
    border: 'none',
    borderRadius: '6px',
    padding: '6px 12px',
    fontSize: '0.85rem',
    cursor: 'pointer'
  },
  tableWrapper: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' },
  th: { padding: '12px', borderBottom: '1px solid #334155', color: '#94a3b8' },
  tr: { borderBottom: '1px solid #1e293b' },
  td: { padding: '12px', verticalAlign: 'middle' },
  deleteBtn: {
    backgroundColor: '#ef444422',
    color: '#f87171',
    border: '1px solid #ef444455',
    borderRadius: '6px',
    padding: '6px 12px',
    fontSize: '0.8rem',
    fontWeight: '600',
    cursor: 'pointer'
  }
};
