import pytest
from datetime import date
from core.payroll_rules import calculate_hourly_wage, calculate_years_of_service, calculate_percentage_bonus, calculate_proportional_salary

def test_calculate_hourly_wage():
    """
    Testa o cálculo puro do salário por hora.
    """
    # Arrange
    base_salary = 1000.00
    monthly_hours = 220

    # Act
    hourly_wage = calculate_hourly_wage(
        salary=base_salary,
        hours=monthly_hours
    )

    # Assert
    # O resultado esperado de 1000 / 220 é aprox. 4.55...    
    assert hourly_wage == 4.55

def test_calculate_years_of_service():
    """
    Testa o tempo de serviço
    """
    # Arrange
    data_admissao = date(2020, 1, 1)
    data_fim = date(2022, 1, 1)    
    # Act
    years = calculate_years_of_service(start_date = data_admissao, end_date = data_fim)
    # Assert
    # Nova linha (correta)
    assert years == pytest.approx(731 / 365.25)

def test_calculate_insalubrity_bonus():
    """
    Testa o cálculo do adicional de insalubridade.
    """
    # Arrange
    base_value = 1500.00  # Valor salário minimo para teste exemplo  
    percent = 0.40 # Percentual de insalubridade

    # Act
    insalubrity_bonus = calculate_percentage_bonus(
        base_value=base_value,
        percent=percent
    )

    # Assert
    assert insalubrity_bonus == 600.00

def test_calculate_proportional_salary():
    """
    Testa o cálculo de salário proporcional aos dias trabalhados.
    """
    # Arrange
    base_salary = 3000.00
    total_days_in_month = 30
    non_worked_days = 10 # Ex: 10 dias de férias

    # Act
    proportional_salary = calculate_proportional_salary(
        base_salary=base_salary,
        total_days_in_month=total_days_in_month,
        non_worked_days=non_worked_days
    )

    # Assert
    # O funcionário trabalhou 20 dias, então deve receber 2/3 do salário.
    # (3000 / 30) * (30 - 10) = 100 * 20 = 2000
    assert proportional_salary == 2000.00