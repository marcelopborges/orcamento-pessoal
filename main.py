# main.py


import os
import json
import datetime
from datetime import date
import copy
import pprint

from core.entities import Employee, Funcao, GlobalConfig, EmployeeMonthlyInput, HistoricalParameter,CenariodeOrcamento, AcaoHeadcount
from core.validators import EmployeeDataValidator, FunctionDataValidator, DataValidationError
from core.payroll_rules import PayrollService
from core.history_manager import HistoryManager
from core.qpa_generator import QPAGenerator

# (Outros imports como core.formulas não são necessários diretamente no main.py,
# pois PayrollService já os utiliza.)

# --- Funções Auxiliares de Display e Carregamento (Adaptadas) ---

def display_full_cost_breakdown(employee_name: str, results: dict):
    """Exibe a ficha de cálculo individual, similar ao seu main.py antigo."""
    print("--- Ficha de Cálculo Individual ---")
    print(f"Funcionário: {employee_name}")
    print("-" * 35)
    pprint.pprint(results)
    print("-" * 35)

def display_orcamento_mensal(orcamento):
    """Exibe um resumo de um orçamento mensal (do contexto QPA)."""
    if not orcamento:
        print("Orçamento não encontrado.")
        return

    print(f"\n--- Orçamento para {orcamento.mes}/{orcamento.ano} ---")
    print(f"  Número total de funcionários: {orcamento.numero_total_funcionarios}")
    print(f"  Custo total do orçamento: R$ {orcamento.custo_total_orcamento:.2f}")
    print("-" * 40)

def display_simulacao_scenario(simulacao_resultado: dict): # Tipo do parâmetro ajustado para 'dict'
    print(f"\n--- Resultado da Simulação do Cenário: {simulacao_resultado['nome_cenario']} ---")
    print(f"  Período: {simulacao_resultado['periodo_simulacao']}")
    print(f"  Custo Total Simulado no Período: R$ {simulacao_resultado['custo_total_simulado']:.2f}")
    print("\n  Detalhes Mensais da Simulação:")
    for mes_str, orcamento_dict in simulacao_resultado['detalhes_mensais'].items(): # Renomeado para orcamento_dict
        print(f"    Mês {mes_str}:")
        # NOVO: Acesse as chaves do dicionário
        print(f"      Número de Funcionários: {orcamento_dict['numero_total_funcionarios']}")
        print(f"      Custo Mensal: R$ {orcamento_dict['custo_total_orcamento']:.2f}")
    print("-" * 50)

# Função para carregar dados históricos (já no main.py da última interação)
def load_historical_data_from_file(file_path: str) -> list[dict]:
    """Carrega dados históricos brutos de um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("O arquivo de histórico deve ser uma lista de objetos.")
            return data
    except FileNotFoundError:
        print(f"Aviso: Arquivo de histórico '{file_path}' não encontrado. Iniciando vazio.")
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao ler arquivo de histórico '{file_path}': {e}. Iniciando vazio.")
        return []

# Função para construir GlobalConfig (já no main.py da última interação)
def build_global_config_for_date(history_manager: HistoryManager, check_date: date) -> GlobalConfig:
    """Constrói uma GlobalConfig para uma data específica a partir do HistoryManager."""
    active_params = history_manager.get_all_active_parameters_on_date(check_date)
    
    required_params = [
        "minimum_wage", "insalubrity_percent", "aliquota_fgts_empresa",
        "aliquota_inss_patronal_media", "percentual_terco_ferias", "meses_do_ano"
    ]
    for param in required_params:
        if param not in active_params or active_params[param] is None:
            raise ValueError(f"Parâmetro histórico '{param}' é obrigatório mas não encontrado ou nulo para {check_date}.")

    return GlobalConfig(
        calculation_date=check_date,
        minimum_wage=active_params.get("minimum_wage"),
        insalubrity_percent=active_params.get("insalubrity_percent"),
        aliquota_fgts_empresa=active_params.get("aliquota_fgts_empresa"),
        aliquota_inss_patronal_media=active_params.get("aliquota_inss_patronal_media"),
        percentual_terco_ferias=active_params.get("percentual_terco_ferias"),
        meses_do_ano=active_params.get("meses_do_ano")
    )

# main.py (continuação)

def main():
    # --- Configuração de Caminhos de Arquivos ---
    employee_data_file = "dados_funcionarios.json"
    funcao_salario_file = "dados_funcoes_salario.json"
    historical_params_file = "dados_historicos_parametros.json" # NOVO
    qpa_scenario_actions_file = "cenario_qpa_acoes.json"
    
    current_qpa_output_file = "qpa_atual_raio_x.csv"
    simulated_qpa_output_file = "qpa_simulado_cenario.csv"

    # --- 1. Geração dos Arquivos de Dados de Exemplo (se não existirem) ---
    # Estes dados de exemplo são CRUCIAIS para o GE e o sistema.
    # Garanta que o 'Employee' de exemplo tenha os campos necessários para benefícios
    # (valor_vale_transporte_mensal etc.) se você optou por eles no Employee.
    # Se GlobalConfig precisa desses valores, eles devem estar no dados_historicos_parametros.json.

    # Dados de funções e salários (para Funcao)
    sample_funcoes_salario_content = [
        {"CODIGO_FUNCAO": "1001", "NOME_FUNCAO": "OPERADOR I", "SALARIO": "2500.00"},
        {"CODIGO_FUNCAO": "4003", "NOME_FUNCAO": "ANALISTA ADMINISTRATIVO I", "SALARIO": "5202.76"},
        {"CODIGO_FUNCAO": "4206", "NOME_FUNCAO": "FUNCAO DO GERALDO", "SALARIO": "5202.76"}, # Função do Geraldo
        {"CODIGO_FUNCAO": "9009", "NOME_FUNCAO": "GERENTE DE AREA", "SALARIO": "12500.50"},
        {"CODIGO_FUNCAO": "0001", "NOME_FUNCAO": "Desenvolvedor Backend Júnior", "SALARIO": "4500.00"}, # Do exemplo anterior
        {"CODIGO_FUNCAO": "0002", "NOME_FUNCAO": "Gerente de Projeto Sênior", "SALARIO": "6000.00"},
        {"CODIGO_FUNCAO": "0003", "NOME_FUNCAO": "Motorista Cat. D", "SALARIO": "3000.00"},
        {"CODIGO_FUNCAO": "0004", "NOME_FUNCAO": "Arquiteto de Soluções", "SALARIO": "7000.00"},
        {"CODIGO_FUNCAO": "0005", "NOME_FUNCAO": "Analista de Dados", "SALARIO": "5500.00"}
    ]
    with open(funcao_salario_file, 'w', encoding='utf-8') as f:
        json.dump(sample_funcoes_salario_content, f, indent=2)
    print(f"Arquivo de funções/salários '{funcao_salario_file}' criado/atualizado.")

    # Dados de funcionários (para Employee)
    # ATENÇÃO: Adicione aqui os campos de benefícios que você tiver no seu Employee,
    # mesmo que estejam como 0.0, para que o validador e o calculate_full_cost_breakdown os vejam.
    sample_employees_content = [
        # O funcionário do seu main.py original
        {"CHAPA": "03494", "NOME": "GERALDO CANDIDO DE SOUSA", "SITUACAO": "A",
         "CODIGO_FUNCAO": "4206", "DATA_ADMISSAO": "15/04/2002",
         "DATA_ADMISSAO_PTS": "15/04/2002", "DATA_NASCIMENTO": "01/01/1980",
         "SESSAO": "01.01.4.10.01.005", "JORNADA": "220", "CPF": "25216977880",
         "CENTRO_CUSTO": "104101205",
         "empresa": "Matriz", "equipe": "Operacao", "funcao": "Motorista", # Adicionados para QPA
         "valor_vale_transporte_mensal": 150.00, "valor_vale_refeicao_mensal": 400.00,
         "plano_saude_mensal": 300.00, "outros_beneficios_mensais": 0.0},
        
    ]
    with open(employee_data_file, 'w', encoding='utf-8') as f:
        json.dump(sample_employees_content, f, indent=2)
    print(f"Arquivo de dados de funcionários '{employee_data_file}' criado/atualizado.")

    # Dados históricos de parâmetros (para HistoricalParameter)
    sample_historical_params_content = [
        {"id": 1, "parameter_name": "minimum_wage", "value": 1320.00, "start_date": "2023-01-01", "end_date": "2023-12-31"},
        {"id": 2, "parameter_name": "minimum_wage", "value": 1412.00, "start_date": "2024-01-01", "end_date": None},
        {"id": 3, "parameter_name": "aliquota_fgts_empresa", "value": 0.08, "start_date": "2000-01-01", "end_date": None},
        {"id": 4, "parameter_name": "aliquota_inss_patronal_media", "value": 0.20, "start_date": "2010-01-01", "end_date": "2023-12-31"},
        {"id": 5, "parameter_name": "aliquota_inss_patronal_media", "value": 0.22, "start_date": "2024-01-01", "end_date": None},
        {"id": 6, "parameter_name": "insalubrity_percent", "value": 0.40, "start_date": "2000-01-01", "end_date": None},
        {"id": 7, "parameter_name": "percentual_terco_ferias", "value": (1/3), "start_date": "1988-10-05", "end_date": None},
        {"id": 8, "parameter_name": "meses_do_ano", "value": 12, "start_date": "1900-01-01", "end_date": None}
    ]
    with open(historical_params_file, 'w', encoding='utf-8') as f:
        json.dump(sample_historical_params_content, f, indent=2)
    print(f"Arquivo de dados históricos de parâmetros '{historical_params_file}' criado/atualizado.")

    # Ações de QPA (para CenariodeOrcamento e AcaoHeadcount)
    ano_cenario = date.today().year
    mes_cenario = (date.today().month % 12) + 1
    if mes_cenario == 1: ano_cenario += 1

    qpa_actions_data = {
        "nome_cenario": "Cenario_QPA_Planejamento_Semestral",
        "ano_inicio": ano_cenario,
        "mes_inicio": mes_cenario,
        "duracao_meses": 6,
        "acoes_headcount": [
            {
                "tipo": "ACRESCIMO_QPA", "data_efetivacao": f"{ano_cenario}-{mes_cenario:02d}-01",
                "empresa": "Filial SP", "equipe": "Operacao", "id_funcao": "0003", "quantidade": 2,
                "salario_base_simulado": 3150.00,
                "valor_vale_transporte_simulado": 110.0, "valor_vale_refeicao_simulado": 310.0,
                "plano_saude_simulado": 210.0, "outros_beneficios_simulados": 0.0
            },
            {
                "tipo": "REDUCAO_QPA", "data_efetivacao": (date.today() + datetime.timedelta(days=150)).strftime("%Y-%m-%d"),
                "empresa": "Matriz", "equipe": "Projetos", "id_funcao": "0002", "quantidade": 1
            }
        ]
    }
    with open(qpa_scenario_actions_file, 'w', encoding='utf-8') as f:
        json.dump(qpa_actions_data, f, indent=2)
    print(f"Arquivo de ações de cenário QPA '{qpa_scenario_actions_file}' criado/atualizado.")

    # 3. Carregamento de Dados e Inicialização de Serviços
    employee_validator = EmployeeDataValidator()
    function_validator = FunctionDataValidator()

    # Carregar dados históricos e criar o HistoryManager
    historical_raw_data = load_historical_data_from_file(historical_params_file)
    history_manager = HistoryManager(historical_raw_data)
    
    # NOVO: Validar e processar funções
    functions_list_validated = []
    for func_raw_data in sample_funcoes_salario_content: # Itera sobre a lista
        try:
            # Chama o validate para CADA DICIONÁRIO na lista
            validated_func_data = function_validator.validate(func_raw_data)
            functions_list_validated.append(Funcao(**validated_func_data))
        except DataValidationError as e:
            print(f"Erro de validação para função: {func_raw_data.get('CODIGO_FUNCAO', 'N/A')}: {e}. Função ignorada.")
            
    if not functions_list_validated:
        print("Nenhuma função válida carregada. O programa será encerrado.")
        exit(1)
        
    functions_map = {f.codigo_funcao: f for f in functions_list_validated} # Cria o mapa após validar todos

    # NOVO: Validar e processar funcionários
    employees_list = []
    for emp_raw_data in sample_employees_content: # Itera sobre a lista
        try:
            # Chama o validate para CADA DICIONÁRIO na lista
            validated_emp_data = employee_validator.validate(emp_raw_data)
            
            # Preenche o objeto Employee
            func_info = functions_map.get(validated_emp_data['codigo_funcao'])
            if not func_info:
                print(f"Aviso: Função '{validated_emp_data['codigo_funcao']}' não encontrada para funcionário {validated_emp_data.get('chapa', 'N/A')}. Funcionário ignorado.")
                continue
            
            employee_obj = Employee(
                chapa=validated_emp_data['chapa'], nome=validated_emp_data['nome'], situacao=validated_emp_data['situacao'],
                codigo_funcao=validated_emp_data['codigo_funcao'], data_admissao=validated_emp_data['data_admissao'],
                data_admissao_pts=validated_emp_data['data_admissao_pts'], data_nascimento=validated_emp_data['data_nascimento'],
                sessao=validated_emp_data['sessao'], jornada=validated_emp_data['jornada'], cpf=validated_emp_data['cpf'],
                centro_custo=validated_emp_data['centro_custo'],
                empresa=validated_emp_data.get('empresa', ''), # Usar .get() para campos opcionais caso seu JSON de exemplo não os tenha para todos
                equipe=validated_emp_data.get('equipe', ''),
                funcao=validated_emp_data.get('funcao', ''), # Nome da função em si
                valor_vale_transporte_mensal=validated_emp_data.get('valor_vale_transporte_mensal', 0.0),
                valor_vale_refeicao_mensal=validated_emp_data.get('valor_vale_refeicao_mensal', 0.0),
                plano_saude_mensal=validated_emp_data.get('plano_saude_mensal', 0.0),
                outros_beneficios_mensais=validated_emp_data.get('outros_beneficios_mensais', 0.0)
            )
            employees_list.append(employee_obj)
        except DataValidationError as e:
            print(f"Erro de validação para funcionário {emp_raw_data.get('CHAPA', 'N/A')}: {e}. Funcionário ignorado.")
        except Exception as e: # Captura outros erros inesperados durante o processamento
            print(f"Erro inesperado ao processar funcionário {emp_raw_data.get('CHAPA', 'N/A')}: {e}. Funcionário ignorado.")

    if not employees_list:
        print("Nenhum funcionário válido carregado. O programa será encerrado.")
        exit(1)
    # Instanciar o PayrollService
    payroll_service = PayrollService()

    # --- 4. Exemplo de Cálculo Individual (do seu main.py antigo) ---
    print("\n--- Demonstração de Cálculo Individual (Raio-X) ---")
    geraldo_employee = next((e for e in employees_list if e.chapa == "03494"), None)
    if geraldo_employee:
        # Precisamos de GlobalConfig para a data de cálculo do Geraldo
        # Use a data de cálculo do cenário ou uma data fixa para este exemplo.
        geraldo_calculation_date = date(2025, 4, 30)
        geraldo_global_config = build_global_config_for_date(history_manager, geraldo_calculation_date)
        
        # MonthlyInput para o Geraldo
        geraldo_monthly_input = EmployeeMonthlyInput(
            vacation_days=10, receives_insalubrity=True
        )

        geraldo_results = payroll_service.calculate_full_cost_breakdown(
            employee=geraldo_employee,
            functions=list(functions_map.values()), # Passa a lista de objetos Funcao
            global_config=geraldo_global_config,
            monthly_input=geraldo_monthly_input
        )
        display_full_cost_breakdown(geraldo_employee.nome, geraldo_results)
    else:
        print("Funcionário Geraldo não encontrado nos dados carregados.")


    # --- 5. Geração do QPA do Raio-X Atual ---
    print("\n--- Geração do QPA do Raio-X Atual ---")
    # Para o QPA atual, calculamos o custo total de cada funcionário
    # para a data de cálculo atual (ex: hoje ou data do início do cenário)
    qpa_current_date = date.today()
    qpa_global_config = build_global_config_for_date(history_manager, qpa_current_date)

    employees_with_calculated_cost = []
    for emp in employees_list:
        emp_copy = copy.deepcopy(emp) # Trabalhe com cópias para não alterar os objetos originais
        # Para calcular o custo, precisamos de um monthly_input.
        # Para o raio-x, podemos usar um monthly_input padrão (sem férias, insalubridade, etc.)
        # ou um input real se você tiver dados mensais para todos.
        default_monthly_input_for_qpa = EmployeeMonthlyInput() # Padrão
        
        # Chame o cálculo para cada funcionário
        payroll_service.calculate_full_cost_breakdown(
            employee=emp_copy,
            functions=list(functions_map.values()),
            global_config=qpa_global_config,
            monthly_input=default_monthly_input_for_qpa
        )
        employees_with_calculated_cost.append(emp_copy)

    qpa_generator = QPAGenerator()
    qpa_actual_data = qpa_generator.generate_qpa_summary(employees_with_calculated_cost)
    qpa_generator.export_qpa_to_csv(qpa_actual_data, current_qpa_output_file)


    # --- 6. Simulação de Cenário QPA ---
    print("\n--- Simulação de Cenário QPA ---")
    try:
        with open(qpa_scenario_actions_file, 'r', encoding='utf-8') as f:
            qpa_scenario_data = json.load(f)
        
        cenario_qpa = CenariodeOrcamento(
            nome_cenario=qpa_scenario_data['nome_cenario'],
            ano_inicio=qpa_scenario_data['ano_inicio'],
            mes_inicio=qpa_scenario_data['mes_inicio'],
            duracao_meses=qpa_scenario_data['duracao_meses'],
            acoes_headcount=[AcaoHeadcount(**acao) for acao in qpa_scenario_data['acoes_headcount']]
        )
        
        # Agora o OrcamentoService precisa de PayrollService e HistoryManager para construir GlobalConfig
        # Ajuste a inicialização do OrcamentoService para receber HistoryManager e o validador.
        # Se você ainda não tem um OrcamentoService, teríamos que criá-lo.
        # Pelo seu erro, OrcamentoService não é visível ou não foi definido.
        # Vamos assumir que OrcamentoService precisa ser criado e vai usar PayrollService e HistoryManager
        # para simular.

        # --- AQUI É ONDE PRECISAMOS DE UM OrcamentoService ---
        # Se você já tem um OrcamentoService em core/services.py (que refatoramos antes),
        # ele precisa ser capaz de receber o PayrollService e o HistoryManager.
        
        # Por agora, para que o main.py compile, vou SIMPLIFICAR e fazer a simulação
        # diretamente aqui, sem uma classe OrcamentoService.
        # MAS, a melhor prática é ter um OrcamentoService para isso.
        
        # Início da Lógica de Simulação no main.py (Temporário, idealmente em OrcamentoService)
        # Funcionários para a simulação:
        funcionarios_atuais_simulacao = {e.chapa: copy.deepcopy(e) for e in employees_list}
        simulacao_mensal_results = {}
        
        current_sim_date = date(cenario_qpa.ano_inicio, cenario_qpa.mes_inicio, 1)

        for i in range(cenario_qpa.duracao_meses):
            mes_simulacao = current_sim_date.month
            ano_simulacao = current_sim_date.year

            # Construir GlobalConfig para o mês da simulação
            current_sim_global_config = build_global_config_for_date(history_manager, current_sim_date)

            # Aplicar ações de headcount para o mês atual
            acoes_do_mes = [
                acao for acao in cenario_qpa.acoes_headcount
                if datetime.datetime.strptime(acao.data_efetivacao, "%Y-%m-%d").year == ano_simulacao and
                   datetime.datetime.strptime(acao.data_efetivacao, "%Y-%m-%d").month == mes_simulacao
            ]

            for acao in acoes_do_mes:
                if acao.tipo == "ACRESCIMO_QPA":
                    # Gerar chapa temporária
                    temp_chapa_base = max([int(e.chapa) for e in funcionarios_atuais_simulacao.values() if e.chapa.isdigit()]) if funcionarios_atuais_simulacao else 0
                    
                    for k in range(acao.quantidade):
                        new_chapa = str(temp_chapa_base + 1 + k).zfill(5)
                        # Obter Funcao de acordo com id_funcao
                        simulated_funcao = functions_map.get(acao.id_funcao)
                        if not simulated_funcao:
                            print(f"Aviso: Função simulada '{acao.id_funcao}' não encontrada. Contratação ignorada.")
                            continue

                        simulated_employee = Employee(
                            chapa=new_chapa,
                            nome=f"Simulado {simulated_funcao.nome_funcao} {new_chapa}",
                            situacao="A", # Ativo
                            codigo_funcao=acao.id_funcao,
                            data_admissao=datetime.datetime.strptime(acao.data_efetivacao, "%Y-%m-%d"),
                            data_admissao_pts=datetime.datetime.strptime(acao.data_efetivacao, "%Y-%m-%d"),
                            data_nascimento=datetime.datetime(1990, 1, 1), # Data de nascimento genérica
                            sessao="99.99.9.99.99.99999", jornada="220", cpf="00000000000", # Dados genéricos
                            centro_custo="000000000",
                            empresa=acao.empresa, equipe=acao.equipe, funcao=simulated_funcao.nome_funcao,
                            valor_vale_transporte_mensal=acao.valor_vale_transporte_simulado,
                            valor_vale_refeicao_mensal=acao.valor_vale_refeicao_simulado,
                            plano_saude_mensal=acao.plano_saude_simulado,
                            outros_beneficios_mensais=acao.outros_beneficios_simulados
                        )
                        funcionarios_atuais_simulacao[new_chapa] = simulated_employee
                        print(f"  [Simulação {ano_simulacao}/{mes_simulacao:02d}] ACRESCIDO QPA: {simulated_employee.nome} ({simulated_employee.empresa}/{simulated_employee.equipe}/{simulated_employee.funcao})")
                    temp_chapa_base += acao.quantidade # Atualiza para próxima rodada

                elif acao.tipo == "REDUCAO_QPA":
                    # Lógica simplificada: remove um número de funcionários do grupo alvo.
                    # Não se preocupa com quem é removido, apenas com a contagem.
                    # Pega os IDs/Chapas que correspondem ao grupo
                    chapas_do_grupo = [
                        emp.chapa for emp in funcionarios_atuais_simulacao.values()
                        if emp.empresa == acao.empresa and emp.equipe == acao.equipe and emp.codigo_funcao == acao.id_funcao # Checa codigo_funcao
                    ]
                    num_to_remove = min(acao.quantidade, len(chapas_do_grupo))
                    
                    if num_to_remove > 0:
                        # Remove os de maior chapa (mais recentes ou simulados)
                        chapas_a_remover = sorted(chapas_do_grupo, reverse=True)[:num_to_remove]
                        for chapa in chapas_a_remover:
                            if chapa in funcionarios_atuais_simulacao:
                                removed_name = funcionarios_atuais_simulacao[chapa].nome
                                del funcionarios_atuais_simulacao[chapa]
                                print(f"  [Simulação {ano_simulacao}/{mes_simulacao:02d}] REDUÇÃO QPA: {removed_name} ({acao.empresa}/{acao.equipe}/{acao.id_funcao})")
                        print(f"  Total de {num_to_remove} reduzidos em {acao.empresa}/{acao.equipe}/{acao.id_funcao}.")
                    else:
                        print(f"  [Simulação {ano_simulacao}/{mes_simulacao:02d}] Aviso: Nada a reduzir em {acao.empresa}/{acao.equipe}/{acao.id_funcao}.")

            # Preparar funcionários para o cálculo do mês atual da simulação
            employees_for_current_month_calc = []
            for emp_chapa, emp_obj in funcionarios_atuais_simulacao.items():
                emp_copy_for_calc = copy.deepcopy(emp_obj)
                # Para o cálculo do custo, usar um monthly_input padrão ou real para o mês simulado
                # O monthly_input_for_sim é simplificado. Em cenário real, viria de dados históricos.
                monthly_input_for_sim = EmployeeMonthlyInput() # Default para simulação
                
                payroll_service.calculate_full_cost_breakdown(
                    employee=emp_copy_for_calc,
                    functions=list(functions_map.values()),
                    global_config=current_sim_global_config, # Usa a config do mês da simulação
                    monthly_input=monthly_input_for_sim
                )
                employees_for_current_month_calc.append(emp_copy_for_calc)

            # Criar um objeto OrcamentoMensal (este modelo não existe ainda em core/models.py com este nome)
            # Você precisaria criar a dataclass OrcamentoMensal em core/models.py para isso funcionar.
            # Supondo que OrcamentoMensal tem (ano, mes, funcionarios_detalhe)
            # Para o QPA, o custo total do orçamento será a soma do custo total de cada funcionário.
            total_custo_mensal_simulacao = sum(emp.custo_total_mensal for emp in employees_for_current_month_calc)
            
            # Precisamos da classe OrcamentoMensal. Se não tiver no entities, vamos precisar criar.
            # Por agora, para não quebrar, vamos usar um dicionário simples.
            # O ideal é ter a classe OrcamentoMensal em core/models.py
            # from core.models import OrcamentoMensal # Importar OrcamentoMensal aqui se ela existir

            simulacao_mensal_results[f"{ano_simulacao}-{mes_simulacao:02d}"] = {
                "ano": ano_simulacao,
                "mes": mes_simulacao,
                "numero_total_funcionarios": len(employees_for_current_month_calc),
                "custo_total_orcamento": total_custo_mensal_simulacao,
                "funcionarios_detalhe": employees_for_current_month_calc # Lista de objetos Employee calculados
            }
            
            current_sim_date += datetime.timedelta(days=30) # Avança 1 mês (simplificado)

        # Preparar resultado final da simulação para display_simulacao_scenario
        final_sim_data = {
            "nome_cenario": cenario_qpa.nome_cenario,
            "periodo_simulacao": f"{cenario_qpa.ano_inicio}-{cenario_qpa.mes_inicio:02d} a {ano_simulacao}-{mes_simulacao:02d}",
            "custo_total_simulado": sum(r["custo_total_orcamento"] for r in simulacao_mensal_results.values()),
            "detalhes_mensais": simulacao_mensal_results
        }
        display_simulacao_scenario(final_sim_data)


        # Geração do QPA resultante da simulação (para o último mês)
        if simulacao_mensal_results:
            last_month_key = sorted(simulacao_mensal_results.keys())[-1]
            last_month_sim_data = simulacao_mensal_results[last_month_key]
            
            # O gerador de QPA precisa de uma lista de objetos Funcionario, não de dicionários.
            # Ajuste aqui para pegar os objetos Employee calculados.
            qpa_simulado_data = qpa_generator.generate_qpa_summary(last_month_sim_data["funcionarios_detalhe"])
            qpa_generator.export_qpa_to_csv(qpa_simulado_data, simulated_qpa_output_file)

    except FileNotFoundError as e:
        print(f"Erro: Arquivo de ações QPA '{qpa_scenario_actions_file}' não encontrado: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Erro ao ler arquivo de ações QPA '{qpa_scenario_actions_file}': {e}")
        return
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a simulação do QPA: {e}")
        import traceback
        traceback.print_exc() # Para ver o traceback completo

    print("\n--- Processo de Orçamento e Simulação QPA Concluído ---")

# Ponto de entrada
if __name__ == "__main__":
    main()