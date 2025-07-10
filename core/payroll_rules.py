# core/payroll_rules.py

from core.entities import Funcionario, Cargo, ConfiguracaoGlobal, LancamentoMensalFuncionario
from core import formulas # Alterado: Importa o novo módulo 'formulas'
from datetime import date, datetime # Import datetime aqui também se for usado na classe

class ServicoFolhaPagamento:
    
    def obter_salario_funcionario(self, employee: Funcionario, functions: list[Cargo]) -> float:
        """Obtém o salário base do funcionário com base na sua função."""
        for function in functions:
            if employee.codigo_funcao == function.codigo_funcao:
                return function.salario
        return 0.0

    def obter_salario_hora_funcionario(self, employee: Funcionario, functions: list[Cargo]) -> float:
        """Calcula o salário por hora do funcionário, usando a fórmula pura."""
        salario_base = self.obter_salario_funcionario(employee=employee, functions=functions)
        jornada_mensal_horas = int(employee.carga_horaria_mensal)
        return formulas.calcular_salario_hora(salario=salario_base, horas=jornada_mensal_horas)

    
    def obter_anos_servico(self, employee: Funcionario, data_calculo: date) -> float:
        """Calcula os anos de serviço do funcionário, usando a fórmula pura."""
        start_date = employee.data_admissao.date()
        end_date = data_calculo
        # CORREÇÃO AQUI: Chamar a função correta
        return formulas.calcular_tempo_servico(data_inicio=start_date, data_fim=end_date)

    
    def calcular_bonus_insalubridade(self, lancamento_mensal: LancamentoMensalFuncionario, configuracao_global: ConfiguracaoGlobal) -> float:
        if not lancamento_mensal.recebe_insalubridade: 
            return 0.0
        valor_base = configuracao_global.salario_minimo
        percentual = configuracao_global.percentual_insalubridade
        return formulas.calcular_bonus_percentual(valor_base=valor_base, percentual=percentual)


    def calcular_total_folha_pagamento(
        self,
        funcionarios: list[Funcionario],
        cargos: list[Cargo],
        configuracao_global: ConfiguracaoGlobal,
        lancamento_mensal_padrao: LancamentoMensalFuncionario
    ) -> float:
        """
        Calcula o custo total da folha de pagamento para uma lista de funcionários.
        ATENÇÃO: Este método ainda soma apenas o salário base. Para custo total completo,
        ele precisaria utilizar o calcular_detalhamento_custo_total para cada funcionário.
        """
        total_cost = 0.0
        for funcionario in funcionarios:
            salario_funcionario = self.obter_salario_funcionario(funcionario, cargos)
            total_cost += salario_funcionario
        return total_cost
    
    def calcular_salario_proporcional_servico(self, funcionario: Funcionario, cargos: list[Cargo], lancamento_mensal: LancamentoMensalFuncionario) -> float:
        """Orquestra o cálculo do salário proporcional, usando a fórmula pura."""
        salario_base = self.obter_salario_funcionario(funcionario, cargos)
        if salario_base == 0.0:
            return 0.0

        dias_nao_trabalhados = lancamento_mensal.dias_ferias
        total_dias_no_mes = 30 
        return formulas.calcular_salario_proporcional(
            salario_base=salario_base, 
            total_dias_no_mes=total_dias_no_mes, 
            dias_nao_trabalhados=dias_nao_trabalhados 
    )
    def calcular_detalhamento_custo_total( 
        self,
        funcionario: Funcionario,
        cargos: list[Cargo],
        configuracao_global: ConfiguracaoGlobal,
        lancamento_mensal: LancamentoMensalFuncionario
    ) -> dict:
        """
        Gera uma ficha de cálculo completa de proventos e encargos para um funcionário.
        """
        results = {}

        # 1. Proventos
        salario_base_funcionario = self.obter_salario_funcionario(funcionario, cargos)
        results["SALARIO_BASE"] = salario_base_funcionario

        salario_proporcional_calculado = self.calcular_salario_proporcional_servico(
            funcionario=funcionario, functions=cargos, lancamento_mensal=lancamento_mensal
        )
        results["EV_DIAS_TRABALHADOS"] = salario_proporcional_calculado

        adicional_insalubridade = self.calcular_bonus_insalubridade(
            lancamento_mensal=lancamento_mensal, configuracao_global=configuracao_global
        )
        results["EV_ADIC_INSALUBRIDADE"] = adicional_insalubridade

        results["TOTAL_PROVENTOS"] = formulas.calcular_total_proventos(
            salario_base_ou_proporcional=salario_proporcional_calculado,
            adicional_insalubridade=adicional_insalubridade
        )

        # 2. Encargos e Provisões (Usando fórmulas puras e premissas de configuracao_global)
        # REMOVIDOS OS VALORES HARDCODED, AGORA USA configuracao_global
        results["ENCARGO_FGTS"] = formulas.calcular_valor_fgts(salario_base_funcionario, configuracao_global.aliquota_fgts_patronal)
        results["ENCARGO_INSS_EMPRESA"] = formulas.calcular_inss_patronal(salario_base_funcionario, configuracao_global.aliquota_inss_patronal_media)
        results["PROVISAO_FERIAS"] = formulas.calcular_provisao_ferias(salario_base_funcionario, configuracao_global.percentual_terco_ferias, configuracao_global.meses_do_ano)
        results["PROVISAO_13_SALARIO"] = formulas.calcular_provisao_decimo_terceiro_salario(salario_base_funcionario, configuracao_global.meses_do_ano)

        total_encargos_e_provisoes = (
            results["ENCARGO_FGTS"] +
            results["ENCARGO_INSS_EMPRESA"] +
            results["PROVISAO_FERIAS"] +
            results["PROVISAO_13_SALARIO"]
        )
        results["TOTAL_ENCARGOS_E_PROVISOES"] = total_encargos_e_provisoes

        # 3. Benefícios (Agora acessando diretamente do objeto Funcionario)
        total_beneficios_calculados = formulas.somar_beneficios(
            valor_vale_transporte_mensal=funcionario.valor_vale_transporte_mensal,
            valor_vale_refeicao_mensal=funcionario.valor_vale_refeicao_mensal,
            plano_saude_mensal=funcionario.plano_saude_mensal,
            outros_beneficios_mensais=funcionario.outros_beneficios_mensais
        )
        results["TOTAL_BENEFICIOS"] = total_beneficios_calculados

        # 4. Custo Total Final do Empregado
        results["TOTAL_CUSTO_FINAL_DO_EMPREGADO"] = formulas.calcular_custo_total_funcionario(
            salario_base=salario_base_funcionario,
            total_beneficios=results["TOTAL_BENEFICIOS"],
            total_encargos_e_provisoes=results["TOTAL_ENCARGOS_E_PROVISOES"]
        )

        # ATUALIZA O ATRIBUTO custo_total_mensal DO OBJETO FUNCIONARIO
        funcionario.custo_total_mensal = results["TOTAL_CUSTO_FINAL_DO_EMPREGADO"]

        return results
    
    


    def calcular_gratificacao(self, funcionario: Funcionario, configuracao_global: ConfiguracaoGlobal, lancamento_mensal: LancamentoMensalFuncionario) -> float:
        """
        Calcula a gratificação do funcionário, considerando a jornada trabalhada.
        """
        valor_base = funcionario.valor_base_gratificacao_mensal
        horas_trabalhadas = lancamento_mensal.horas_trabalhadas_no_mes # ou de Employee se for atributo fixo
        jornada_padrao = configuracao_global.horas_jornada_padrao_mensal

        return formulas.calcular_gratificacao(valor_base_gratificacao_mensal=valor_base, horas_trabalhadas_no_mes=horas_trabalhadas, jornada_padrao_mensal_horas=jornada_padrao)
    
    def calcular_hora_s_aviso(self, funcionario: Funcionario, cargos: list[Cargo], configuracao_global: ConfiguracaoGlobal, lancamento_mensal: LancamentoMensalFuncionario) -> float:
        """
        Calcula o valor do evento 'Hora S. Aviso'.
        """
        salario_base = self.obter_salario_funcionario(funcionario, cargos)
        jornada_padrao = configuracao_global.horas_jornada_padrao_mensal
        quantidade_horas = lancamento_mensal.quantidade_horas_s_aviso

        return formulas.calcular_hora_s_aviso(salario_base=salario_base, jornada_padrao_mensal_horas=jornada_padrao, quantidade_horas_s_aviso=quantidade_horas)


    def calcular_adicional_periculosidade(self, lancamento_mensal: LancamentoMensalFuncionario, configuracao_global: ConfiguracaoGlobal, valor_dias_trabalhados: float) -> float:
        if not lancamento_mensal.recebe_periculosidade: 
            return 0.0
        percentual = configuracao_global.percentual_periculosidade 
        return formulas.calcular_adicional_periculosidade_formula(valor_dias_trabalhados=valor_dias_trabalhados, percentual_periculosidade=percentual)

    def calcular_adicional_noturno(self, funcionario: Funcionario, cargos: list[Cargo], configuracao_global: ConfiguracaoGlobal, lancamento_mensal: LancamentoMensalFuncionario, valor_adicional_insalubridade: float, valor_adicional_periculosidade: float) -> float:
        """
        Calcula o adicional noturno, com base no salário, insalubridade e periculosidade.
        """
        salario_base = self.obter_salario_funcionario(funcionario, cargos)
        base_calculo_adicional_noturno = salario_base + valor_adicional_insalubridade + valor_adicional_periculosidade
        jornada_padrao = configuracao_global.horas_jornada_padrao_mensal 
        percentual_adicional = configuracao_global.percentual_adicional_noturno 
        quantidade_horas = lancamento_mensal.quantidade_horas_adicional_noturno 

        return formulas.calcular_adicional_noturno_formula(base_calculo_hora_total=base_calculo_adicional_noturno, jornada_padrao_mensal_horas=jornada_padrao, percentual_adicional=percentual_adicional, quantidade_horas_noturnas=quantidade_horas)
