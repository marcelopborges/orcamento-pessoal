from datetime import date
import pprint
from core.entities import Employee, Funcao, GlobalConfig, EmployeeMonthlyInput
from core.validators import EmployeeDataValidator, FunctionDataValidator
from core.services import PayrollService

# =================================================================
# 1. SIMULANDO OS DADOS DE ENTRADA
# =================================================================
# Usaremos os dados de apenas um funcionário para ver o cálculo individual
raw_employee_data = {
    "CHAPA": "03494", "NOME": "GERALDO CANDIDO DE SOUSA", "SITUACAO": "A",
    "CODIGO_FUNCAO": "4206", "DATA_ADMISSAO": "15/04/2002",
    "DATA_ADMISSAO_PTS": "15/04/2002",
    "SESSAO": "01.01.4.10.01.005", "JORNADA": "220", "CENTRO_CUSTO": "104101205",
    "CPF": "25216977880", "DATA_NASCIMENTO": "01/01/1980"
}

# Para este funcionário, precisamos da sua função correspondente
raw_function_data = [
    {"CODIGO_FUNCAO": "4206", "NOME_FUNCAO": "FUNCAO DO GERALDO", "SALARIO": "5202.76"},
    # Poderíamos ter outras funções aqui, o serviço encontrará a correta
]

# Inputs para o mês do cálculo (Abril/2025)
global_config = GlobalConfig(
    calculation_date=date(2025, 4, 30),
    minimum_wage=1918.00,
    insalubrity_percent=0.40
)
# Simulando que este funcionário teve 10 dias de férias e recebe insalubridade
monthly_input = EmployeeMonthlyInput(
    vacation_days=10,
    receives_insalubrity=True
)

# =================================================================
# 2. ORQUESTRAÇÃO DO CÁLCULO
# =================================================================
# Instanciar as ferramentas
employee_validator = EmployeeDataValidator()
function_validator = FunctionDataValidator()
service = PayrollService()

# Validar e criar as entidades
employee = Employee(**employee_validator.validate(raw_employee_data))
functions = [Funcao(**function_validator.validate(f)) for f in raw_function_data]

# Chamar o método mestre que gera a ficha de cálculo
calculation_results = service.calculate_full_cost_breakdown(
    employee=employee,
    functions=functions,
    global_config=global_config,
    monthly_input=monthly_input
)

# =================================================================
# 3. EXIBINDO O RESULTADO FINAL
# =================================================================
print("--- Ficha de Cálculo Individual ---")
print(f"Funcionário: {raw_employee_data['NOME']}")
print("-" * 35)
pprint.pprint(calculation_results)
print("-" * 35)