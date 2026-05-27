import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/axios';

// OVDE DODAJ { user } U ZAGRADU:
export default function Cart({ user }) { 
  const [cart, setCart] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) return; 

    api.get(`/cart/${user.id}`) 
      .then(res => {
        console.log("ODGOVOR SERVERA:", res.data); // OVO JE KLJUČNO
        setCart(res.data);
      })
      .catch(err => {
        console.error("GREŠKA:", err.response ? err.response.data : err.message);
      });
  }, [user]);

  return (
    <div className="p-10 max-w-4xl mx-auto">
      <h2 className="text-3xl font-serif mb-8">Tvoja korpa</h2>
      {!cart || !cart.stavke || cart.stavke.length === 0 ? <p>Korpa je prazna.</p> : (
        <div className="space-y-4">
          {cart.stavke.map(item => (
            <div key={item.stavka_id} className="flex justify-between p-4 bg-white rounded-xl shadow-sm border">
              <div>
                <p className="font-bold">{item.naziv}</p>
                <p className="text-sm text-slate-500">Kol: {item.kolicina}</p>
              </div>
              <p className="font-bold">{item.cijena_po_komadu * item.kolicina} RSD</p>
            </div>
          ))}
          <div className="pt-6 border-t mt-4 flex justify-between items-center">
            <h3 className="text-xl font-bold">Ukupno: {cart.ukupno} RSD</h3>
            <button 
              onClick={() => navigate('/checkout')}
              className="bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition"
            >
              Završi nabavku
            </button>
          </div>
        </div>
      )}
    </div>
  );
}