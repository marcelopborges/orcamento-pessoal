"""
DICIONÁRIOS DE VARIÁVEIS
"""
def calculate_hourly_wage(salary, hours):
    """
    SALÁRIO BASE DIVIDIDO PELA CARGA HORÁRIA MENSAL
    """
    hourly_wage = salary / hours
    return round(hourly_wage, 2)

def calculate_years_of_service(start_date, end_date):
    """
    TEMPO TOTAL DE SERVIÇO DO FUNCIONÁRIO ATÉ O ÚLTIMO DIA DA BASE CALCULADA
    """
    delta = end_date - start_date
    # 365,35 é a média de dias em um ano para contabilizar anos bissextos.
    years = delta.days / 365.25
    return years

def calculate_percentage_bonus(base_value: float, percent: float) -> float:
    """
    Calcula um valor de bônus baseado em um percentual de um valor base.
    Ex: Insalubridade, Periculosidade, Gratificações.
    """
    bonus = base_value * percent
    return round(bonus, 2)

def calculate_proportional_salary(base_salary: float, total_days_in_month: int, non_worked_days: int) -> float:
    """
    Calcula o salário proporcional aos dias trabalhados no mês.
    Ex: Férias, Afastamentos, Licenças.
    """
    worked_days = total_days_in_month - non_worked_days
    daily_salary = base_salary / total_days_in_month
    proportional_salary = daily_salary * worked_days
    return round(proportional_salary, 2)