import pytest
from datetime import datetime, date
from core.entities import Employee, Funcao
from core.services import PayrollService
from core.entities import GlobalConfig, EmployeeMonthlyInput

@pytest.fixture
def sample_employee():
    """ 
    Cria uma instância de um funcionário para os testes. 
    """
    return Employee(
        chapa="99999", nome="MARCELO BORGES", situacao="A",
        codigo_funcao="4003", data_admissao=datetime(2023, 1, 1),
        data_admissao_pts=datetime(2023, 1, 1), data_nascimento=datetime(1980, 1, 1),
        sessao="01.01.1.01.01.00001", jornada="220", cpf="93541134780",
        centro_custo="222222222"
    )

@pytest.fixture
def company_functions():
    """ 
    Cria uma lista de funções (nossa tabela de referência em memória). 
    """
    return [
        Funcao(codigo_funcao="1001", nome_funcao="OPERADOR I", salario=2500.00),
        Funcao(codigo_funcao="4003", nome_funcao="ANALISTA ADMINISTRATIVO I", salario=5202.76),
        Funcao(codigo_funcao="9009", nome_funcao="GERENTE DE AREA", salario=12500.50),
    ]

def test_get_employee_salary(sample_employee, company_functions):
    """
    Testa se o serviço encontra o salário correto para um funcionário
    a partir de uma lista de funções.
    """
    service = PayrollService()
    salary = service.get_employee_salary(
        employee=sample_employee,
        functions=company_functions
    )
    assert salary == 5202.76


def test_service_can_calculate_employee_hourly_wage(sample_employee, company_functions):
    service = PayrollService()
    hourly_wage = service.get_employee_hourly_wage(
        employee=sample_employee, 
        functions=company_functions
    )
    assert round(hourly_wage, 2) == 23.65


def test_service_can_get_years_of_service(sample_employee):
    service = PayrollService()
    calculation_date = date(2025, 1, 1)
    years_of_service = service.get_employee_years_of_service(
        employee=sample_employee,
          calculation_date=calculation_date
    )
    assert years_of_service == pytest.approx(2.001368)

def test_service_calculates_insalubrity_bonus_when_eligible():
    """
    Testa se o serviço calcula o bônus de insalubridade corretamente
    quando o funcionário é elegível.
    """
    # Arrange
    service = PayrollService()
    config = GlobalConfig(
        calculation_date=date(2025, 4, 30),
        minimum_wage=1918.00,
        insalubrity_percent=0.40
    )
    monthly_input = EmployeeMonthlyInput(receives_insalubrity=True)

    # Act
    bonus = service.calculate_insalubrity_bonus(
        monthly_input=monthly_input,
        global_config=config
    )

    # Assert
    assert bonus == pytest.approx(1918.00 * 0.40)

def test_service_returns_zero_insalubrity_bonus_when_not_eligible():
    """
    Testa se o bônus de insalubridade é zero quando o funcionário não é elegível.
    """
    # Arrange
    service = PayrollService()
    config = GlobalConfig(
        calculation_date=date(2025, 4, 30),
        minimum_wage=1918.00,
        insalubrity_percent=0.40
    )
    # Input mensal indicando que o funcionário NÃO é elegível
    monthly_input = EmployeeMonthlyInput(receives_insalubrity=False)

    # Act
    bonus = service.calculate_insalubrity_bonus(
        monthly_input=monthly_input,
        global_config=config
    )

    # Assert
    assert bonus == 0.0


def test_service_calculates_proportional_salary(sample_employee, company_functions):
    """ Testa se o serviço calcula o salário proporcional corretamente. """
    # Arrange
    service = PayrollService()
    # Input mensal com 10 dias de férias
    monthly_input = EmployeeMonthlyInput(vacation_days=10)
    # O salário base do sample_employee é 5202.76

    # Act
    proportional_salary = service.calculate_proportional_salary(
        employee=sample_employee,
        functions=company_functions,
        monthly_input=monthly_input
    )

    # Assert
    # (5202.76 / 30) * (30 - 10) = 173.425 * 20 = 3468.51
    assert proportional_salary == pytest.approx(3468.51)


def test_service_generates_full_cost_breakdown(sample_employee, company_functions):
    """
    Testa se o serviço gera a ficha de cálculo completa, calculando
    múltiplos proventos e o total.
    """
    # Arrange
    service = PayrollService()
    config = GlobalConfig(
        calculation_date=date(2025, 4, 30),
        minimum_wage=1918.00,
        insalubrity_percent=0.40
    )
    # Um input mensal com vários dados preenchidos
    monthly_input = EmployeeMonthlyInput(
        vacation_days=10,
        receives_insalubrity=True
    )

    # Act    
    results = service.calculate_full_cost_breakdown(
        employee=sample_employee,
        functions=company_functions,
        global_config=config,
        monthly_input=monthly_input
    )

    # Assert
    assert isinstance(results, dict)
    assert results["SALARIO_BASE"] == pytest.approx(5202.76)
    assert results["EV_DIAS_TRABALHADOS"] == pytest.approx(3468.51)
    assert results["EV_ADIC_INSALUBRIDADE"] == pytest.approx(767.20) # 1918.00 * 0.40

    # Vamos testar um cálculo que depende de outros, como o TOTAL DE PROVENTOS    
    expected_total = results["EV_DIAS_TRABALHADOS"] + results["EV_ADIC_INSALUBRIDADE"]
    assert results["TOTAL_PROVENTOS"] == pytest.approx(expected_total)