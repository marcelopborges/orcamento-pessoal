import pytest
from core.validators import ValidadorDadosCargo, DataValidationError
from core.entities import Cargo

@pytest.fixture
def validador_cargo():
    """
    Fixture que retorna uma instância do ValidadorDadosCargo.
    """
    return ValidadorDadosCargo()

@pytest.fixture
def dados_cargo_validos():
    """
    Fixture que retorna um dicionário de dados válidos para um Cargo.
    """
    return {
        "CODIGO_FUNCAO": "4003",
        "NOME_FUNCAO": "ANALISTA ADMINISTRATIVO I",
        "SALARIO": "5202.76" 
    }

def test_validador_cargo_valida_dados_corretamente(validador_cargo, dados_cargo_validos):
    """
    Testa se o validador de Cargo aceita dados válidos e os formata corretamente.
    """
    dados_validados = validador_cargo.validate(dados_cargo_validos)

    assert dados_validados["codigo_funcao"] == "4003"
    assert dados_validados["nome_funcao"] == "ANALISTA ADMINISTRATIVO I"
    assert dados_validados["salario"] == 5202.76

def test_validador_cargo_rejeita_salario_invalido(validador_cargo, dados_cargo_validos):
    """
    Testa se o validador de Cargo rejeita um salário com formato inválido.
    """    
    dados_invalidos = dados_cargo_validos.copy()
    dados_invalidos["SALARIO"] = "salário invalido"
    
    with pytest.raises(DataValidationError, match="O campo 'SALARIO' deve ser um número válido."):
        validador_cargo.validate(dados_invalidos)

def test_criacao_entidade_cargo_com_dados_validos():
    """
    Testa a criação da entidade Cargo a partir de dados válidos.
    """
    cargo = Cargo(
        codigo_funcao="4003",
        nome_funcao="ANALISTA ADMINISTRATIVO I",
        salario=5202.76
    )
    assert cargo.codigo_funcao == "4003"
    assert cargo.salario == 5202.76