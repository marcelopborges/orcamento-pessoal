from datetime import date
from typing import List
from core.entities import ParametroHistorico


def get_historical_value(history: List[ParametroHistorico], target_date: date) -> float:
    """
    Obtém o valor histórico mais recente antes ou igual à data alvo.
    """
    sorted_history = sorted(history, key=lambda x: x.data_inicio, reverse=True)

    for param in sorted_history:
        # CORREÇÃO: Use 'param.start_date' e 'param.end_date' para a verificação de vigência
        if param.data_inicio <= target_date and \
           (param.data_fim is None or param.data_fim >= target_date):
            return param.valor
    raise ValueError("Nenhum valor de configuração válido encontrado para a data fornecida.")

