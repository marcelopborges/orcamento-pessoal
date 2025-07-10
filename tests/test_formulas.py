import pytest
from datetime import date
from core import formulas # Agora importa o módulo formulas

def test_calcular_salario_hora_padrao_sucesso():
    """
    Testa o cálculo puro do salário por hora com valores padrão.
    """
    assert formulas.calcular_salario_hora(1000.00, 220) == 4.55

def test_calcular_salario_hora_salario_zero_retorna_zero():
    """
    Testa se o cálculo do salário por hora retorna zero quando o salário é zero.
    """
    assert formulas.calcular_salario_hora(0.00, 220) == 0.00

def test_calcular_salario_hora_horas_zero_retorna_zero():
    """
    Testa se o cálculo do salário por hora retorna zero quando as horas são zero (evita divisão por zero).
    """
    assert formulas.calcular_salario_hora(1000.00, 0) == 0.00

def test_calcular_tempo_servico_anos_completos():
    """
    Testa a fórmula pura do tempo de serviço para anos completos.
    """
    data_inicio = date(2020, 1, 1)
    data_fim = date(2022, 1, 1)    
    anos = formulas.calcular_tempo_servico(data_inicio=data_inicio, data_fim=data_fim)
    assert anos == pytest.approx(731 / 365.25)

def test_calcular_tempo_servico_ano_bissexto_correto():
    """
    Testa a fórmula pura do tempo de serviço para incluir ano bissexto.
    """
    data_inicio = date(2024, 1, 1)
    data_fim = date(2025, 1, 1)    
    anos = formulas.calcular_tempo_servico(data_inicio=data_inicio, data_fim=data_fim)
    assert anos == pytest.approx(366 / 365.25)

def test_calcular_tempo_servico_mesmo_dia_retorna_zero():
    """
    Testa a fórmula pura do tempo de serviço quando início e fim são o mesmo dia.
    """
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 1, 1)
    anos = formulas.calcular_tempo_servico(data_inicio=data_inicio, data_fim=data_fim)
    assert anos == 0.0

def test_calcular_bonus_percentual_valor_positivo():
    """
    Testa a fórmula pura de cálculo de bônus percentual com valores positivos.
    """
    assert formulas.calcular_bonus_percentual(1500.00, 0.40) == 600.00

def test_calcular_bonus_percentual_valor_base_zero_retorna_zero():
    """
    Testa a fórmula pura de cálculo de bônus percentual com valor base zero.
    """
    assert formulas.calcular_bonus_percentual(0.00, 0.50) == 0.00

def test_calcular_salario_proporcional_dias_trabalhados():
    """
    Testa a fórmula pura de salário proporcional com dias não trabalhados.
    """
    assert formulas.calcular_salario_proporcional(3000.00, 30, 10) == 2000.00

def test_calcular_salario_proporcional_sem_dias_nao_trabalhados():
    """
    Testa a fórmula pura de salário proporcional sem dias não trabalhados.
    """
    assert formulas.calcular_salario_proporcional(1000.00, 30, 0) == 1000.00

def test_calcular_salario_proporcional_todos_dias_nao_trabalhados():
    """
    Testa a fórmula pura de salário proporcional quando todos os dias foram não trabalhados.
    """
    assert formulas.calcular_salario_proporcional(1000.00, 30, 30) == 0.00

def test_calcular_salario_proporcional_total_dias_mes_zero_retorna_zero():
    """
    Testa a fórmula pura de salário proporcional quando o total de dias no mês é zero.
    """
    assert formulas.calcular_salario_proporcional(1000.00, 0, 0) == 0.00

def test_calcular_valor_fgts_padrao():
    assert formulas.calcular_valor_fgts(1000, 0.08) == 80.0

def test_calcular_valor_fgts_salario_base_zero_retorna_zero():
    assert formulas.calcular_valor_fgts(0, 0.08) == 0.0

def test_calcular_inss_patronal_padrao():
    assert formulas.calcular_inss_patronal(1000, 0.20) == 200.0

def test_calcular_inss_patronal_salario_base_zero_retorna_zero():
    assert formulas.calcular_inss_patronal(0, 0.20) == 0.0

def test_calcular_provisao_ferias_padrao():
    assert formulas.calcular_provisao_ferias(1000, (1/3), 12) == pytest.approx(111.11, abs=1e-2)

def test_calcular_provisao_ferias_salario_base_zero_retorna_zero():
    assert formulas.calcular_provisao_ferias(0, (1/3), 12) == 0.0

def test_calcular_provisao_decimo_terceiro_salario_padrao():
    assert formulas.calcular_provisao_decimo_terceiro_salario(1000, 12) == pytest.approx(83.33, abs=1e-2)

def test_calcular_provisao_decimo_terceiro_salario_zero_retorna_zero():
    assert formulas.calcular_provisao_decimo_terceiro_salario(0, 12) == 0.0

def test_somar_beneficios_todos_valores_positivos():
    assert formulas.somar_beneficios(100, 200, 50, 25) == 375.0

def test_somar_beneficios_todos_valores_zero_retorna_zero():
    assert formulas.somar_beneficios(0, 0, 0, 0) == 0.0

def test_calcular_custo_total_funcionario_padrao():
    assert formulas.calcular_custo_total_funcionario(5000, 375, 1500) == 6875.0

def test_calcular_custo_total_funcionario_todos_zero_retorna_zero():
    assert formulas.calcular_custo_total_funcionario(0, 0, 0) == 0.0

def test_calcular_total_proventos_padrao():
    assert formulas.calcular_total_proventos(2000, 600) == 2600.0

def test_calcular_total_proventos_adicional_zero_retorna_salario_base():
    assert formulas.calcular_total_proventos(1000, 0) == 1000.0

def test_calcular_adicional_periculosidade_formula_padrao():
    assert formulas.calcular_adicional_periculosidade_formula(5000.00, 0.30) == 1500.00

def test_calcular_adicional_periculosidade_formula_valor_base_zero():
    assert formulas.calcular_adicional_periculosidade_formula(0.00, 0.30) == 0.00
