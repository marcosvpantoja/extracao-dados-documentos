import { describe, expect, it } from 'vitest';
import { formatarValor } from './formatar';

describe('formatação para a assistente', () => {
  it('chave da NF-e em grupos de 4', () => {
    expect(formatarValor('chave_acesso', '13260929989158000118550010004347171918294748'))
      .toBe('1326 0929 9891 5800 0118 5500 1000 4347 1719 1829 4748');
  });
  it('valor em reais e data no formato brasileiro', () => {
    expect(formatarValor('valor_total', '4763.70').replace(/\s/g, ' ')).toBe('R$ 4.763,70');
    expect(formatarValor('vencimento', '2027-03-16')).toBe('16/03/2027');
  });
});
