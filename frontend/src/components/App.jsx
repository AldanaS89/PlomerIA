import { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import "./styles/global.css";

export default function App() {
  const [screen, setScreen] = useState("login"); // "login" | "dashboard"
  const [user, setUser] = useState(null);

  function handleLogin(userData) {
    setUser(userData);
    setScreen("dashboard");
  }

  function handleLogout() {
    setUser(null);
    setScreen("login");
  }

  return (
    <div className="app">
      {screen === "login" && <Login onLogin={handleLogin} />}
      {screen === "dashboard" && <Dashboard user={user} onLogout={handleLogout} />}
    </div>
  );
}
