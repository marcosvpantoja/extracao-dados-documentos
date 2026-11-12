import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Revisao, { ordenarParaRevisao } from './Revisao';

const campos = {
  cpf: { valor: '644.836.782-99', origem: 'padrão', validado: true },
  nome: { valor: 'NATALIA RIBEIRO', origem: 'rótulo', validado: false },
  filiacao_mae: { valor: 'CARLA RIBEIRO', origem: 'ia', validado: false },
};

describe('tela de revisão', () => {
  it('campos da IA vêm primeiro e os conferidos por último (HU-05)', () => {
    expect(ordenarParaRevisao(campos).map(([k]) => k)).toEqual(['filiacao_mae', 'nome', 'cpf']);
  });

  it('confirmar os demais preserva o que já foi recusado', async () => {
    const onDecidir = vi.fn();
    render(<Revisao titulo="CNH" tipo="CNH" faces={{}} campos={campos} decisoes={{ nome: 'recusado' }} onDecidir={onDecidir} onFechar={() => {}} />);
    await userEvent.click(screen.getByRole('button', { name: /Confirmar os demais \(2\)/ }));
    expect(onDecidir).toHaveBeenCalledWith({ filiacao_mae: 'confirmado', nome: 'recusado', cpf: 'confirmado' });
  });
});
