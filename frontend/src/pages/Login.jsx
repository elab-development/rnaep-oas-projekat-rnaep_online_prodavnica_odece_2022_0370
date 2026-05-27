import { useState } from 'react';
import { api } from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Login({ setUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      
      const res = await api.post('/users/login', { 
        email, 
        lozinka: password 
      });
      
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.korisnik)); 
      setUser(res.data.korisnik); 

      alert('Uspešna prijava!');
      navigate(res.data.korisnik.rola === 'administrator' ? '/panel' : '/');
    } catch (err) {
      alert('Pogrešan email ili lozinka.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white p-10 rounded-3xl shadow-2xl border border-pink-100">
        <h2 className="text-3xl font-serif font-bold text-slate-950 mb-2">Dobrodošli nazad</h2>
        <form onSubmit={handleLogin} className="space-y-5">
          <input type="email" placeholder="Email adresa" className="w-full p-4 border rounded-xl" onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Lozinka" className="w-full p-4 border rounded-xl" onChange={(e) => setPassword(e.target.value)} required />
          <button type="submit" className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold hover:bg-slate-800">Prijavi se</button>
        </form>
        <p className="mt-6 text-center text-slate-600">
          Nemaš nalog? <Link to="/register" className="text-purple-600 font-bold hover:underline">Registruj se</Link>
        </p>
      </div>
    </div>
  );
}