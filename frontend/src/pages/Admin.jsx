import { useState } from 'react';
import { api } from '../api/axios';

export default function Admin() {
  const [product, setProduct] = useState({ name: '', price: '', category: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: product.name,
        price: Number(product.price),
        category: product.category
      };
      
      await api.post('/products', payload);
      alert('Proizvod uspešno dodat!');
      setProduct({ name: '', price: '', category: '' });
    } catch (error) {
      console.error("Greška:", error);
      alert('Došlo je do greške pri dodavanju.');
    }
  };

  return (
    <div className="p-10 max-w-2xl mx-auto">
      <h2 className="text-3xl font-serif text-slate-900 mb-8">Dodaj novi proizvod</h2>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-3xl shadow-lg border border-pink-100 flex flex-col gap-4">
        <input 
          placeholder="Ime proizvoda" 
          className="p-3 border rounded-xl"
          value={product.name}
          onChange={(e) => setProduct({...product, name: e.target.value})}
        />
        <input 
          type="number" 
          placeholder="Cena (RSD)" 
          className="p-3 border rounded-xl"
          value={product.price}
          onChange={(e) => setProduct({...product, price: e.target.value})}
        />
        <input 
          placeholder="Kategorija" 
          className="p-3 border rounded-xl"
          value={product.category}
          onChange={(e) => setProduct({...product, category: e.target.value})}
        />
        <button type="submit" className="bg-slate-900 text-white py-3 rounded-xl hover:bg-slate-800 transition">
          Sačuvaj proizvod
        </button>
      </form>
    </div>
  );
}