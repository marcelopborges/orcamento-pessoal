# tests/test_validators.py

import pytest
from datetime import datetime
from core.validators import ValidadorDadosFuncionario, DataValidationError

@pytest.fixture
def validador_funcionario():
    """
    Fixture que retorna uma instância do ValidadorDadosFuncionario.
    """
    return ValidadorDadosFuncionario()

def test_validador_funcionario_campo_obrigatorio_ausente_falha(validador_funcionario):
    """
    Testa se o validador de funcionário falha quando um campo obrigatório está ausente.
    """
    # Dados de exemplo com um campo obrigatório (CPF) ausente
    dados_funcionario_incompleto = {
        "CHAPA": "99999",
        "NOME": "MARCELO BORGES",
        "SITUACAO": "A",
        "CODIGO_FUNCAO": "8888", # Corrigido de "FUNCAO" para "CODIGO_FUNCAO"
        "DATA_ADMISSAO": "2023-01-01",
        "DATA_ADMISSAO_PTS": "2023-01-01",
        "DATA_NASCIMENTO": "1980-01-01",
        "SECAO": "01.01.1.01.01.001",
        "CARGA_HORARIA_MENSAL": "220",                
        "CENTRO_CUSTO": "222222222",        
        "EMPRESA": "Empresa Teste",
        "EQUIPE": "Equipe Teste",
        "FUNCAO": "Funcao Teste",
        "VALOR_VALE_TRANSPORTE_MENSAL": 150.0,
        "VALOR_VALE_REFEICAO_MENSAL": 400.0,
        "PLANO_SAUDE_MENSAL": 300.0,
        "OUTROS_BENEFICIOS_MENSAIS": 0.0
    }
    
    with pytest.raises(DataValidationError, match="O campo obrigatório 'CPF' está ausente."):
        validador_funcionario.validate(dados_funcionario_incompleto)

def test_validador_data_aceita_formato_brasileiro(validador_funcionario):
    """ 
    Testa se o validador de data aceita o formato DD/MM/YYYY. 
    """
    data_string_brasileira = "28/10/1999"    
    data_validada = validador_funcionario._validate_date_format(data_string_brasileira)
    assert isinstance(data_validada, datetime)
    assert data_validada.year == 1999
    assert data_validada.month == 10
    assert data_validada.day == 28