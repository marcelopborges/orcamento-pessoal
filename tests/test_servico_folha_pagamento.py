import pytest
from datetime import date, datetime
import copy
from core.payroll_rules import ServicoFolhaPagamento
from core.entities import Funcionario, Cargo, ConfiguracaoGlobal, LancamentoMensalFuncionario, Funcionario




@pytest.fixture
def servico_folha_pagamento():
    """Retorna uma instância do ServicoFolhaPagamento."""
    return ServicoFolhaPagamento()

@pytest.fixture
def funcionario_exemplo():
    """Retorna uma instância de Funcionario para testes."""
    return Funcionario(
        chapa="99999", nome="Funcionario Teste", situacao="A",
        codigo_funcao="0001", data_admissao=datetime(2020, 1, 1),
        data_admissao_pts=datetime(2020, 1, 1), data_nascimento=datetime(1980, 1, 1),
        secao="01.01.1.01.01.001", 
        carga_horaria_mensal="220",
        cpf="12345678909",
        centro_custo="CC1234567",
        empresa="Empresa Teste", equipe="Equipe Teste", funcao="Cargo Teste",
        valor_vale_transporte_mensal=100.0, valor_vale_refeicao_mensal=300.0,
        plano_saude_mensal=50.0, outros_beneficios_mensais=25.0,
        valor_base_gratificacao_mensal=1000.0
    )

@pytest.fixture
def cargos_empresa():
    """Retorna uma lista de objetos Cargo."""
    return [
        Cargo(codigo_funcao="0001", nome_funcao="Cargo Teste", salario=5000.00),
        Cargo(codigo_funcao="0002", nome_funcao="Outro Cargo", salario=3000.00)
    ]

@pytest.fixture
def configuracao_global_exemplo():
    """Retorna uma instância de ConfiguracaoGlobal para testes, com todos os novos campos."""
    return ConfiguracaoGlobal(
        data_calculo=date(2025, 7, 10),
        salario_minimo=1412.00,
        percentual_insalubridade=0.40,
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=(1/3),
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220,        
        percentual_periculosidade=0.30, 
        percentual_adicional_noturno=0.20
        
    )

@pytest.fixture
def lancamento_mensal_exemplo_base():
    """Retorna uma instância base de LancamentoMensalFuncionario para testes."""
    return LancamentoMensalFuncionario(
        horas_extras_50_porcento=0.0,
        horas_extras_100_porcento=0.0,
        recebe_insalubridade=False,
        recebe_periculosidade=False,
        recebe_adicional_noturno=False,
        dias_ferias=0,
        horas_trabalhadas_no_mes=220.0,
        quantidade_horas_s_aviso=0.0,
        valor_descanso_semanal_remunerado=0.0,
        quantidade_horas_adicional_noturno=0.0,
    )


def test_obter_salario_funcionario(servico_folha_pagamento, funcionario_exemplo, cargos_empresa):
    """Testa se o serviço encontra o salário correto para um funcionário."""
    salario = servico_folha_pagamento.obter_salario_funcionario(
        employee=funcionario_exemplo,
        functions=cargos_empresa
    )
    assert salario == 5000.00

def test_obter_salario_hora_funcionario(servico_folha_pagamento, funcionario_exemplo, cargos_empresa):
    """Testa se o serviço calcula o salário por hora do funcionário."""
    # Base: 5000 / 220 = 22.727 -> 22.73
    salario_hora = servico_folha_pagamento.obter_salario_hora_funcionario(
        employee=funcionario_exemplo,
        functions=cargos_empresa
    )
    assert salario_hora == pytest.approx(22.73)

def test_obter_anos_servico_funcionario(servico_folha_pagamento, funcionario_exemplo):
    data_admissao_teste = funcionario_exemplo.data_admissao.date()
    data_calculo_teste = date(2025, 7, 10)

    anos_servico = servico_folha_pagamento.obter_anos_servico(
        employee=funcionario_exemplo,
        data_calculo=data_calculo_teste
    )

    valor_esperado_em_dias = (data_calculo_teste - data_admissao_teste).days
    assert anos_servico == pytest.approx(valor_esperado_em_dias / 365.25)


def test_calcular_bonus_insalubridade_quando_elegivel(servico_folha_pagamento, lancamento_mensal_exemplo_base):
    """Testa se o serviço calcula o bônus de insalubridade quando o funcionário é elegível."""
    # Arrange
    configuracao_global_teste = ConfiguracaoGlobal(
        data_calculo=date(2025, 7, 10),
        salario_minimo=1412.00,
        percentual_insalubridade=0.40, # Valor relevante para este teste
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=(1/3),
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220,
        percentual_periculosidade=0.30,
        percentual_adicional_noturno=0.20
    )
    lancamento_com_insalubridade = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_com_insalubridade.recebe_insalubridade = True

    # Act
    bonus = servico_folha_pagamento.calcular_bonus_insalubridade(
        lancamento_mensal=lancamento_com_insalubridade,
        configuracao_global=configuracao_global_teste # Use a nova instância
    )

    # Assert
    assert bonus == pytest.approx(1412.00 * 0.40) # 564.80


def test_calcular_bonus_insalubridade_retorna_zero_quando_nao_elegivel(servico_folha_pagamento, lancamento_mensal_exemplo_base):
    """Testa se o bônus de insalubridade é zero quando o funcionário não é elegível."""
    # Arrange
    configuracao_global_teste = ConfiguracaoGlobal( # Recrie para cada teste
        data_calculo=date(2025, 7, 10),
        salario_minimo=1412.00,
        percentual_insalubridade=0.40,
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=(1/3),
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220,
        percentual_periculosidade=0.30,
        percentual_adicional_noturno=0.20
    )
    lancamento_sem_insalubridade = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_sem_insalubridade.recebe_insalubridade = False

    # Act
    bonus = servico_folha_pagamento.calcular_bonus_insalubridade(
        lancamento_mensal=lancamento_sem_insalubridade,
        configuracao_global=configuracao_global_teste
    )

    # Assert
    assert bonus == 0.0

def test_calcular_total_folha_pagamento_soma_salarios_base(servico_folha_pagamento, funcionario_exemplo, cargos_empresa, configuracao_global_exemplo, lancamento_mensal_exemplo_base):
    """Testa se o método calcula_total_folha_pagamento soma corretamente os salários base."""
    # Arrange: Dois funcionários
    funcionario1 = copy.deepcopy(funcionario_exemplo)
    funcionario1.chapa = "00001"
    funcionario1.codigo_funcao = "0001" # Já tem salário 5000

    funcionario2 = copy.deepcopy(funcionario_exemplo)
    funcionario2.chapa = "00002"
    funcionario2.codigo_funcao = "0002" # Tem salário 3000

    lista_funcionarios = [funcionario1, funcionario2]

    # Act
    custo_total = servico_folha_pagamento.calcular_total_folha_pagamento(
        funcionarios=lista_funcionarios,
        cargos=cargos_empresa,
        configuracao_global=configuracao_global_exemplo,
        lancamento_mensal_padrao=lancamento_mensal_exemplo_base
    )

    # Assert: 5000 + 3000 = 8000
    assert custo_total == 8000.00


def test_calcular_salario_proporcional_servico_sem_ferias(servico_folha_pagamento, funcionario_exemplo, cargos_empresa, lancamento_mensal_exemplo_base):
    """Testa o cálculo do salário proporcional sem dias de férias."""
    # O salário base do funcionario_exemplo é 5000.00
    salario_proporcional = servico_folha_pagamento.calcular_salario_proporcional_servico(
        funcionario=funcionario_exemplo,
        cargos=cargos_empresa,
        lancamento_mensal=lancamento_mensal_exemplo_base # Sem férias
    )
    assert salario_proporcional == 5000.00

def test_calcular_salario_proporcional_servico_com_ferias(servico_folha_pagamento, funcionario_exemplo, cargos_empresa, lancamento_mensal_exemplo_base):
    """Testa o cálculo do salário proporcional com dias de férias."""
    lancamento_com_ferias = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_com_ferias.dias_ferias = 10 # 10 dias de férias

    # (5000 / 30) * (30 - 10) = 166.666... * 20 = 3333.33
    salario_proporcional = servico_folha_pagamento.calcular_salario_proporcional_servico(
        funcionario=funcionario_exemplo,
        cargos=cargos_empresa,
        lancamento_mensal=lancamento_com_ferias
    )
    assert salario_proporcional == pytest.approx(3333.33)

def test_calcular_adicional_periculosidade_quando_apto(servico_folha_pagamento, lancamento_mensal_exemplo_base):
    """Testa o cálculo do adicional de periculosidade quando o funcionário é apto."""
    # Arrange
    valor_dias_trabalhados_simulado = 3468.51 # Exemplo de valor de 'EV Dias Trabalhados'
    
    configuracao_global_teste = ConfiguracaoGlobal( # Recrie para cada teste
        data_calculo=date(2025, 7, 10),
        salario_minimo=1412.00,
        percentual_insalubridade=0.40,
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=(1/3),
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220,
        percentual_periculosidade=0.30, # Valor relevante para este teste
        percentual_adicional_noturno=0.20
    )
    lancamento_com_peric = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_com_peric.recebe_periculosidade = True

    # Act
    adicional_periculosidade = servico_folha_pagamento.calcular_adicional_periculosidade(
        lancamento_mensal=lancamento_com_peric,
        configuracao_global=configuracao_global_teste,
        valor_dias_trabalhados=valor_dias_trabalhados_simulado
    )

    # Assert
    # 3468.51 * 0.30 = 1040.553 -> 1040.55
    assert adicional_periculosidade == pytest.approx(1040.55)

def test_adicional_periculosidade_retorna_zero_quando_nao_apto(servico_folha_pagamento, lancamento_mensal_exemplo_base):
    """Testa se o bônus de periculosidade é zero quando o funcionário não é elegível."""
    # Arrange
    valor_dias_trabalhados_simulado = 3468.51 # Não importa, pois não é apto
    
    configuracao_global_teste = ConfiguracaoGlobal( # Recrie para cada teste
        data_calculo=date(2025, 7, 10),
        salario_minimo=1412.00,
        percentual_insalubridade=0.40,
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=(1/3),
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220,
        percentual_periculosidade=0.30,
        percentual_adicional_noturno=0.20
    )
    lancamento_sem_peric = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_sem_peric.recebe_periculosidade = False # Não apto

    # Act
    adicional_periculosidade = servico_folha_pagamento.calcular_adicional_periculosidade(
        lancamento_mensal=lancamento_sem_peric,
        configuracao_global=configuracao_global_teste,
        valor_dias_trabalhados=valor_dias_trabalhados_simulado
    )

    # Assert
    assert adicional_periculosidade == 0.0
def test_calcular_adicional_noturno_padrao(servico_folha_pagamento, funcionario_exemplo, cargos_empresa, configuracao_global_exemplo, lancamento_mensal_exemplo_base):
    # Arrange
    salario_base_func = servico_folha_pagamento.obter_salario_funcionario(funcionario_exemplo, cargos_empresa)

    # --- CALCULAR INSALUBRIDADE E PERICULOSIDADE REALISTAMENTE PARA O TESTE ---
    # Recrie config e lancamento mensais para obter os valores corretos
    # para a insalubridade e periculosidade (que são inputs de elegibilidade)
    lancamento_para_insalubridade_periculosidade = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_para_insalubridade_periculosidade.recebe_insalubridade = True # Para calcular insalubridade
    lancamento_para_insalubridade_periculosidade.recebe_periculosidade = True # Para calcular periculosidade

    # Para periculosidade, precisamos do valor de EV DIAS TRABALHADOS
    # Vamos assumir 0 dias de ferias para que EV DIAS TRABALHADOS seja o salario base
    valor_ev_dias_trabalhados = servico_folha_pagamento.calcular_salario_proporcional_servico(
            funcionario=funcionario_exemplo, # <--- MUDANÇA AQUI!
            cargos=cargos_empresa,           # <--- MUDANÇA AQUI!
            lancamento_mensal=lancamento_para_insalubridade_periculosidade
    )

    # Agora, calcule os valores simulados usando os métodos do serviço:
    adicional_insalubridade_simulado = servico_folha_pagamento.calcular_bonus_insalubridade(
        lancamento_mensal=lancamento_para_insalubridade_periculosidade,
        configuracao_global=configuracao_global_exemplo # Use a fixture, ela já tem SM e %
    )
    adicional_periculosidade_simulado = servico_folha_pagamento.calcular_adicional_periculosidade(
        lancamento_mensal=lancamento_para_insalubridade_periculosidade,
        configuracao_global=configuracao_global_exemplo,
        valor_dias_trabalhados=valor_ev_dias_trabalhados
    )
    # --- FIM DO CÁLCULO REALISTA ---

    base_calc_adicional = salario_base_func + adicional_insalubridade_simulado + adicional_periculosidade_simulado


    configuracao_global_teste = ConfiguracaoGlobal( # Recrie para cada teste
        data_calculo=date(2025, 7, 10),
        salario_minimo=configuracao_global_exemplo.salario_minimo, # Use da fixture
        percentual_insalubridade=configuracao_global_exemplo.percentual_insalubridade, # Use da fixture
        aliquota_fgts_patronal=configuracao_global_exemplo.aliquota_fgts_patronal, # Use da fixture
        aliquota_inss_patronal_media=configuracao_global_exemplo.aliquota_inss_patronal_media, # Use da fixture
        percentual_terco_ferias=configuracao_global_exemplo.percentual_terco_ferias, # Use da fixture
        meses_do_ano=configuracao_global_exemplo.meses_do_ano, # Use da fixture
        horas_jornada_padrao_mensal=220, # <--- Mantenha 220 ou use configuracao_global_exemplo.horas_jornada_padrao_mensal
        percentual_periculosidade=configuracao_global_exemplo.percentual_periculosidade, # Use da fixture
        percentual_adicional_noturno=0.20 # Este é o valor que o teste quer testar para este cenário
    )

    

    lancamento_noturno = copy.deepcopy(lancamento_mensal_exemplo_base)
    lancamento_noturno.quantidade_horas_adicional_noturno = 40.0 # Horas noturnas para teste

    adicional_noturno = servico_folha_pagamento.calcular_adicional_noturno(
        funcionario=funcionario_exemplo, cargos=cargos_empresa,
        configuracao_global=configuracao_global_teste,
        lancamento_mensal=lancamento_noturno,
        valor_adicional_insalubridade=adicional_insalubridade_simulado,
        valor_adicional_periculosidade=adicional_periculosidade_simulado
    )

    adicional_noturno_esperado = (base_calc_adicional / configuracao_global_teste.horas_jornada_padrao_mensal) * \
                                 configuracao_global_teste.percentual_adicional_noturno * \
                                 lancamento_noturno.quantidade_horas_adicional_noturno
    
    assert adicional_noturno == pytest.approx(round(adicional_noturno_esperado, 2))