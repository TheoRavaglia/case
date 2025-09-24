import { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import MetricsTable from './components/MetricsTable';
import { api } from './services/api';
import type { User, LoginCredentials } from './types';
import './App.css';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar se já tem token salvo
    const token = localStorage.getItem('token');
    if (token) {
      api.setToken(token);
      // Verificar se o token ainda é válido
      api.getCurrentUser()
        .then(userData => {
          setUser(userData);
        })
        .catch(() => {
          // Token inválido, remover
          localStorage.removeItem('token');
          api.setToken(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = async (credentials: LoginCredentials) => {
    const response = await api.login(credentials);
    localStorage.setItem('token', response.access_token);
    api.setToken(response.access_token);
    setUser(response.user);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    api.setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="container">
      {!user ? (
        <LoginForm onLogin={handleLogin} />
      ) : (
        <>
          <div className="user-info">
            <div>
              <strong>Bem-vindo, {user.name}</strong>
              <br />
              <small>{user.email} ({user.role})</small>
            </div>
            <button className="btn btn-danger" onClick={handleLogout}>
              Sair
            </button>
          </div>
          <MetricsTable user={user} />
        </>
      )}
    </div>
  );
}

export default App
