// src/components/ProductCard.jsx
import React from 'react';

export default function ProductCard({ product }) {
  
    const addToCart = async () => {
    try {
      // Šaljemo POST zahtev na cart servis
      await api.post(`/cart/1/items`, {
        product_id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1
      });
      alert("Proizvod je uspešno dodat u korpu!");
    } catch (error) {
      console.error("Greška pri dodavanju:", error);
      alert("Došlo je do greške. Proverite da li ste ulogovani.");
    }
  };

  // Mapiramo tvoje kategorije na proverene, stabilne slike
  const categoryImages = {
    'odeca': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80',
    'obuca': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',
    'dodaci': 'https://picsum.photos/id/175/400/300'
  };

  // Uzimamo kategoriju, pretvorimo u mala slova
  const cat = product.category ? product.category.toLowerCase().trim() : 'odeca';
  
  // Ako ne nađe kategoriju, koristi default sliku
  const imageUrl = categoryImages[cat] || categoryImages['odeca'];

  return (
    <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 hover:shadow-lg transition duration-300">
      <div className="h-48 bg-slate-100 rounded-xl mb-4 overflow-hidden">
        <img 
          src={imageUrl} 
          alt={product.name} 
          className="w-full h-full object-cover"
        />
      </div>
      <h3 className="text-lg font-bold text-slate-900">{product.name}</h3>
      <p className="text-purple-600 font-semibold">{product.price} RSD</p>
      <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded mt-2 inline-block">
        {product.category}
      </span>
    </div>
  );
}