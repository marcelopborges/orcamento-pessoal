# tests/test_employee.py

import pytest
from datetime import datetime
# A linha abaixo vai dar erro, pois o arquivo e a classe ainda não existem. É o esperado!
from core.entities import Employee
from core.validators import EmployeeDataValidator

@pytest.fixture
def valid_employee_data():
    """ 
        Exemplo "válido" de registro de funcionário.
    """
    return {
        "CHAPA": "99999",
        "NOME": "MARCELO BORGES",
        "SITUACAO": "A",
        "CODIGO_FUNCAO": "8888",
        "DATA_ADMISSAO": "2023-01-01",
        "DATA_ADMISSAO_PTS": "2023-01-01",
        "DATA_NASCIMENTO": "1980-01-01",
        "SESSAO": "01.01.1.01.01.001",
        "JORNADA": "220",
        "CPF": "93541134780",
        "CENTRO_CUSTO": "222222222"
    }

def test_create_employee_from_validated_data(valid_employee_data):
    """
    Testa se é possível criar uma instância de Employee
    a partir de um dicionário de dados válidos.
    """
    # Arrange
    validator = EmployeeDataValidator()
    # Primeiro, validamos os dados brutos
    validated_data = validator.validate(valid_employee_data)

    # Act
    # Agora, tentamos criar a nossa entidade com os dados validados
    employee = Employee(**validated_data)

    # Assert
    assert employee.nome == "MARCELO BORGES"
    assert employee.chapa == "99999"
    assert isinstance(employee.data_admissao, datetime)
    assert employee.data_admissao.year == 2023

def test_is_active_returns_true_for_active_employee(valid_employee_data):
    """
    Testa se is_active() retorna True para um funcionário com situação 'A'.
    """
    validator = EmployeeDataValidator()
    valid_employee_data["SITUACAO"] = "A"
    validated_data = validator.validate(valid_employee_data)
    employee = Employee(**validated_data)
    assert employee.is_active() is True

def test_is_active_returns_false_for_inactive_employee(valid_employee_data):
    """
    Testa se is_active() retorna False para um funcionário com situação diferente de 'A'.
    """
    validator = EmployeeDataValidator()
    valid_employee_data["SITUACAO"] = "F"
    validated_data = validator.validate(valid_employee_data)
    employee = Employee(**validated_data)
    assert employee.is_active() is False