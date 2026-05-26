import { useState } from 'react';
import { api } from '../api/axios';

export default function Admin() {
  const [product, setProduct] = useState({ 
    name: '', 
    price: '', 
    category: '', 
    description: '',
    is_active: true 
  });

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      
      await api.post('/products', product);
      alert('Proizvod "' + product.name + '" je uspešno dodat!');
      
    
      setProduct({ name: '', price: '', category: '', description: '', is_active: true });
    } catch (err) {
      console.error("Greška pri dodavanju:", err.response?.data);
      alert('Greška: ' + (err.response?.data?.detail || 'Proveri podatke i pokušaj ponovo.'));
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-10">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-serif font-bold text-slate-950 mb-2">Administracija proizvoda</h1>
        <p className="text-slate-600 mb-10">Popunite podatke o novom proizvodu koji želite dodati u ponudu.</p>
        
        <form onSubmit={handleAddProduct} className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 space-y-6">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">Naziv proizvoda</label>
            <input 
              className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none transition" 
              value={product.name}
              onChange={(e) => setProduct({...product, name: e.target.value})} 
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Cena (RSD)</label>
              <input 
                type="number" 
                className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none" 
                value={product.price}
                onChange={(e) => setProduct({...product, price: parseFloat(e.target.value)})} 
                required
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Kategorija</label>
              <input 
                className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none" 
                value={product.category}
                onChange={(e) => setProduct({...product, category: e.target.value})} 
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">Opis</label>
            <textarea 
              className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none" 
              rows="4"
              value={product.description}
              onChange={(e) => setProduct({...product, description: e.target.value})} 
            />
          </div>

          <button type="submit" className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold hover:bg-slate-800 transition transform active:scale-[0.99] shadow-lg">
            Dodaj proizvod u katalog
          </button>
        </form>
      </div>
    </div>
  );
}