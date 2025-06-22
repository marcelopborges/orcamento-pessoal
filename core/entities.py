from dataclasses import dataclass
from datetime import datetime, date

@dataclass(frozen=True)
class Employee:
    """
    Entidade funcionários altamente tipados e imutáveis (frozen=True)
    """
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

    def is_active(self) -> bool:
        """
        Verifica se o funcionário está ativo.
        Um funcionário é considerado ativo se a situação for 'A'.
        """
        return self.situacao == 'A'
    

@dataclass(frozen=True)
class Funcao:
    "Entidade função altamente tipados e imutáveis. Representa a função e seu salário base"
    codigo_funcao: str
    nome_funcao: str
    salario: float

@dataclass(frozen=True)
class HistoricalParameter:
    """ Representa um parâmetro com um valor e sua data de vigência. """
    effective_date: date
    value: float

class GlobalConfig:
    """
    Configuração global do sistema, contendo parâmetros que podem ser alterados ao longo do tempo.
    """
    def __init__(self, calculation_date: date, minimum_wage: float, insalubrity_percent: float):
        self.calculation_date = calculation_date
        self.minimum_wage = minimum_wage
        self.insalubrity_percent = insalubrity_percent

@dataclass
class EmployeeMonthlyInput:
    """ 
    Guarda os inputs variáveis de um funcionário para um mês de cálculo. 
    """
    def __init__(self, extra_hours_50: float = 0.0, extra_hours_100: float = 0.0,
                 receives_insalubrity: bool = False, vacation_days: int = 0):
        self.extra_hours_50 = extra_hours_50
        self.extra_hours_100 = extra_hours_100
        self.receives_insalubrity = receives_insalubrity
        self.vacation_days = vacation_days
    pass


    
    