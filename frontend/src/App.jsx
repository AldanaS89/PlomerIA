import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Registro from './pages/Registro';
import HomeCliente from './pages/HomeCliente';
import DashboardPlomero from './pages/DashboardPlomero';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/cliente" element={<HomeCliente />} />
        <Route path="/plomero" element={<DashboardPlomero />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;