# core/formulas.py

"""
Este módulo centraliza todas as fórmulas matemáticas e lógicas de cálculo puro
utilizadas no sistema de orçamento. As funções aqui são agnósticas ao contexto
de objetos Employee ou GlobalConfig, recebendo todos os parâmetros necessários
e retornando um resultado.
"""

from datetime import date
from typing import Dict, Any

def calculate_hourly_wage_formula(salary: float, hours: int) -> float:
    """
    Calcula o salário por hora.
    Formula: SALARIO / HORAS_MENSAIS
    """
    if hours == 0:
        return 0.0
    hourly_wage = salary / hours
    return round(hourly_wage, 2)

def calcular_salario_hora_formula(start_date: date, end_date: date) -> float:
    """
    Calcula o tempo total de serviço do funcionário em anos.
    Formula: (END_DATE - START_DATE).days / 365.25 (considera anos bissextos)
    """
    delta = end_date - start_date
    years = delta.days / 365.25
    return years

def calculate_percentage_bonus_formula(base_value: float, percent: float) -> float:
    """
    Calcula um valor de bônus baseado em um percentual de um valor base (ex: Insalubridade, Periculosidade).
    Formula: BASE_VALUE * PERCENT
    """
    bonus = base_value * percent
    return round(bonus, 2)

def calculate_proportional_salary_formula(base_salary: float, total_days_in_month: int, non_worked_days: int) -> float:
    """
    Calcula o salário proporcional aos dias trabalhados no mês.
    Formula: (BASE_SALARY / TOTAL_DAYS_IN_MONTH) * (TOTAL_DAYS_IN_MONTH - NON_WORKED_DAYS)
    """
    if total_days_in_month <= 0:
        return 0.0
    worked_days = total_days_in_month - non_worked_days
    if worked_days < 0:
        worked_days = 0
    
    daily_salary = base_salary / total_days_in_month
    proportional_salary = daily_salary * worked_days
    return round(proportional_salary, 2)

# --- Adicione aqui outras fórmulas puras, como as de encargos/provisões se você já as tiver ---
# Por exemplo, se elas forem calculadas assim, mova-as para cá:
def calculate_fgts_amount_formula(salario_base: float, aliquota_fgts: float) -> float:
    return salario_base * aliquota_fgts

def calculate_inss_patronal_formula(salario_base: float, aliquota_inss_empresa: float) -> float:
    return salario_base * aliquota_inss_empresa

def calculate_vacation_provision_formula(salario_base: float, terco_ferias_percent: float, meses_ano: int) -> float:
    return (salario_base * (1 + terco_ferias_percent)) / meses_ano

def calculate_thirteenth_salary_provision_formula(salario_base: float, meses_ano: int) -> float:
    return salario_base / meses_ano

def sum_benefits_formula(
    valor_vale_transporte_mensal: float,
    valor_vale_refeicao_mensal: float,
    plano_saude_mensal: float,
    outros_beneficios_mensais: float
) -> float:
    return (
        valor_vale_transporte_mensal +
        valor_vale_refeicao_mensal +
        plano_saude_mensal +
        outros_beneficios_mensais
    )

def calculate_total_employee_cost_formula(
    salario_base: float,
    total_beneficios: float,
    total_encargos_e_provisoes: float
) -> float:
    return salario_base + total_beneficios + total_encargos_e_provisoes

def calculate_total_proventos_formula(
    salario_base_ou_proporcional: float,
    adicional_insalubridade: float,
) -> float:
    return salario_base_ou_proporcional + adicional_insalubridade