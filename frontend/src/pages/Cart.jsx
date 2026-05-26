// src/pages/Cart.jsx
import { useEffect, useState } from 'react';
import { api } from '../api/axios';

export default function Cart() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    
    api.get('/cart/1/items')
      .then(res => setItems(res.data))
      .catch(err => console.error("Greška pri učitavanju korpe:", err));
  }, []);

  return (
    <div className="p-10 max-w-4xl mx-auto">
      <h2 className="text-3xl font-serif mb-8">Tvoja korpa</h2>
      {items.length === 0 ? <p>Korpa je prazna.</p> : (
        <div className="space-y-4">
          {items.map(item => (
            <div key={item.id} className="flex justify-between p-4 bg-white rounded-xl shadow-sm border">
              <span>{item.name}</span>
              <span>{item.price} RSD</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}