// src/components/Navbar.jsx
import { Link } from 'react-router-dom';
import { ShoppingBag, ShieldCheck } from 'lucide-react';

export default function Navbar({ user, logout }) {
  
  // Ova funkcija će pozvati funkciju 'logout' koju prosleđuješ iz App.jsx
  const onLogoutClick = () => {
    localStorage.removeItem('token');
    localStorage.clear();
    // Ako imaš prosleđen 'logout' kao prop, pozovi ga, inače osveži stranicu
    if (logout) {
      logout();
    } else {
      window.location.href = '/login';
    }
  };

  return (
    <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 px-8 py-4 flex justify-between items-center border-b border-slate-100">
      <Link to="/" className="flex items-center space-x-2">
        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-white font-serif font-bold italic">V</div>
        <span className="text-2xl font-serif font-black tracking-tight text-slate-950">VELURA</span>
      </Link>

      <div className="flex gap-8 font-medium text-slate-600">
        <Link to="/" className="hover:text-purple-600 transition">Početna</Link>
        <Link to="/kolekcija" className="hover:text-purple-600 transition">Kolekcija</Link>
        
        {/* Proveri da li je rola 'administrator' ili 'admin' */}
        {user?.rola === 'administrator' && (
          <Link to="/panel" className="flex items-center gap-1 text-purple-700 font-bold">
            <ShieldCheck size={18} /> Admin
          </Link>
        )}
      </div>

      <div className="flex items-center gap-4">
        <Link to="/cart" className="p-2 hover:bg-slate-100 rounded-full"><ShoppingBag size={22} /></Link>
        
        {user ? (
          <button 
            onClick={onLogoutClick} 
            className="px-4 py-2 bg-slate-100 rounded-full hover:bg-slate-200 transition"
          >
            Izloguj se
          </button>
        ) : (
          <Link to="/login" className="px-5 py-2 bg-slate-900 text-white rounded-full hover:bg-slate-800 transition">Prijava</Link>
        )}
      </div>
    </nav>
  );
}