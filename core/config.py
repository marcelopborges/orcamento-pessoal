from datetime import date
from typing import List
from core.entities import HistoricalParameter


def get_historical_value(history: List[HistoricalParameter], target_date):
    """
    Obtém o valor histórico mais recente antes ou igual à data alvo.
    """
    sorted_history = sorted(history, key=lambda x: x.effective_date, reverse=True)
    for param in sorted_history:
        if param.effective_date <= target_date:
            return param.value
    raise ValueError("Nenhum valor de configuração válido encontrado para a data fornecida.")