import { api } from '../api/axios';
import { ShoppingBag } from 'lucide-react';

export default function ProductCard({ product }) {
  
  const addToCart = async () => {
    try {
      
      await api.post(`/cart/1/items`, {
        product_id: product.id,
        quantity: 1
      });
      alert("Dodato u korpu!");
    } catch (error) {
      console.error("Greška pri dodavanju:", error);
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
    <div className="bg-white p-4 rounded-3xl shadow-sm hover:shadow-xl transition border border-slate-100">
      <img src={imageUrl} className="h-48 w-full object-cover rounded-2xl mb-4" alt={product.name} />
      <h3 className="font-bold text-slate-900">{product.name}</h3>
      <p className="text-purple-600 font-bold mb-4">{product.price} RSD</p>
      
      <button 
        onClick={addToCart}
        className="w-full bg-slate-900 text-white py-3 rounded-xl hover:bg-slate-800 transition flex items-center justify-center gap-2"
      >
        <ShoppingBag size={18} /> Dodaj u korpu
      </button>
    </div>
  );
}