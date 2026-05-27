import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Register from './pages/Register';
import Collection from './pages/Collection';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';


function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="bg-slate-50 min-h-screen">
        <Navbar user={user} logout={handleLogout} />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/panel" element={<Admin user={user} />} />
            <Route path="/login" element={<Login setUser={setUser} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/cart" element={<Cart user={user} />} />
            <Route path="/checkout" element={<Checkout user={user} />} />
            <Route path="/kolekcija" element={<Collection user={user} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;