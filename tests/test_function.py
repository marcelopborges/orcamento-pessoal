import pytest
from core.validators import FunctionDataValidator, DataValidationError
from core.entities import Funcao

@pytest.fixture
def validator():
    return FunctionDataValidator()

def test_validate_valid_function_data(validator):
    """ 
    Testa se dados válidos para uma função passam na validação. 
    """
    data = {
        "CODIGO_FUNCAO": "4003",
        "NOME_FUNCAO": "ANALISTA ADMINISTRATIVO I",
        "SALARIO": "5202.76"
    }
    validated_data = validator.validate(data)

    assert validated_data["codigo_funcao"] == "4003" 
    assert validated_data["nome_funcao"] == "ANALISTA ADMINISTRATIVO I"
    assert validated_data["salario"] == 5202.76

def test_validate_invalid_salary_format(validator):
    """
      Testa se um salário com formato inválido falha. 
    """
    data = {
        "CODIGO_FUNCAO": "4003",
        "NOME_FUNCAO": "ANALISTA ADMINISTRATIVO I",
        "SALARIO": "salário invalido"
    }
    with pytest.raises(DataValidationError, match="O campo 'SALARIO' deve ser um número válido."):
        validator.validate(data)

def test_create_function_entity():
    """ 
    Testa a criação da entidade Funcao. 
    """
    funcao = Funcao(
        codigo_funcao="4003",
        nome_funcao="ANALISTA ADMINISTRATIVO I",
        salario=5202.76
    )
    assert funcao.codigo_funcao == "4003"
    assert funcao.salario == 5202.76