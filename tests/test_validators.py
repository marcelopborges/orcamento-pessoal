import pytest
from datetime import datetime
from core.validators import EmployeeDataValidator, DataValidationError


@pytest.fixture
def validator():
    return EmployeeDataValidator()

def test_validate_required_field(validator):
    data = {
        "CHAPA": "99999",
        "NOME": "MARCELO BORGES",
        "SITUACAO": "A",
        "FUNCAO": "8888",
        "DATA_ADMISSAO": "2023-01-01",
        "DATA_ADMISSAO_PTS" : "2023-01-01",
        "DATA_NASCIMENTO": "1980-01-01",
        "SESSAO": "01.01.1.01.01.001",
        "JORNADA": "220",                
        "CENTRO_CUSTO": "222222222"
    }
    with pytest.raises(DataValidationError, match="O campo obrigatório 'CPF' está ausente."):
        validator.validate(data)

def test_date_validator_accepts_brazilian_format(validator):
    """ 
    Testa se o validador de data aceita o formato DD/MM/YYYY. 
    """
    date_str = "28/10/1999"
    # O método a ser testado é o privado, pois a lógica está lá
    validated_date = validator._validate_date_format(date_str)
    assert isinstance(validated_date, datetime)
    assert validated_date.year == 1999
    assert validated_date.month == 10
    assert validated_date.day == 28