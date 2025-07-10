from datetime import date
import pytest
from core.config import get_historical_value
from core.entities import ParametroHistorico, ConfiguracaoGlobal

@pytest.fixture
def minimum_wage_history():
    """ Simula um histórico de alterações do salário mínimo. """
    return [
        ParametroHistorico(id=1, nome_parametro="salario_minimo", data_inicio=date(2024, 1, 1), valor=1800.00, data_fim=None),
        ParametroHistorico(id=2, nome_parametro="salario_minimo", data_inicio=date(2025, 1, 1), valor=1918.00, data_fim=None),
        ParametroHistorico(id=3, nome_parametro="salario_minimo", data_inicio=date(2023, 1, 1), valor=1700.00, data_fim=date(2023, 12, 31)), 
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
    config = ConfiguracaoGlobal(
        data_calculo=date(2025, 4, 30),
        salario_minimo=1918.00,
        percentual_insalubridade=0.40,        
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=0.3333333333333333,
        meses_do_ano=12
    )

    # Assert
    assert config.salario_minimo == 1918.00
    assert config.percentual_insalubridade == 0.40