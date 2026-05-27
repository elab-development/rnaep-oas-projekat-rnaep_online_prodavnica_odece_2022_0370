import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Collection from './pages/Collection';
import Cart from './pages/Cart'; // Nova stranica za korpu

function App() {
  // Stanje korisnika - proveravamo da li je ulogovan pri učitavanju
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Ovde možeš dodati logiku za čitanje podataka o korisniku iz tokena (JWT decode)
      setUser({ ime: "Admin", rola: "administrator" });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="bg-slate-50 min-h-screen">
        {/* Navbar dobija informacije o korisniku i funkciju za odjavu */}
        <Navbar user={user} logout={handleLogout} />
        
        {/* Sve stranice aplikacije */}
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/kolekcija" element={<Collection />} />
            <Route path="/panel" element={<Admin />} />
            <Route path="/login" element={<Login />} />
            <Route path="/cart" element={<Cart />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;