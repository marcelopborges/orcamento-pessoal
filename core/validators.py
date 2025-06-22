
import re
from datetime import datetime
from typing import Dict, Any, Optional, Union


class DataValidationError(Exception):
    """ 
        Exceção personalizada para erros de validação de dados.
        Esta exceção é levantada quando os dados fornecidos não atendem aos critérios de validação
        definidos na classe EmployeeDataValidator.
    """
    pass

class EmployeeDataValidator:
    def __init__(self):
        self.required_keys = ["NOME","SITUACAO","CODIGO_FUNCAO","DATA_ADMISSAO","DATA_ADMISSAO","DATA_ADMISSAO_PTS","DATA_NASCIMENTO","SESSAO","JORNADA","CPF","CENTRO_CUSTO"]
        self.validation_rules = {
            "CHAPA": self._validate_CHAPA,
            "NOME": self._validate_string,
            "SITUACAO":self._validate_SITUACAO_format,
            "CODIGO_FUNCAO": self._validate_CODIGO_FUNCAO_format,
            "DATA_ADMISSAO": self._validate_date_format,
            "DATA_ADMISSAO_PTS": self._validate_date_format,
            "DATA_NASCIMENTO": self._validate_date_format,
            "SESSAO": self._validate_SESSAO_format,
            "JORNADA": self._validate_JORNADA_format,
            "CPF": self._validate_CPF_format,
            "CENTRO_CUSTO": self._validate_CENTRO_CUSTO_format
        }

    def _validate_CHAPA(self, value: Any) -> str:
        """
        Valida o campo CHAPA.
        O campo CHAPA deve ser uma string de 5 dígitos numéricos.
        """
        if not isinstance(value, str) or not re.match(r'^\d{5}$', value):
            raise DataValidationError("O campo 'CHAPA' deve ser uma string de 5 dígitos numéricos.")
        return value
    
    def _validate_string(self, value: Any) -> str:
        """
        Valida se o valor é uma string não vazia.
        """
        if not isinstance(value, str) or not value.strip():
            raise DataValidationError("O campo deve ser uma string não vazia.")
        return value.strip()
    
    def _validate_SITUACAO_format(self, value: Any) -> str:
        """
        Valida o campo SITUACAO.
        O campo SITUACAO deve ser uma string de 1 caractere sendo ele (A, F, I, L, P , T) representando a situação do empregado.
        Valores válidos:
        - 'A' para Ativo
        - 'F' para Férias
        - 'I' para Apos. por Incapacidade Permanente
        - 'L' para Licença s/venc
        - 'P' para Af.Previdência
        - 'T' para Af.Ac.Trabalho
        """
        valid_values = {'A', 'F', 'I', 'L', 'P', 'T'}
        if not isinstance(value, str) or len(value) != 1 or value not in valid_values:
            raise DataValidationError("O campo 'SITUACAO' deve ser uma string de 1 caractere com um dos seguintes valores: 'A', 'F', 'I', 'L', 'P', 'T'.")
        return value.strip()
    
    def _validate_CODIGO_FUNCAO_format(self, value: Any) -> str:
        """
        Valida o campo FUNCAO.
        O campo FUNCAO deve ser uma string de 4 dígitos numéricos.
        """
        if not isinstance(value, str) or not re.match(r'^\d{4}$', value):
            raise DataValidationError("O campo 'FUNCAO' deve ser uma string de 4 dígitos numéricos.")
        return value.strip()
    
    def _validate_date_format(self, value: Any) -> datetime:
        """
        Valida se o valor é uma data nos formatos 'YYYY-MM-DD' ou 'DD/MM/YYYY'.
        Retorna um objeto datetime se a validação for bem-sucedida.
        """
        if not isinstance(value, str):
            raise DataValidationError("O campo de data deve ser uma string.")

        # Tenta o primeiro formato
        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d')
        except ValueError:
            # Se falhar, tenta o segundo formato
            try:
                return datetime.strptime(value.strip(), '%d/%m/%Y')
            except ValueError:
                # Se ambos falharem, lança a exceção
                raise DataValidationError("A data deve estar no formato 'YYYY-MM-DD' ou 'DD/MM/YYYY'.")

    
    def _validate_SESSAO_format(self, value: Any) -> str:
        """
        Valida o campo SESSAO.
        O campo SESSAO deve ser uma string no formato 'XX.XX.X.XX.XX.XXXXX'.
        """
        if not isinstance(value, str) or not re.match(r'^\d{2}\.\d{2}\.\d\.\d{2}\.\d{2}\.\d{3}$', value):
            raise DataValidationError("O campo 'SESSAO' deve estar no formato 'XX.XX.X.XX.XX.XXX'.")
        return value.strip()
    
    def _validate_JORNADA_format(self, value: Any) -> str:
        """
        Valida o campo JORNADA.
        O campo JORNADA deve ser uma string de 3 dígitos numéricos.
        valores válidos:
        - '220' para 220 horas mensais
        - '150' para 150 horas mensais
        - '075' para 75 horas mensais
        """
        valid_values = {'220', '150', '75'}
        if not isinstance(value, str) or value not in valid_values:
            raise DataValidationError("O campo 'JORNADA' deve ser uma string com um dos seguintes valores: '220', '150', '075'.")
        return value.strip()
    
    def _validate_CPF_format(self, value: Any) -> str:
        """
        Valida o campo CPF.
        """
        if not isinstance(value, str):
            raise DataValidationError("O CPF deve ser fornecido como uma string.")

        # Remove espaços em branco do início e do fim
        value = value.strip()

        # Verifica se o CPF está vazio após a limpeza
        if not value:
            raise DataValidationError("O CPF deve conter 11 dígitos.")

        # Valida se contém apenas números, pontos e hífens
        if not re.match(r'^[0-9.\-]+$', value):
            raise DataValidationError("O CPF deve conter apenas números ou os formatos válidos (XXX.XXX.XXX-XX).")

        # Remove qualquer caractere que não seja número
        cpf = re.sub(r'\D', '', value)

        # Verifica se o CPF tem exatamente 11 dígitos
        if len(cpf) != 11:
            raise DataValidationError("O CPF deve conter 11 dígitos.")

        # Ignora CPFs com dígitos repetidos conhecidos (ex.: 000.000.000-00)
        if cpf in [str(i) * 11 for i in range(10)]:
            raise DataValidationError("O CPF fornecido é inválido.")

        # Valida os dígitos verificadores
        if not self._is_valid_cpf(cpf):
            raise DataValidationError("Os dígitos verificadores do CPF são inválidos.")

        return cpf

    # Dentro da classe EmployeeDataValidator

    def _is_valid_cpf(self, cpf: str) -> bool:
        """
        Valida os dígitos verificadores do CPF.
        """
        # Se o cpf não tiver 11 dígitos, é inválido.
        if len(cpf) != 11:
            return False

        # Cálculo do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        primeiro_digito = (soma * 10) % 11
        if primeiro_digito == 10:
            primeiro_digito = 0

        if primeiro_digito != int(cpf[9]):
            return False

        # Cálculo do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        segundo_digito = (soma * 10) % 11
        if segundo_digito == 10:
            segundo_digito = 0

        if segundo_digito != int(cpf[10]):
            return False

        return True
    
    def _validate_CENTRO_CUSTO_format(self, value: Any) -> str:
        """
        Valida o campo CENTRO_CUSTO.
        O campo CENTRO_CUSTO deve ser uma string de 9 dígitos numéricos.
        """
        if not isinstance(value, str) or not re.match(r'^\d{9}$', value):
            raise DataValidationError("O campo 'CENTRO_CUSTO' deve ser uma string de 9 dígitos numéricos.")
        return value.strip()
    
# validators.py -> Correção do método validate()
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida os dados do empregado.
        Verifica se todos os campos obrigatórios estão presentes e se atendem às regras de validação.
        Retorna os dados validados.
        """
        validated_data = {}
        errors = []

        for key in self.required_keys:
            if key not in data:
                errors.append(f"O campo obrigatório '{key}' está ausente.")
        
        if errors:
            raise DataValidationError(", ".join(errors))

        for key, value in data.items():
            if key in self.validation_rules:
                try:
                    validated_data[key] = self.validation_rules[key](value)
                except DataValidationError as e:
                    errors.append(f"Erro no campo '{key}': {e}")
            else:
                 validated_data[key] = value

        if errors:
            raise DataValidationError("Erros de validação encontrados: " + "; ".join(errors))
        return {k.lower(): v for k, v in validated_data.items()}

class FunctionDataValidator:
    """Valida os dados de entrada para a entidade Funcao."""
    def __init__(self):
        self.required_keys = ["CODIGO_FUNCAO", "NOME_FUNCAO", "SALARIO"]
        self.validation_rules = {
            "CODIGO_FUNCAO": self._validate_string_code,
            "NOME_FUNCAO": self._validate_string,
            "SALARIO": self._validate_salary
        }

    def _validate_string_code(self, value: Any) -> str:
        if not isinstance(value, str) or not re.match(r'^\d{4}$', value):
            raise DataValidationError("O campo 'CODIGO_FUNCAO' deve ser uma string de 4 digitos númericos.")
        return value.strip()

    def _validate_string(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise DataValidationError("O campo 'NOME_FUNCAO' deve ser uma string não vazia")
        return value.strip()

    def _validate_salary(self, value: Any) -> float:
        if not isinstance(value, str):
            raise DataValidationError("O campo 'SALARIO' deve ser uma string.")
        try:
            cleaned_value = value.strip()
            if ',' in cleaned_value:
                cleaned_value = cleaned_value.replace('.', '').replace(',', '.')
            return float(cleaned_value)
        except (ValueError, TypeError):
            raise DataValidationError("O campo 'SALARIO' deve ser um número válido.")


    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        validated_data = {}
        errors = []

        for key in self.required_keys:
            if key not in data:
                errors.append(f"O campo obrigatório '{key}' está ausente.")

        if errors:
            raise DataValidationError(", ".join(errors))

        for key, value in data.items():
            if key in self.validation_rules:
                try:
                    validated_data[key] = self.validation_rules[key](value)
                except DataValidationError as e:
                    errors.append(f"Erro no campo '{key}': {e}")
            else:
                validated_data[key] = value

        if errors:
            raise DataValidationError("Erros de validação encontrados: " + "; ".join(errors))
        
        return {k.lower(): v for k, v in validated_data.items()}