import { useState } from 'react';
import { api } from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [formData, setFormData] = useState({ email: '', password: '', ime: '', prezime: '' });
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Koristimo tvoju postojeću putanju u Gateway-u
      await api.post('/users/register', {
        email: formData.email,
        lozinka: formData.password,
        ime: formData.ime,
        prezime: formData.prezime
      });
      alert('Registracija uspešna!');
      navigate('/login');
    } catch (err) {
      alert('Greška pri registraciji.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white p-10 rounded-3xl shadow-xl">
        <h2 className="text-3xl font-bold mb-6">Registracija</h2>
        <form onSubmit={handleRegister} className="space-y-4">
          <input placeholder="Ime" className="w-full p-4 border rounded-xl" onChange={(e) => setFormData({...formData, ime: e.target.value})} required />
          <input placeholder="Prezime" className="w-full p-4 border rounded-xl" onChange={(e) => setFormData({...formData, prezime: e.target.value})} required />
          <input type="email" placeholder="Email" className="w-full p-4 border rounded-xl" onChange={(e) => setFormData({...formData, email: e.target.value})} required />
          <input type="password" placeholder="Lozinka" className="w-full p-4 border rounded-xl" onChange={(e) => setFormData({...formData, password: e.target.value})} required />
          <button className="w-full bg-slate-900 text-white py-4 rounded-xl font-bold">Registruj se</button>
        </form>
        <p className="mt-6 text-center">Već imaš nalog? <Link to="/login" className="text-purple-600 font-bold">Prijavi se</Link></p>
      </div>
    </div>
  );
}