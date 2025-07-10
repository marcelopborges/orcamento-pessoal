# core/payroll_rules.py

from core.entities import Employee, Funcao, GlobalConfig, EmployeeMonthlyInput
from core import formulas # Alterado: Importa o novo módulo 'formulas'
from datetime import date, datetime # Import datetime aqui também se for usado na classe

class PayrollService:
    
    def get_employee_salary(self, employee: Employee, functions: list[Funcao]) -> float:
        """Obtém o salário base do funcionário com base na sua função."""
        for function in functions:
            if employee.codigo_funcao == function.codigo_funcao:
                return function.salario
        return 0.0

    def get_employee_hourly_wage(self, employee: Employee, functions: list[Funcao]) -> float:
        """Calcula o salário por hora do funcionário, usando a fórmula pura."""
        base_salary = self.get_employee_salary(employee=employee, functions=functions)
        monthly_hours = int(employee.jornada)
        return formulas.calculate_hourly_wage_formula(salary=base_salary, hours=monthly_hours)
    
    def get_employee_years_of_service(self, employee: Employee, calculation_date: date) -> float:
        """Calcula os anos de serviço do funcionário, usando a fórmula pura."""
        start_date = employee.data_admissao.date()
        end_date = calculation_date
        return formulas.calcular_salario_hora_formula(start_date=start_date, end_date=end_date)
    
    def calculate_insalubrity_bonus(self, monthly_input: EmployeeMonthlyInput, global_config: GlobalConfig) -> float:
        """Calcula o adicional de insalubridade, usando a fórmula pura."""
        if not monthly_input.receives_insalubrity:
            return 0.0

        base_value = global_config.minimum_wage
        percent = global_config.insalubrity_percent
        return formulas.calculate_percentage_bonus_formula(base_value=base_value, percent=percent)

    def calculate_total_payroll(
        self,
        employees: list[Employee], # Tipo mais específico
        functions: list[Funcao], # Tipo mais específico
        global_config: GlobalConfig,
        default_monthly_input: EmployeeMonthlyInput
    ) -> float:
        """
        Calcula o custo total da folha de pagamento.
        ATENÇÃO: Este método ainda soma apenas o salário base. Para custo total completo,
        ele precisaria utilizar o calculate_full_cost_breakdown para cada funcionário.
        """
        total_cost = 0.0
        for employee in employees:
            employee_salary = self.get_employee_salary(employee, functions)
            total_cost += employee_salary
        return total_cost
    
    def calculate_proportional_salary(
        self,
        employee: Employee,
        functions: list[Funcao],
        monthly_input: EmployeeMonthlyInput
    ) -> float:
        """Orquestra o cálculo do salário proporcional, usando a fórmula pura."""
        base_salary = self.get_employee_salary(employee, functions)
        if base_salary == 0.0:
            return 0.0

        non_worked_days = monthly_input.vacation_days
        total_days_in_month = 30 # A ser parametrizado futuramente
        return formulas.calculate_proportional_salary_formula(
            base_salary=base_salary,
            total_days_in_month=total_days_in_month,
            non_worked_days=non_worked_days
        )
    
    def calculate_full_cost_breakdown(
        self,
        employee: Employee,
        functions: list[Funcao],
        global_config: GlobalConfig,
        monthly_input: EmployeeMonthlyInput
    ) -> dict:
        """
        Gera uma ficha de cálculo completa de proventos e encargos para um funcionário.
        """
        results = {}

        # 1. Proventos
        base_salary = self.get_employee_salary(employee, functions)
        results["SALARIO_BASE"] = base_salary

        proportional_salary_calculated = self.calculate_proportional_salary(employee, functions, monthly_input)
        results["EV_DIAS_TRABALHADOS"] = proportional_salary_calculated

        adicional_insalubridade = self.calculate_insalubrity_bonus(monthly_input, global_config)
        results["EV_ADIC_INSALUBRIDADE"] = adicional_insalubridade

        results["TOTAL_PROVENTOS"] = formulas.calculate_total_proventos_formula(
            salario_base_ou_proporcional=proportional_salary_calculated,
            adicional_insalubridade=adicional_insalubridade
        )

        # 2. Encargos e Provisões (Usando fórmulas puras e premissas de global_config)
        # ATENÇÃO: As alíquotas abaixo devem vir de global_config ou outro local de premissas.
        # Substitua os valores hardcoded por atributos de global_config, exemplo:
        # aliquota_fgts = global_config.aliquota_fgts_empresa
        # aliquota_inss_empresa = global_config.aliquota_inss_patronal
        # terco_ferias_percent = global_config.terco_ferias_percent
        # meses_ano = global_config.meses_do_ano # Ou um valor fixo de 12

        # Exemplo com valores hardcoded TEMPORÁRIOS para demonstração, SUBSTITUA COM DADOS REAIS!
        aliquota_fgts_exemplo = 0.08
        aliquota_inss_empresa_exemplo = 0.20
        terco_ferias_percent_exemplo = (1/3)
        meses_ano_exemplo = 12 # Assume 12 meses para provisão anual

        results["ENCARGO_FGTS"] = formulas.calculate_fgts_amount_formula(base_salary, aliquota_fgts_exemplo)
        results["ENCARGO_INSS_EMPRESA"] = formulas.calculate_inss_patronal_formula(base_salary, aliquota_inss_empresa_exemplo)
        results["PROVISAO_FERIAS"] = formulas.calculate_vacation_provision_formula(base_salary, terco_ferias_percent_exemplo, meses_ano_exemplo)
        results["PROVISAO_13_SALARIO"] = formulas.calculate_thirteenth_salary_provision_formula(base_salary, meses_ano_exemplo)

        total_encargos_e_provisoes = (
            results["ENCARGO_FGTS"] +
            results["ENCARGO_INSS_EMPRESA"] +
            results["PROVISAO_FERIAS"] +
            results["PROVISAO_13_SALARIO"]
        )
        results["TOTAL_ENCARGOS_E_PROVISOES"] = total_encargos_e_provisoes

        # 3. Benefícios (Assumindo que os valores estão em EmployeeMonthlyInput ou Employee)
        # Se os benefícios de VT, VR, etc. não estiverem no monthly_input, você precisará buscá-los
        # do objeto Employee ou de outro lugar.
        total_beneficios_calculados = formulas.sum_benefits_formula(
            getattr(monthly_input, 'extra_hours_50', 0.0), # Seu EmployeeMonthlyInput tem extra_hours_50, etc.
            getattr(monthly_input, 'extra_hours_100', 0.0),
            getattr(monthly_input, 'valor_vale_transporte_mensal', 0.0), # Se EmployeeMonthlyInput não tiver isso, obter de Employee
            getattr(monthly_input, 'valor_vale_refeicao_mensal', 0.0) # E assim por diante para outros benefícios
        )
        # O EmployeeMonthlyInput que você me passou só tem extra_hours e receives_insalubrity.
        # Os valores de benefícios como VT, VR, Plano Saúde, etc., devem vir do objeto Employee
        # (seus dados de entrada) ou de um `GlobalConfig` para valores padrão.
        # Por hora, vou deixar como `getattr(monthly_input, 'valor_...', 0.0)` mas você precisará
        # mapear de onde vêm esses dados no seu `Employee` ou em algum outro lugar.
        
        # Adaptação para o EmployeeMonthlyInput que você me forneceu:
        # Se os benefícios não estão em EmployeeMonthlyInput, eles deveriam estar em Employee.
        # Por enquanto, vou usar 0.0 para os que não estão no seu EmployeeMonthlyInput e que são novos
        total_beneficios_calculados_temp = formulas.sum_benefits_formula(
            getattr(employee, 'valor_vale_transporte_mensal', 0.0), # Assumindo que estão no Employee
            getattr(employee, 'valor_vale_refeicao_mensal', 0.0),
            getattr(employee, 'plano_saude_mensal', 0.0),
            getattr(employee, 'outros_beneficios_mensais', 0.0)
        )
        results["TOTAL_BENEFICIOS"] = total_beneficios_calculados_temp


        # 4. Custo Total Final do Empregado
        results["TOTAL_CUSTO_FINAL_DO_EMPREGADO"] = formulas.calculate_total_employee_cost_formula(
            salario_base=base_salary,
            total_beneficios=results["TOTAL_BENEFICIOS"], # Usar o total de benefícios calculado
            total_encargos_e_provisoes=results["TOTAL_ENCARGOS_E_PROVISOES"]
        )
        
        return results