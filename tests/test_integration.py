import pytest
from datetime import date
from core.entities import Employee, Funcao, GlobalConfig, EmployeeMonthlyInput
from core.validators import EmployeeDataValidator, FunctionDataValidator
from core.services import PayrollService
from core.payroll_rules import calculate_percentage_bonus
from core.config import get_historical_value

# Em tests/test_integration.py

def test_full_process_from_raw_data():
    """
    Testa o fluxo completo com dados reais simulados do Excel.
    """
    # ARRANGE - PARTE 1: SIMULANDO SEUS DADOS REAIS
    raw_employee_data = [
        {
            "CHAPA": "03494", "NOME": "GERALDO CANDIDO DE SOUSA", "SITUACAO": "A",
            "CODIGO_FUNCAO": "4206", "DATA_ADMISSAO": "15/04/2002",
            "DATA_ADMISSAO_PTS": "15/04/2002",
            "SESSAO": "01.01.4.10.01.005", "JORNADA": "220", "CENTRO_CUSTO": "104101205",
            # Adicionando os campos que faltam com dados fictícios
            "CPF": "01776476123", "DATA_NASCIMENTO": "01/01/1980"
        },
        {
            "CHAPA": "04694", "NOME": "MARCOS TEIXEIRA MACHADO", "SITUACAO": "A",
            "CODIGO_FUNCAO": "4151", "DATA_ADMISSAO": "03/07/2007",
            "DATA_ADMISSAO_PTS": "03/07/2007",
            "SESSAO": "01.01.4.11.02.000", "JORNADA": "150", "CENTRO_CUSTO": "104101801",
            # Adicionando os campos que faltam com dados fictícios
            "CPF": "01776476123", "DATA_NASCIMENTO": "01/01/1985"
        }
    ]

    raw_function_data = [
        {"CODIGO_FUNCAO": "4206", "NOME_FUNCAO": "FUNCAO DO GERALDO", "SALARIO": "5500.00"},
        {"CODIGO_FUNCAO": "4151", "NOME_FUNCAO": "FUNCAO DO MARCOS", "SALARIO": "4200.50"}
    ]
    # (Usei salários fictícios, substitua pelos valores reais se os tiver)

    # ARRANGE - PARTE 2: CONFIGURAÇÕES
    global_config = GlobalConfig(calculation_date=date(2025, 4, 30), minimum_wage=1918.00, insalubrity_percent=0.40)
    default_monthly_input = EmployeeMonthlyInput()

    # ACT - A LÓGICA DE ORQUESTRAÇÃO (exatamente como antes)
    employee_validator = EmployeeDataValidator()
    function_validator = FunctionDataValidator()
    service = PayrollService()

    validated_employees = [Employee(**employee_validator.validate(row)) for row in raw_employee_data]
    validated_functions = [Funcao(**function_validator.validate(row)) for row in raw_function_data]

    total_payroll_cost = service.calculate_total_payroll(
        employees=validated_employees,
        functions=validated_functions,
        global_config=global_config,
        default_monthly_input=default_monthly_input
    )

    # ASSERT - VERIFICAÇÃO FINAL
    # O custo total deve ser a soma dos salários base: 5500.00 + 4200.50
    assert total_payroll_cost == pytest.approx(9700.50)