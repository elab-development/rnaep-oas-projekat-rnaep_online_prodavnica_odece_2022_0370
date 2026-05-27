import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import ProductCard from '../components/ProductCard';

export default function Collection({ user }) {
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [categories, setCategories] = useState(['SVE']);
  const [activeCategory, setActiveCategory] = useState('SVE');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/products').then(res => {
      const data = res.data;
      setProducts(data);
      setFiltered(data);
      const cats = ['SVE', ...new Set(data.map(p => p.category.toUpperCase()))];
      setCategories(cats);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleFilter = (cat) => {
    setActiveCategory(cat);
    setFiltered(cat === 'SVE' ? products : products.filter(p => p.category.toUpperCase() === cat));
  };

  return (
    <div className="min-h-screen bg-white pt-14">
      {/* Page header */}
      <div className="border-b border-neutral-200 px-6 py-8">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h1 className="text-4xl font-serif">Kolekcija</h1>

          {/* Category filter */}
          <div className="flex items-center gap-6 flex-wrap">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => handleFilter(cat)}
                className={`text-xs tracking-widest uppercase pb-0.5 transition ${
                  activeCategory === cat
                    ? 'border-b border-black text-black'
                    : 'text-neutral-400 hover:text-black'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 py-10">
        <p className="text-xs text-neutral-400 tracking-wide mb-8 uppercase">
          {filtered.length} {filtered.length === 1 ? 'proizvod' : 'proizvoda'}
        </p>

        {loading ? (
          <div className="text-center py-32 text-xs tracking-widest uppercase text-neutral-300">
            Učitavanje...
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-32 text-xs tracking-widest uppercase text-neutral-300">
            Nema proizvoda
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-14">
            {filtered.map(p => (
              <ProductCard key={p.id} product={p} user={user} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
