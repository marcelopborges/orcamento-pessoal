from core.entities import Employee, Funcao, GlobalConfig, EmployeeMonthlyInput
from core.payroll_rules import calculate_hourly_wage, calculate_years_of_service,calculate_percentage_bonus,calculate_proportional_salary
from datetime import date


class PayrollService:
    
    def get_employee_salary(self, employee: Employee, functions: list[Funcao])  -> float:

        for function in functions:
            if employee.codigo_funcao == function.codigo_funcao:
                return function.salario
        

#TODO: Existe alguma regra para se computar salário, por exemplo, existe algum status de funcionário
#que não deve ser considerado baseado no status? Neste trecho só estou pegando o valor do salário baseado na função.
    def get_employee_hourly_wage(self, employee: Employee, functions: list[Funcao])  -> float:
        base_salary = self.get_employee_salary(employee=employee, functions=functions)
        monthly_hours = int(employee.jornada)
        hourly_wage = calculate_hourly_wage(salary=base_salary, hours = monthly_hours)
        return hourly_wage
    
    def get_employee_years_of_service(self, employee: Employee, calculation_date: date)->float:
        start_date = employee.data_admissao.date()
        end_date = calculation_date
        years_of_service = calculate_years_of_service(start_date=start_date, end_date=end_date)
        return years_of_service
    
    def calculate_insalubrity_bonus(self, monthly_input: EmployeeMonthlyInput, global_config: GlobalConfig) -> float:
        """
        Calcula o adicional de insalubridade com base nos inputs e configurações.
        """
        # Verifica se o funcionário recebe insalubridade
        if not monthly_input.receives_insalubrity:
            return 0.0

        # Recebe os parâmetros necessários da configuração global
        base_value = global_config.minimum_wage
        percent = global_config.insalubrity_percent

        # Calcula o bônus de insalubridade
        bonus = calculate_percentage_bonus(
            base_value=base_value,
            percent=percent
        )        
        return bonus

    def calculate_total_payroll(
        self,
        employees: list,
        functions: list,
        global_config: object,
        default_monthly_input: object
    ) -> float:
        """
        Calcula o custo total da folha de pagamento para uma lista de funcionários.    
        """
        total_cost = 0.0

        for employee in employees:
            employee_cost = self.get_employee_salary(employee, functions)
            total_cost += employee_cost
        return total_cost
    

    def calculate_proportional_salary(
        self,
        employee: Employee,
        functions: list[Funcao],
        monthly_input: EmployeeMonthlyInput
    ) -> float:
        """
        Orquestra o cálculo do salário proporcional, buscando os dados
        necessários e delegando o cálculo matemático.
        """
        base_salary = self.get_employee_salary(employee, functions)

        if base_salary is None:
            return 0.0

        non_worked_days = monthly_input.vacation_days

        total_days_in_month = 30 #temporário

        proportional_salary = calculate_proportional_salary(
            base_salary=base_salary,
            total_days_in_month=total_days_in_month,
            non_worked_days=non_worked_days
        )

        return proportional_salary
    


    def calculate_full_cost_breakdown(
        self,
        employee: Employee,
        functions: list[Funcao],
        global_config: GlobalConfig,
        monthly_input: EmployeeMonthlyInput
    ) -> dict:
        """
        Gera uma ficha de cálculo completa, incluindo múltiplos proventos e o total.
        """
        # Passo 1: Iniciar um dicionário para guardar os resultados numéricos
        results = {}

        # Passo 2: Chamar cada método de cálculo e guardar o resultado com a chave correta
        results["SALARIO_BASE"] = self.get_employee_salary(employee, functions)

        results["EV_DIAS_TRABALHADOS"] = self.calculate_proportional_salary(
            employee, functions, monthly_input
        )

        results["EV_ADIC_INSALUBRIDADE"] = self.calculate_insalubrity_bonus(
            monthly_input, global_config
        )

        # Adicione aqui futuras chamadas para outras regras (periculosidade, etc.)
        # Ex: results["EV_ADIC_PERICULOSIDADE"] = self.calculate_periculosity_bonus(...)

        
        # O teste espera uma chave 'TOTAL_PROVENTOS'
        results["TOTAL_PROVENTOS"] = (
            results["EV_DIAS_TRABALHADOS"] + 
            results["EV_ADIC_INSALUBRIDADE"]
            # Some aqui outros proventos que você adicionar
        )

        
        return results