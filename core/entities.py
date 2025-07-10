# core/entities.py (REVISADO)

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any

# --- Entidades de Funcionário e Funções (Adaptações) ---

@dataclass()
class Employee:
    chapa: str
    nome: str
    situacao: str
    codigo_funcao: str
    data_admissao: datetime
    data_admissao_pts: datetime
    data_nascimento: datetime
    sessao: str
    jornada: str
    cpf: str
    centro_custo: str
    empresa: str
    equipe: str
    funcao: str
    valor_vale_transporte_mensal: float
    valor_vale_refeicao_mensal: float
    plano_saude_mensal: float
    outros_beneficios_mensais: float
    custo_total_mensal: float = 0.0 # Adicione este atributo COM VALOR PADRÃO
    
    def is_active(self) -> bool:
        """
        Verifica se o funcionário está ativo.
        Um funcionário é considerado ativo se a situação for 'A'.
        """
        return self.situacao == 'A'
    
    # ATENÇÃO: Valores com histórico DEVEM ser tratados por histórico em outro lugar,
    # ou o Employee deve ter uma lista de histórico.
    # Por agora, vou deixar aqui como placeholders para mostrar que vêm de outro lugar,
    # mas o acesso será via DataLoader/Serviço de Histórico.
    # Se estes campos forem 'fixos' para o Employee (ex: o funcionário tem UM valor atual),
    # mas que pode ter mudado no passado, então ele PRECISA de uma relação com um histórico de benefícios individuais.
    # Para simplicidade inicial, vamos considerar que o DataLoader/serviço os preenche para a data de cálculo.
    # OU, o Employee pode ter IDs para as tabelas históricas de benefícios.
    
    # Exemplo: Se os benefícios são específicos para o funcionário e podem mudar:
    # ids_beneficios_vigentes: List[int] = field(default_factory=list) # Referencia ID de um BenefitHistory
    pass # Manter a estrutura existente. A "vigência" será tratada na camada de dados.

@dataclass(frozen=True)
class Funcao:
    codigo_funcao: str
    nome_funcao: str
    # ATENÇÃO: Salário aqui é o *padrão*. O salário *vigente* de um funcionário virá do histórico de salários.
    salario: float
    pass # Manter a estrutura existente. A "vigência" será tratada na camada de dados.

# --- NOVO: Entidade para Gerenciar Parâmetros Históricos (Vigências) ---

@dataclass(frozen=True)
class HistoricalParameter:
    """ Representa um valor de parâmetro com uma data de vigência de início e fim. """
    id: int 
    parameter_name: str
    value: float
    start_date: date
    end_date: Optional[date] = None

    def is_active_on_date(self, check_date: date) -> bool:
        """Verifica se este parâmetro está ativo em uma determinada data."""
        if self.start_date > check_date:
            return False
        if self.end_date and self.end_date < check_date:
            return False
        return True

# --- Configuração Global (Agora irá *usar* o histórico de parâmetros) ---

@dataclass(frozen=True)
class GlobalConfig:
    """
    Configuração global do sistema para uma data de cálculo específica,
    obtendo os valores vigentes dos parâmetros históricos.
    """
    calculation_date: date
    minimum_wage: float # Salário Mínimo vigente na calculation_date
    insalubrity_percent: float # % de insalubridade vigente
    aliquota_fgts_empresa: float # % FGTS vigente
    aliquota_inss_patronal_media: float # % INSS Empresa vigente
    percentual_terco_ferias: float # % 1/3 férias vigente
    meses_do_ano: int # Meses no ano (fixo ou histórico)

@dataclass
class EmployeeMonthlyInput:
    """ 
    Guarda os inputs variáveis de um funcionário para um mês de cálculo.
    Estes são inputs diretos, não precisam de histórico aqui.
    """
    extra_hours_50: float = 0.0
    extra_hours_100: float = 0.0
    receives_insalubrity: bool = False
    vacation_days: int = 0
    # Valores de benefícios específicos do mês, se não vierem do histórico de Employee/GlobalConfig:
    # valor_vale_transporte_mensal: Optional[float] = 0.0
    # valor_vale_refeicao_mensal: Optional[float] = 0.0
    # plano_saude_mensal: Optional[float] = 0.0
    # outros_beneficios_mensais: Optional[float] = 0.0


@dataclass
class AcaoHeadcount:
    tipo: str # "ACRESCIMO_QPA" ou "REDUCAO_QPA"
    data_efetivacao: str # Formato YYYY-MM-DD

    # Critérios de grupo para a ação
    empresa: str
    equipe: str
    id_funcao: str # ID da função para o grupo

    quantidade: int # Quantidade a aumentar ou diminuir neste grupo

    # Dados para NOVAS contratações (usado apenas em "ACRESCIMO_QPA")
    salario_base_simulado: Optional[float] = None # Pode sobrescrever o padrão da função
    valor_vale_transporte_simulado: Optional[float] = 0.0
    valor_vale_refeicao_simulado: Optional[float] = 0.0 # Ajuste o nome aqui
    plano_saude_simulado: Optional[float] = 0.0
    outros_beneficios_simulados: Optional[float] = 0.0

    def __post_init__(self):
        if self.tipo not in ["ACRESCIMO_QPA", "REDUCAO_QPA"]:
            raise ValueError("Tipo de ação de headcount deve ser 'ACRESCIMO_QPA' ou 'REDUCAO_QPA'.")

        if not self.empresa or not self.equipe or not self.id_funcao:
            raise ValueError("Para ações de QPA, 'empresa', 'equipe' e 'id_funcao' são obrigatórios.")

        if self.quantidade is None or self.quantidade <= 0:
            raise ValueError("'quantidade' deve ser um inteiro positivo.")

        if self.salario_base_simulado is not None and self.salario_base_simulado < 0:
            raise ValueError("Salário base simulado não pode ser negativo.")

@dataclass
class CenariodeOrcamento:
    nome_cenario: str
    ano_inicio: int
    mes_inicio: int
    duracao_meses: int
    acoes_headcount: List[AcaoHeadcount] = field(default_factory=list)

    def adicionar_acao(self, acao: AcaoHeadcount):
        self.acoes_headcount.append(acao)

    def get_end_date(self) -> Dict[str, int]:
        end_date_calc = datetime(self.ano_inicio, self.mes_inicio, 1) + relativedelta(months=self.duracao_meses - 1)
        return {"ano": end_date_calc.year, "mes": end_date_calc.month}