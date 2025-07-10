import pytest
from datetime import datetime, date # Garanta que 'date' também está importado, se for usado em fixtures ou testes
from core.entities import Funcionario # Importa a entidade Funcionario
from core.validators import ValidadorDadosFuncionario # Importa o validador de dados de funcionário

@pytest.fixture
def dados_funcionario_valido():
    """ 
    Fixture que retorna um exemplo "válido" de registro de funcionário para testes.
    """
    return {
        "CHAPA": "99999",
        "NOME": "MARCELO BORGES",
        "SITUACAO": "A",
        "CODIGO_FUNCAO": "8888",
        "DATA_ADMISSAO": "2023-01-01",
        "DATA_ADMISSAO_PTS": "2023-01-01",
        "DATA_NASCIMENTO": "1990-01-01",
        "SECAO": "01.01.1.01.01.001",
        "CARGA_HORARIA_MENSAL": "220",
        "CPF": "01776476123",
        "CENTRO_CUSTO": "222222222",        
        "EMPRESA": "Empresa Teste",
        "EQUIPE": "Equipe Teste",
        "FUNCAO": "Funcao Teste", 
        "VALOR_VALE_TRANSPORTE_MENSAL": 100.0,
        "VALOR_VALE_REFEICAO_MENSAL": 200.0,
        "PLANO_SAUDE_MENSAL": 50.0,
        "OUTROS_BENEFICIOS_MENSAIS": 10.0
    }

def test_criar_funcionario_a_partir_de_dados_validados(dados_funcionario_valido):
    """
    Testa se é possível criar uma instância de Funcionario
    a partir de um dicionário de dados válidos.
    """
    # Arrange
    validador = ValidadorDadosFuncionario()    
    dados_validados = validador.validate(dados_funcionario_valido)

    # Act    
    funcionario = Funcionario(**dados_validados)

    # Assert
    assert funcionario.nome == "MARCELO BORGES"
    assert funcionario.chapa == "99999"
    assert isinstance(funcionario.data_admissao, datetime)
    assert funcionario.data_admissao.year == 2023

def test_funcionario_ativo_retorna_verdadeiro(dados_funcionario_valido):
    """
    Testa se is_active() retorna True para um funcionário com situação 'A'.
    """
    validador = ValidadorDadosFuncionario()    
    dados_para_teste = dados_funcionario_valido.copy() 
    dados_para_teste["SITUACAO"] = "A"
    dados_validados = validador.validate(dados_para_teste)
    funcionario = Funcionario(**dados_validados)
    assert funcionario.is_active() is True

def test_funcionario_inativo_retorna_falso(dados_funcionario_valido):
    """
    Testa se is_active() retorna False para um funcionário com situação diferente de 'A'.
    """
    validador = ValidadorDadosFuncionario()    
    dados_para_teste = dados_funcionario_valido.copy()
    dados_para_teste["SITUACAO"] = "F"
    dados_validados = validador.validate(dados_para_teste)
    funcionario = Funcionario(**dados_validados)
    assert funcionario.is_active() is False