// Apresentação dos campos para a assistente: nomes legíveis e valores no formato brasileiro.

export const NOMES_CAMPOS: Record<string, string> = {
  nome: 'Nome', cpf: 'CPF', data_nascimento: 'Data de nascimento', sexo: 'Sexo',
  filiacao_pai: 'Pai', filiacao_mae: 'Mãe', naturalidade: 'Naturalidade', orgao_expedidor: 'Órgão expedidor',
  registro_geral: 'Registro geral (RG)', numero_registro: 'Nº de registro da CNH', categoria: 'Categoria',
  data_emissao: 'Data de emissão', data_expedicao: 'Data de expedição', validade: 'Validade',
  chave_acesso: 'Chave de acesso', emitente_cnpj: 'CNPJ do emitente', valor_total: 'Valor total',
  linha_digitavel: 'Linha digitável', valor: 'Valor', vencimento: 'Vencimento',
  beneficiario_documento: 'CNPJ do beneficiário', pagador_documento: 'CPF do pagador',
  cnpj_emissora: 'CNPJ da empresa', cliente: 'Cliente',
};

/** Campos longos ocupam a linha inteira. */
export const CAMPOS_LARGOS = new Set(['chave_acesso', 'linha_digitavel', 'nome', 'filiacao_pai', 'filiacao_mae']);

export function formatarValor(campo: string, valor: string): string {
  if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) {
    const [a, m, d] = valor.split('-');
    return `${d}/${m}/${a}`;
  }
  if (['valor', 'valor_total'].includes(campo) && /^\d+(\.\d+)?$/.test(valor)) {
    return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  if (campo === 'chave_acesso' && /^\d{44}$/.test(valor)) return valor.replace(/(\d{4})(?=\d)/g, '$1 ');
  if (campo === 'sexo') return valor === 'F' ? 'Feminino' : valor === 'M' ? 'Masculino' : valor;
  return valor;
}
