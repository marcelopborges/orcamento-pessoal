# tests/test_integration.py

import pytest
from datetime import date
from core.entities import Funcionario, Cargo, ConfiguracaoGlobal, LancamentoMensalFuncionario
from core.validators import ValidadorDadosFuncionario, ValidadorDadosCargo
from core.payroll_rules import ServicoFolhaPagamento


def test_processo_completo_desde_dados_brutos():
    """
    Testa o fluxo completo do sistema, desde a validação de dados brutos até o cálculo total da folha.
    """
    raw_employee_data = [
        {
            "CHAPA": "03494", "NOME": "GERALDO CANDIDO DE SOUSA", "SITUACAO": "A",
            "CODIGO_FUNCAO": "4206", "DATA_ADMISSAO": "15/04/2002",
            "DATA_ADMISSAO_PTS": "15/04/2002",
            "SECAO": "01.01.4.10.01.005", 
            "CARGA_HORARIA_MENSAL": "220", "CENTRO_CUSTO": "104101205",
            "CPF": "01776476123",
            "DATA_NASCIMENTO": "01/01/1980",
            "EMPRESA": "Matriz", "EQUIPE": "Operacao", "FUNCAO": "Motorista",
            "VALOR_VALE_TRANSPORTE_MENSAL": 150.0, "VALOR_VALE_REFEICAO_MENSAL": 400.0,
            "PLANO_SAUDE_MENSAL": 300.0, "OUTROS_BENEFICIOS_MENSAIS": 0.0
        },
        {
            "CHAPA": "04694", "NOME": "MARCOS TEIXEIRA MACHADO", "SITUACAO": "A",
            "CODIGO_FUNCAO": "4151", "DATA_ADMISSAO": "03/07/2007",
            "DATA_ADMISSAO_PTS": "03/07/2007",
            "SECAO": "01.01.4.11.02.000",
            "CARGA_HORARIA_MENSAL": "150", "CENTRO_CUSTO": "104101801",
            "CPF": "01776476123",
            "DATA_NASCIMENTO": "01/01/1985",
            "EMPRESA": "Matriz", "EQUIPE": "Projetos", "FUNCAO": "Gerente",
            "VALOR_VALE_TRANSPORTE_MENSAL": 100.0, "VALOR_VALE_REFEICAO_MENSAL": 200.0,
            "PLANO_SAUDE_MENSAL": 50.0, "OUTROS_BENEFICIOS_MENSAIS": 0.0
        }
    ]


    raw_function_data = [
        {"CODIGO_FUNCAO": "4206", "NOME_FUNCAO": "FUNCAO DO GERALDO", "SALARIO": "5500.00"},
        {"CODIGO_FUNCAO": "4151", "NOME_FUNCAO": "FUNCAO DO MARCOS", "SALARIO": "4200.50"}
    ]

    configuracao_global = ConfiguracaoGlobal(
        data_calculo=date(2025, 4, 30),
        salario_minimo=1918.00,
        percentual_insalubridade=0.40,        
        aliquota_fgts_patronal=0.08,
        aliquota_inss_patronal_media=0.20,
        percentual_terco_ferias=0.3333333333333333,
        meses_do_ano=12,
        horas_jornada_padrao_mensal=220 # Adicione este se já estiver na sua ConfiguracaoGlobal
    )
    lancamento_mensal_padrao = LancamentoMensalFuncionario() # Instância com valores padrão


    validador_funcionario = ValidadorDadosFuncionario()
    validador_cargo = ValidadorDadosCargo()
    servico_folha_pagamento = ServicoFolhaPagamento()


    funcionarios_validados = [Funcionario(**validador_funcionario.validate(row)) for row in raw_employee_data]
    cargos_validados = [Cargo(**validador_cargo.validate(row)) for row in raw_function_data]


    custo_total_folha = servico_folha_pagamento.calcular_total_folha_pagamento(
        funcionarios=funcionarios_validados,
        cargos=cargos_validados, 
        configuracao_global=configuracao_global,
        lancamento_mensal_padrao=lancamento_mensal_padrao 
    )

    
    # O custo total deve ser a soma dos salários base: 5500.00 + 4200.50
    assert custo_total_folha == pytest.approx(9700.50)