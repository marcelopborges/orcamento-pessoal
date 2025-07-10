import pytest
from core.entities import LancamentoMensalFuncionario

def test_criar_lancamento_mensal_funcionario_com_valores_padrao():
    """ 
    Testa a criação da entidade de input mensal com valores padrão. 
    """
    
    lancamento_mensal = LancamentoMensalFuncionario()
    assert lancamento_mensal.horas_extras_50_porcento == 0.0 
    assert lancamento_mensal.horas_extras_100_porcento == 0.0
    assert lancamento_mensal.recebe_insalubridade is False
    assert lancamento_mensal.dias_ferias == 0
    assert lancamento_mensal.horas_trabalhadas_no_mes == 0.0
    assert lancamento_mensal.quantidade_horas_s_aviso == 0.0


def test_criar_lancamento_mensal_funcionario_com_valores_especificos():
    """ 
    Testa a criação da entidade de input mensal com valores específicos. 
    """
    lancamento_mensal = LancamentoMensalFuncionario(
        horas_extras_50_porcento=10.5,
        recebe_insalubridade=True,
        dias_ferias=15,
        horas_trabalhadas_no_mes=160.0,
        quantidade_horas_s_aviso=8.0
    )

    # Assert
    assert lancamento_mensal.horas_extras_50_porcento == 10.5
    assert lancamento_mensal.recebe_insalubridade is True
    assert lancamento_mensal.horas_extras_100_porcento == 0.0
    assert lancamento_mensal.dias_ferias == 15    
    assert lancamento_mensal.horas_trabalhadas_no_mes == 160.0
    assert lancamento_mensal.quantidade_horas_s_aviso == 8.0