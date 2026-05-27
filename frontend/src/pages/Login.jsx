// src/pages/Login.jsx
import { useState } from 'react';
import { api } from '../api/axios';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // 1. Šaljemo podatke na server
      const res = await api.post('/users/login', { email, password });
      
      // 2. Čuvamo token u localStorage da ga kasnije koristimo za autorizaciju
      localStorage.setItem('token', res.data.token);
      
      // 3. Provera uloge (ovo podrazumeva da tvoj server vraća { token: "...", role: "admin" })
      // Ako tvoj server ne vraća role, možda ćeš morati da dekodiraš token
      const userRole = res.data.role; 

      alert('Uspešna prijava!');

      // 4. Pametno preusmeravanje
      if (userRole === 'admin') {
        navigate('/panel'); // Ako je admin, šaljemo ga u Admin panel
      } else {
        navigate('/'); // Ako je kupac, šaljemo ga na početnu
      }
      
    } catch (err) {
      console.error("Greška pri prijavi:", err);
      alert('Pogrešan email ili lozinka.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white p-10 rounded-3xl shadow-2xl border border-pink-100 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-purple-600 to-pink-500"></div>
        <h2 className="text-3xl font-serif font-bold text-slate-950 mb-2">Dobrodošli nazad</h2>
        <p className="text-slate-500 mb-8">Prijavite se na Velura nalog.</p>
        
        <form onSubmit={handleLogin} className="space-y-5">
          <input 
            type="email" 
            placeholder="Email adresa" 
            className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)} 
            required
          />
          <input 
            type="password" 
            placeholder="Lozinka" 
            className="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500 outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)} 
            required
          />
          <button type="submit" className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold hover:bg-slate-800 transition">
            Prijavi se
          </button>
        </form>
      </div>
    </div>
  );
}