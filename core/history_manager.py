# core/history_manager.py (NOVO)

from datetime import date, datetime
from typing import List, Dict, Optional, Any
from core.entities import HistoricalParameter # Assumindo que HistoricalParameter está em entities

class HistoryManager:
    """
    Gerencia o carregamento e a consulta de parâmetros históricos.
    Em um cenário real com DB, ele se conectaria ao banco.
    Por enquanto, simula o carregamento de um JSON/dicionário.
    """
    def __init__(self, historical_data: List[Dict[str, Any]] = None):
        self._history_records: List[HistoricalParameter] = []
        if historical_data:
            self.load_from_raw_data(historical_data)

    def load_from_raw_data(self, raw_data: List[Dict[str, Any]]):
        """Carrega registros históricos a partir de dados brutos (ex: JSON)."""
        self._history_records = []
        for item in raw_data:
            try:
                # Converte strings de data para objetos date
                start_date = datetime.strptime(item['start_date'], "%Y-%m-%d").date()
                end_date = datetime.strptime(item['end_date'], "%Y-%m-%d").date() if item.get('end_date') else None
                record = HistoricalParameter(
                    id=item['id'],
                    parameter_name=item['parameter_name'],
                    value=float(item['value']),
                    start_date=start_date,
                    end_date=end_date
                )
                self._history_records.append(record)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Erro ao carregar registro histórico: {item}. Erro: {e}. Registro ignorado.")
        # Opcional: Ordenar para otimizar buscas
        self._history_records.sort(key=lambda x: x.start_date)

    def get_value_on_date(self, parameter_name: str, check_date: date) -> Optional[float]:
        """
        Retorna o valor mais recente de um parâmetro que estava ativo na data especificada.
        Se houver múltiplos valores ativos, retorna o que tem a start_date mais recente.
        """
        active_records = []
        for record in self._history_records:
            if record.parameter_name == parameter_name and record.is_active_on_date(check_date):
                active_records.append(record)
        
        if not active_records:
            print(f"Aviso: Nenhum valor histórico encontrado para '{parameter_name}' na data {check_date}.")
            return None # Ou levantar uma exceção

        # Se houver mais de um, pega o mais recente (com a start_date maior)
        # Em casos de sobreposição, a regra mais recente geralmente prevalece.
        latest_record = max(active_records, key=lambda x: x.start_date)
        return latest_record.value

    def get_all_active_parameters_on_date(self, check_date: date) -> Dict[str, float]:
        """
        Retorna um dicionário com todos os parâmetros ativos e seus valores para uma dada data.
        Útil para montar a GlobalConfig.
        """
        active_params = {}
        # Garante que, se houver sobreposições, o valor mais recente (start_date) prevalece
        sorted_records = sorted(self._history_records, key=lambda x: x.start_date, reverse=True) # Mais recente primeiro

        for record in sorted_records:
            if record.is_active_on_date(check_date):
                if record.parameter_name not in active_params: # Adiciona apenas se não foi adicionado por uma versão mais recente
                    active_params[record.parameter_name] = record.value
        return active_params