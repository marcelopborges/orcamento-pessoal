import pytest
from core.validators import ValidadorDadosFuncionario, DataValidationError
import re

# Fixture para criar o validador
@pytest.fixture
def validator():
    return ValidadorDadosFuncionario()


# Teste para CPFs válidos
@pytest.mark.parametrize("cpf", [
    "123.456.789-09",
    "935.411.347-80",  
])
def test_valid_CPF(validator, cpf):
    # Validação deve retornar o CPF limpo (somente números)
    assert validator._validate_CPF_format(cpf) == cpf.replace(".", "").replace("-", "")


# Teste para casos borda (edge cases)
@pytest.mark.parametrize("cpf,expected_error", [
    ("", "O CPF deve conter 11 dígitos."),  # CPF vazio
    ("   ", "O CPF deve conter 11 dígitos."),  # Somente espaços
    ("123.456.789-0A", "O CPF deve conter apenas números ou os formatos válidos (XXX.XXX.XXX-XX)."),
    ("@12345678909", "O CPF deve conter apenas números ou os formatos válidos (XXX.XXX.XXX-XX).")
])
def test_edge_cases_CPF(validator, cpf, expected_error):
    with pytest.raises(DataValidationError, match=re.escape(expected_error)): 
        validator._validate_CPF_format(cpf)


# Teste para comprimento de CPF inválido
def test_invalid_CPF_length(validator):
    with pytest.raises(DataValidationError, match="O CPF deve conter 11 dígitos."): 
        validator._validate_CPF_format("123.456-78")


# Teste para CPFs inválidos (dígitos repetidos)
@pytest.mark.parametrize("cpf,expected_error", [
    ("111.111.111-11", "O CPF fornecido é inválido."),
    ("222.222.222-22", "O CPF fornecido é inválido."),
])
def test_invalid_CPF(validator, cpf, expected_error):
    with pytest.raises(DataValidationError, match=re.escape(expected_error)):  # Corrigida a exceção
        validator._validate_CPF_format(cpf)


# Teste para CPFs com dígitos verificadores incorretos
def test_invalid_check_digits(validator):
    with pytest.raises(DataValidationError, match="Os dígitos verificadores do CPF são inválidos."):  # Corrigida a exceção
        validator._validate_CPF_format("123.456.789-00")