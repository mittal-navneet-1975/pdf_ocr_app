import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log("Frontend URL:", window.location.href);
console.log("Hostname:", window.location.hostname);
console.log("Origin:", window.location.origin);
console.log("Pathname:", window.location.pathname);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
