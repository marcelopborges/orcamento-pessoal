from datetime import date
import pytest
from core.config import get_historical_value
from core.entities import HistoricalParameter, GlobalConfig

@pytest.fixture
def minimum_wage_history():
    """ Simula um histórico de alterações do salário mínimo. """
    return [
        HistoricalParameter(effective_date=date(2024, 1, 1), value=1800.00),
        HistoricalParameter(effective_date=date(2025, 1, 1), value=1918.00),
        HistoricalParameter(effective_date=date(2023, 1, 1), value=1700.00),
    ]

def test_get_historical_value_returns_correct_value_for_date(minimum_wage_history):
    """
    Testa se a função auxiliar consegue buscar o valor correto do histórico
    para uma data específica.
    """
    assert get_historical_value(minimum_wage_history, date(2024, 5, 15)) == 1800.00
    assert get_historical_value(minimum_wage_history, date(2025, 10, 20)) == 1918.00
    assert get_historical_value(minimum_wage_history, date(2023, 6, 1)) == 1700.00

# --- NOSSA NOVA MISSÃO ESTÁ AQUI ---
def test_create_global_config():
    """ Testa a criação da entidade de configuração global. """
    # Arrange & Act
    config = GlobalConfig(
        calculation_date=date(2025, 4, 30),
        minimum_wage=1918.00,
        insalubrity_percent=0.40
    )

    # Assert
    assert config.minimum_wage == 1918.00
    assert config.insalubrity_percent == 0.40