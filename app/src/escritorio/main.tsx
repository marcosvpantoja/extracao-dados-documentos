import { createRoot } from 'react-dom/client';
import '../compartilhado/tokens.css';
import './escritorio.css';
import Escritorio from './Escritorio';

createRoot(document.getElementById('raiz')!).render(<Escritorio />);
