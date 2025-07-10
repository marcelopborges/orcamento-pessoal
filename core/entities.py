
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from dateutil.relativedelta import relativedelta



@dataclass()
class Funcionario:
    chapa: str
    nome: str
    situacao: str
    codigo_funcao: str
    data_admissao: datetime
    data_admissao_pts: datetime
    data_nascimento: datetime
    secao: str
    carga_horaria_mensal: str
    cpf: str
    centro_custo: str
    empresa: str
    equipe: str
    funcao: str
    valor_vale_transporte_mensal: float
    valor_vale_refeicao_mensal: float
    plano_saude_mensal: float
    outros_beneficios_mensais: float
    valor_base_gratificacao_mensal: float = 0.0
    custo_total_mensal: float = 0.0  

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
class Cargo:
    codigo_funcao: str
    nome_funcao: str
    # ATENÇÃO: Salário aqui é o *padrão*. O salário *vigente* de um funcionário virá do histórico de salários.
    salario: float
    

@dataclass(frozen=True)
class ParametroHistorico:
    """ Representa um valor de parâmetro com uma data de vigência de início e fim. """
    id: int 
    nome_parametro: str
    valor: float
    data_inicio: date
    data_fim: Optional[date] = None

    def is_active_on_date(self, check_date: date) -> bool:
        """Verifica se este parâmetro está ativo em uma determinada data."""
        if self.data_inicio > check_date:
            return False
        if self.data_fim and self.data_fim < check_date:
            return False
        return True

# --- Configuração Global (Agora irá *usar* o histórico de parâmetros) ---

@dataclass(frozen=True)
class ConfiguracaoGlobal:
    """
    Configuração global do sistema para uma data de cálculo específica,
    obtendo os valores vigentes dos parâmetros históricos.
    """
    data_calculo: date
    salario_minimo: float # Salário Mínimo vigente na calculation_date
    percentual_insalubridade: float # % de insalubridade vigente
    aliquota_fgts_patronal: float # % FGTS vigente
    aliquota_inss_patronal_media: float # % INSS Empresa vigente
    percentual_terco_ferias: float # % 1/3 férias vigente
    meses_do_ano: int # Meses no ano (fixo ou histórico)
    horas_jornada_padrao_mensal: int = 220 # Padrão de horas mensais (pode ser ajustado por jornada)
    percentual_periculosidade: float = 0.30 
    percentual_adicional_noturno: float = 0.20 

@dataclass
class LancamentoMensalFuncionario:
    """ 
    Guarda os inputs variáveis de um funcionário para um mês de cálculo.
    Estes são inputs diretos, não precisam de histórico aqui.
    """
    horas_extras_50_porcento: float = 0.0
    horas_extras_100_porcento: float = 0.0
    recebe_insalubridade: bool = False 
    recebe_periculosidade: bool = False 
    recebe_adicional_noturno: bool = False 
    dias_ferias: int = 0 
    horas_trabalhadas_no_mes: float = 0.0 
    quantidade_horas_s_aviso: float = 0.0 
    valor_descanso_semanal_remunerado: float = 0.0 
    quantidade_horas_adicional_noturno: float = 0.0


@dataclass
class AcaoQuadroPessoal:
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
class CenarioOrcamento:
    nome_cenario: str
    ano_inicio: int
    mes_inicio: int
    duracao_meses: int
    acoes_quadro_pessoal: List[AcaoQuadroPessoal] = field(default_factory=list)

    def adicionar_acao(self, acao: AcaoQuadroPessoal):
        self.acoes_quadro_pessoal.append(acao)

    def get_end_date(self) -> Dict[str, int]:
        end_date_calc = datetime(self.ano_inicio, self.mes_inicio, 1) + relativedelta(months=self.duracao_meses - 1)
        return {"ano": end_date_calc.year, "mes": end_date_calc.month}