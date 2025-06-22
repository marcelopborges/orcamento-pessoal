import pytest
from core.entities import EmployeeMonthlyInput

def test_create_employee_monthly_input_with_defaults():
    """ 
    Testa a criação da entidade de input mensal com valores padrão. 
    """
    # Arrange & Act
    monthly_input = EmployeeMonthlyInput()

    # Assert
    assert monthly_input.extra_hours_50 == 0.0
    assert monthly_input.extra_hours_100 == 0.0
    assert monthly_input.receives_insalubrity is False
    assert monthly_input.vacation_days == 0

def test_create_employee_monthly_input_with_specific_values():
    """ 
    Testa a criação da entidade de input mensal com valores específicos. 
    """
    # Arrange & Act
    # Aqui simulamos um mês em que o funcionário teve inputs específicos.
    monthly_input = EmployeeMonthlyInput(
        extra_hours_50=10.5,
        receives_insalubrity=True,
        vacation_days=15
    )

    # Assert
    assert monthly_input.extra_hours_50 == 10.5
    assert monthly_input.receives_insalubrity is True
    assert monthly_input.extra_hours_100 == 0.0
    assert monthly_input.vacation_days == 15