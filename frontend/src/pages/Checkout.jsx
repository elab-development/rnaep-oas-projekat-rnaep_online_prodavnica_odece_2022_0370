import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/axios';

export default function Checkout() {
  const [formData, setFormData] = useState({ adresa_isporuke: '', email: '' });
  const navigate = useNavigate();

  const handleConfirm = async (e) => {
    e.preventDefault();
    try {
      await api.post('/orders/1', formData);
      alert("Narudžbina uspešno kreirana!");
      navigate('/');
    } catch (err) {
      console.error(err);
      alert("Došlo je do greške pri kreiranju narudžbine.");
    }
  };

  return (
    <div className="p-10 max-w-lg mx-auto bg-white rounded-2xl shadow-sm border">
      <h2 className="text-2xl font-serif mb-6">Podaci za dostavu</h2>
      <form onSubmit={handleConfirm} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700">Adresa</label>
          <input 
            required
            className="w-full p-3 border rounded-lg" 
            placeholder="Unesite adresu..."
            onChange={e => setFormData({...formData, adresa_isporuke: e.target.value})}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input 
            required
            type="email"
            className="w-full p-3 border rounded-lg" 
            placeholder="vasa@email.com"
            onChange={e => setFormData({...formData, email: e.target.value})}
          />
        </div>
        <button 
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-bold"
        >
          Potvrdi narudžbinu
        </button>
      </form>
    </div>
  );
}