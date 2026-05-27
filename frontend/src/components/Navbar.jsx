import { Link } from 'react-router-dom';
import { ShoppingBag, ShieldCheck } from 'lucide-react';

export default function Navbar({ user, logout }) {
  return (
    <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 px-8 py-4 flex justify-between items-center border-b border-slate-100">
     
      <Link to="/" className="flex items-center space-x-2">
        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-white font-serif font-bold italic">V</div>
        <span className="text-2xl font-serif font-black tracking-tight text-slate-950">VELURA</span>
      </Link>

      <div className="flex gap-8 font-medium text-slate-600">
        <Link to="/" className="hover:text-purple-600 transition">Početna</Link>
        <Link to="/kolekcija" className="hover:text-purple-600 transition">Kolekcija</Link>
        
        {user?.rola === 'administrator' && (
          <Link to="/panel" className="flex items-center gap-1 text-purple-700 font-bold hover:text-purple-900 transition">
            <ShieldCheck size={18} /> Admin
          </Link>
        )}
      </div>

      <div className="flex items-center gap-4">
        <Link to="/cart" className="p-2 hover:bg-slate-100 rounded-full transition"><ShoppingBag size={22} /></Link>
        
        {user ? (
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-700">Zdravo, <span className="font-bold">{user.ime}</span></span>
            <button 
              onClick={logout} 
              className="px-4 py-2 bg-slate-100 rounded-full hover:bg-slate-200 transition text-sm font-bold"
            >
              Odjava
            </button>
          </div>
        ) : (
          <Link to="/login" className="px-5 py-2 bg-slate-900 text-white rounded-full hover:bg-slate-800 transition text-sm font-bold">Prijava</Link>
        )}
      </div>
    </nav>
  );
}