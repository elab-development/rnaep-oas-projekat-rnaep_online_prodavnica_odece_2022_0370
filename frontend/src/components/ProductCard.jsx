import React from 'react';
import { api } from '../api/axios';

export default function ProductCard({ product, user }) {
  const addToCart = async () => {
    // 1. Provera: ako user ne postoji, ne dozvoljavaj dodavanje
    if (!user) {
      alert("Morate biti ulogovani da biste dodali proizvod u korpu!");
      return;
    }

    try {
      // 2. Sada koristimo user.id
      await api.post(`/cart/${user.id}/items`, {
        proizvod_id: product.id || product._id,
        naziv_proizvoda: product.name,
        velicina: "M", 
        boja: "Standardna",
        kolicina: 1,
        cijena_po_komadu: parseFloat(product.price)
      });
      
      alert("Proizvod je uspešno dodat u korpu!");
      window.location.href = '/cart'; 
    } catch (error) {
      console.error("Greška:", error);
      alert("Došlo je do greške pri dodavanju.");
    }
  };

  const categoryImages = {
    'odeca': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80',
    'obuca': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',
    'dodaci': 'https://picsum.photos/id/175/400/300'
  };

  const cat = product.category ? product.category.toLowerCase().trim() : 'odeca';
  const imageUrl = categoryImages[cat] || categoryImages['odeca'];

  return (
    <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 hover:shadow-lg transition duration-300">
      <div className="h-48 bg-slate-100 rounded-xl mb-4 overflow-hidden">
        <img src={imageUrl} alt={product.name} className="w-full h-full object-cover" />
      </div>
      <h3 className="text-lg font-bold text-slate-900">{product.name}</h3>
      <p className="text-purple-600 font-semibold">{product.price} RSD</p>
      <button 
        onClick={addToCart}
        className="mt-4 w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition"
      >
        Dodaj u korpu
      </button>
    </div>
  );
}