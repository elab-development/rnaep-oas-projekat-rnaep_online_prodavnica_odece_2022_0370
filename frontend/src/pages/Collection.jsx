import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import ProductCard from '../components/ProductCard'; 

// 1. Dodaj { user } ovde
export default function Collection({ user }) {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products');
        setProducts(response.data);
      } catch (error) {
        console.error("Greška pri učitavanju:", error);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <h1 className="text-4xl font-serif mb-10 text-slate-900">Naša Kolekcija</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map((p) => (
          // 2. Prosledi user={user} ovde
          <ProductCard key={p._id || p.id} product={p} user={user} />
        ))}
      </div>
      
      {products.length === 0 && <p>Nema proizvoda u kolekciji.</p>}
    </div>
  );
}