import { createRoot } from 'react-dom/client';
import '../compartilhado/tokens.css';
import './captura.css';
import Captura from './Captura';

createRoot(document.getElementById('raiz')!).render(<Captura />) // sem StrictMode: o pareamento abre o canal uma única vez;
