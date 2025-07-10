# core/history_manager.py (NOVO)

from datetime import date, datetime
from typing import List, Dict, Optional, Any
from core.entities import ParametroHistorico # Assumindo que HistoricalParameter está em entities

class GerenciadorHistorico:
    """
    Gerencia o carregamento e a consulta de parâmetros históricos.
    Em um cenário real com DB, ele se conectaria ao banco.
    Por enquanto, simula o carregamento de um JSON/dicionário.
    """
    def __init__(self, historical_data: List[Dict[str, Any]] = None):
        self._history_records: List[ParametroHistorico] = []
        if historical_data:
            self.carregar_de_dados_brutos(historical_data)

    def carregar_de_dados_brutos(self, raw_data: List[Dict[str, Any]]):
        """Carrega registros históricos a partir de dados brutos (ex: JSON)."""
        self._history_records = []
        for item in raw_data:
            try:
                # Converte strings de data para objetos date
                start_date = datetime.strptime(item['start_date'], "%Y-%m-%d").date()
                end_date = datetime.strptime(item['end_date'], "%Y-%m-%d").date() if item.get('end_date') else None
                record = ParametroHistorico(
                    id=item['id'],
                    nome_parametro=item['parameter_name'],
                    valor=float(item['value']),
                    data_inicio=start_date,
                    data_fim=end_date
                )
                self._history_records.append(record)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Erro ao carregar registro histórico: {item}. Erro: {e}. Registro ignorado.")
        # Opcional: Ordenar para otimizar buscas
        self._history_records.sort(key=lambda x: x.data_inicio)

    def obter_valor_na_data(self, parameter_name: str, check_date: date) -> Optional[float]:
        """
        Retorna o valor mais recente de um parâmetro que estava ativo na data especificada.
        Se houver múltiplos valores ativos, retorna o que tem a start_date mais recente.
        """
        active_records = []
        for record in self._history_records:
            if record.nome_parametro == parameter_name and record.is_active_on_date(check_date):
                active_records.append(record)
        
        if not active_records:
            print(f"Aviso: Nenhum valor histórico encontrado para '{parameter_name}' na data {check_date}.")
            return None # Ou levantar uma exceção

        # Se houver mais de um, pega o mais recente (com a start_date maior)
        # Em casos de sobreposição, a regra mais recente geralmente prevalece.
        latest_record = max(active_records, key=lambda x: x.start_date)
        return latest_record.value

    def obter_todos_parametros_ativos_na_data(self, check_date: date) -> Dict[str, float]:
        """
        Retorna um dicionário com todos os parâmetros ativos e seus valores para uma dada data.
        Útil para montar a GlobalConfig.
        """
        active_params = {}        
        sorted_records = sorted(self._history_records, key=lambda x: x.data_inicio, reverse=True)

        for record in sorted_records:
            if record.is_active_on_date(check_date):
                if record.nome_parametro not in active_params: 
                    active_params[record.nome_parametro] = record.valor
        return active_params