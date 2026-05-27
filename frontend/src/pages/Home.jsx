// src/pages/Home.jsx
import { useEffect, useState } from 'react';
import { api } from '../api/axios';
import { ShoppingBag, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard'; // Uvozimo našu karticu

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get('/products')
      .then(res => {
        setProducts(res.data.slice(0, 4)); // Uzimamo samo prva 4 za početnu
        setLoading(false);
      })
      .catch(err => {
        console.error("Greška pri učitavanju:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex flex-col items-center min-h-screen bg-velura-50">
      
      {/* 1. HERO SEKCIJA - Tvoja originalna */}
      <header className="w-full h-[85vh] bg-velura-hero flex flex-col items-center justify-center text-center p-8 relative overflow-hidden">
        <div className="absolute -top-20 -left-20 w-80 h-80 bg-velura-purple-light/50 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-velura-100/70 rounded-full blur-3xl"></div>

        <div className="relative z-10 max-w-4xl">
          <h1 className="text-8xl md:text-9xl font-serif text-velura-900 mb-6 tracking-tighter leading-none">
            V E L U R A
          </h1>
          <p className="text-2xl md:text-3xl text-velura-800 italic font-light leading-relaxed max-w-2xl mx-auto mb-12">
            Tvoj stil, tvoja priča, tvoja elegancija – u svakom šavu.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-velura-900 hover:bg-black text-white px-10 py-4 rounded-full font-semibold transition-all shadow-xl hover:-translate-y-0.5 flex items-center gap-2 group text-lg">
              Nova Kolekcija
              <ChevronRight className="group-hover:translate-x-1 transition-transform" size={20} />
            </button>
            <button className="bg-white hover:bg-velura-100 text-velura-900 px-10 py-4 rounded-full font-semibold transition-all shadow-md text-lg">
              Saznaj više
            </button>
          </div>
        </div>
      </header>

      {/* 2. GRID PROIZVODA - Sada koristi ProductCard */}
      <section className="max-w-7xl w-full p-10 md:p-16">
        <div className="flex justify-between items-center mb-12 border-b border-velura-200 pb-6">
          <h2 className="text-4xl font-serif text-velura-900 font-semibold tracking-tight">
            Izdvojeno iz ponude
          </h2>
          <Link to="/kolekcija" className="text-velura-700 hover:text-velura-500 font-medium flex items-center gap-1 group">
            Pogledaj sve
            <ChevronRight size={18} className="group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {loading ? (
          <div className="text-center text-velura-400 py-20">Učitavanje prelepih stvari...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            {products.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}