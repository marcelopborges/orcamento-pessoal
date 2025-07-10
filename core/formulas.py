"""
Este módulo centraliza todas as fórmulas matemáticas e lógicas de cálculo puro
utilizadas no sistema de orçamento. As funções aqui são agnósticas ao contexto
de objetos Employee ou GlobalConfig, recebendo todos os parâmetros necessários
e retornando um resultado.
"""

from datetime import date
from typing import Dict, Any
from core.entities import Funcionario, Cargo, ConfiguracaoGlobal, LancamentoMensalFuncionario
from core.payroll_rules import ServicoFolhaPagamento

def calcular_salario_hora(salario: float, horas: int) -> float:
    """
    Calcula o salário por hora.
    Formula: SALARIO / HORAS_MENSAIS
    """
    if horas == 0:
        return 0.0
    salario_hora_calculado = salario / horas
    return round(salario_hora_calculado, 2)

def calcular_bonus_percentual(valor_base: float, percentual: float) -> float:
    """
    Calcula um valor de bônus baseado em um percentual de um valor base.
    Formula: VALOR_BASE * PERCENTUAL
    """
    bonus = valor_base * percentual
    return round(bonus, 2)

def calcular_salario_proporcional(salario_base: float, total_dias_no_mes: int, dias_nao_trabalhados: int) -> float: # <--- RENOMEADO AQUI
    """
    Calcula o salário proporcional aos dias trabalhados no mês.
    Formula: (SALARIO_BASE / TOTAL_DIAS_NO_MES) * (TOTAL_DIAS_NO_MES - DIAS_NAO_TRABALHADOS)
    """
    if total_dias_no_mes <= 0:
        return 0.0
    dias_trabalhados = total_dias_no_mes - dias_nao_trabalhados
    if dias_trabalhados < 0:
        dias_trabalhados = 0

    salario_diario = salario_base / total_dias_no_mes # <--- Use novos nomes
    salario_proporcional_calculado = salario_diario * dias_trabalhados # <--- Use novos nomes
    return round(salario_proporcional_calculado, 2)


def calcular_tempo_servico(data_inicio: date, data_fim: date) -> float:
    """
    Calcula o tempo total de serviço em anos.
    Fórmula: (DATA_FIM - DATA_INICIO).days / 365.25 (considera anos bissextos)
    """
    delta = data_fim - data_inicio
    anos = delta.days / 365.25
    return anos

def calcular_valor_fgts(salario_base: float, aliquota_fgts: float) -> float:
    return salario_base * aliquota_fgts

def calcular_inss_patronal(salario_base: float, aliquota_inss_empresa: float) -> float:
    return salario_base * aliquota_inss_empresa

def calcular_provisao_ferias(salario_base: float, terco_ferias_percent: float, meses_ano: int) -> float:
    return (salario_base * (1 + terco_ferias_percent)) / meses_ano

def calcular_provisao_decimo_terceiro_salario(salario_base: float, meses_ano: int) -> float:
    return salario_base / meses_ano

def somar_beneficios(
    valor_vale_transporte_mensal: float,
    valor_vale_refeicao_mensal: float,
    plano_saude_mensal: float,
    outros_beneficios_mensais: float
) -> float:
    return (
        valor_vale_transporte_mensal +
        valor_vale_refeicao_mensal +
        plano_saude_mensal +
        outros_beneficios_mensais
    )

def calcular_custo_total_funcionario(
    salario_base: float,
    total_beneficios: float,
    total_encargos_e_provisoes: float
) -> float:
    return salario_base + total_beneficios + total_encargos_e_provisoes

def calcular_total_proventos(
    salario_base_ou_proporcional: float,
    adicional_insalubridade: float,
) -> float:
    return salario_base_ou_proporcional + adicional_insalubridade


def calcular_adicional_periculosidade_formula(valor_dias_trabalhados: float, percentual_periculosidade: float) -> float:
    """
    Calcula o adicional de periculosidade.
    Fórmula: VALOR_DIAS_TRABALHADOS * PERCENTUAL_PERICULOSIDADE
    """
    adicional = valor_dias_trabalhados * percentual_periculosidade
    return round(adicional, 2)

def calcular_adicional_noturno_formula(base_calculo_hora_total: float, jornada_padrao_mensal_horas: int, percentual_adicional: float, quantidade_horas_noturnas: float) -> float: # <-- Nomes dos parâmetros em português
    """
    Calcula o adicional noturno.
    Fórmula: (BASE_CALCULO_HORA_TOTAL / jornada_padrao_mensal_horas) * PERCENTUAL_ADICIONAL * QUANTIDADE_HORAS_NOTURNAS
    """
    if jornada_padrao_mensal_horas <= 0:
        return 0.0
    
    valor_hora_base = base_calculo_hora_total / jornada_padrao_mensal_horas
    adicional = valor_hora_base * percentual_adicional * quantidade_horas_noturnas
    return round(adicional, 2)