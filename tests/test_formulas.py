# tests/test_formulas.py

import pytest
from datetime import date
from core import formulas # Agora importa o módulo formulas

def test_calculate_hourly_wage_formula():
    """
    Testa o cálculo puro do salário por hora.
    """
    assert formulas.calculate_hourly_wage_formula(1000.00, 220) == 4.55
    assert formulas.calculate_hourly_wage_formula(0.00, 220) == 0.00 # Caso de salário zero
    assert formulas.calculate_hourly_wage_formula(1000.00, 0) == 0.00 # Caso de horas zero para evitar ZeroDivisionError

def test_calculate_years_of_service_formula():
    """
    Testa a fórmula pura do tempo de serviço.
    """
    start_date = date(2020, 1, 1)
    end_date = date(2022, 1, 1)
    years = formulas.calcular_salario_hora_formula(start_date=start_date, end_date=end_date)
    assert years == pytest.approx(731 / 365.25) # 731 dias entre 2020-01-01 e 2022-01-01

    # Teste para ano bissexto (2024 é bissexto)
    start_date_bissexto = date(2024, 1, 1)
    end_date_bissexto = date(2025, 1, 1)
    years_bissexto = formulas.calcular_salario_hora_formula(start_date=start_date_bissexto, end_date=end_date_bissexto)
    assert years_bissexto == pytest.approx(366 / 365.25) # 366 dias em um ano bissexto

def test_calculate_percentage_bonus_formula():
    """
    Testa a fórmula pura de cálculo de bônus percentual.
    """
    assert formulas.calculate_percentage_bonus_formula(1500.00, 0.40) == 600.00
    assert formulas.calculate_percentage_bonus_formula(100.00, 0.10) == 10.00
    assert formulas.calculate_percentage_bonus_formula(0.00, 0.50) == 0.00

def test_calculate_proportional_salary_formula():
    """
    Testa a fórmula pura de salário proporcional.
    """
    assert formulas.calculate_proportional_salary_formula(3000.00, 30, 10) == 2000.00
    assert formulas.calculate_proportional_salary_formula(1000.00, 30, 0) == 1000.00 # Sem dias não trabalhados
    assert formulas.calculate_proportional_salary_formula(1000.00, 30, 30) == 0.00 # Todos os dias não trabalhados
    assert formulas.calculate_proportional_salary_formula(1000.00, 0, 0) == 0.00 # Total de dias no mês zero

# --- Adicione aqui os testes para as novas fórmulas puras que você colocou em core/formulas.py ---
def test_calculate_fgts_amount_formula():
    assert formulas.calculate_fgts_amount_formula(1000, 0.08) == 80.0
    assert formulas.calculate_fgts_amount_formula(0, 0.08) == 0.0

def test_calculate_inss_patronal_formula():
    assert formulas.calculate_inss_patronal_formula(1000, 0.20) == 200.0
    assert formulas.calculate_inss_patronal_formula(0, 0.20) == 0.0

def test_calculate_vacation_provision_formula():
    # (1000 * (1 + 1/3)) / 12 = 1333.333... / 12 = 111.11 (arredondado para 2 casas)
    assert formulas.calculate_vacation_provision_formula(1000, (1/3), 12) == pytest.approx(111.11, abs=1e-2)
    assert formulas.calculate_vacation_provision_formula(0, (1/3), 12) == 0.0

def test_calculate_thirteenth_salary_provision_formula():
    # 1000 / 12 = 83.333... = 83.33 (arredondado para 2 casas)
    assert formulas.calculate_thirteenth_salary_provision_formula(1000, 12) == pytest.approx(83.33, abs=1e-2)
    assert formulas.calculate_thirteenth_salary_provision_formula(0, 12) == 0.0

def test_sum_benefits_formula():
    assert formulas.sum_benefits_formula(100, 200, 50, 25) == 375.0
    assert formulas.sum_benefits_formula(0, 0, 0, 0) == 0.0

def test_calculate_total_employee_cost_formula():
    # Salário + Benefícios + Encargos
    assert formulas.calculate_total_employee_cost_formula(5000, 375, 1500) == 6875.0
    assert formulas.calculate_total_employee_cost_formula(0, 0, 0) == 0.0

def test_calculate_total_proventos_formula():
    # Salário_Base_ou_Proporcional + Adicional_Insalubridade
    assert formulas.calculate_total_proventos_formula(2000, 600) == 2600.0
    assert formulas.calculate_total_proventos_formula(1000, 0) == 1000.0