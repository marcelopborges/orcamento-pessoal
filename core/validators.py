# core/validators.py

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
        # Mantém required_keys em MAIÚSCULAS, como já está no seu código.
        self.required_keys = ["CHAPA","NOME","SITUACAO","CODIGO_FUNCAO","DATA_ADMISSAO","DATA_ADMISSAO_PTS","DATA_NASCIMENTO","SESSAO","JORNADA","CPF","CENTRO_CUSTO"]
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
        # Adiciona campos de agrupamento e benefícios aos required_keys e validation_rules
        self.required_keys.extend([
            "EMPRESA", "EQUIPE", "FUNCAO",
            "VALOR_VALE_TRANSPORTE_MENSAL", "VALOR_VALE_REFEICAO_MENSAL",
            "PLANO_SAUDE_MENSAL", "OUTROS_BENEFICIOS_MENSAIS" # Nomes em MAIÚSCULAS
        ])
        self.validation_rules.update({
            "EMPRESA": self._validate_string,
            "EQUIPE": self._validate_string,
            "FUNCAO": self._validate_string,
            "VALOR_VALE_TRANSPORTE_MENSAL": self._validate_non_negative_float,
            "VALOR_VALE_REFEICAO_MENSAL": self._validate_non_negative_float,
            "PLANO_SAUDE_MENSAL": self._validate_non_negative_float,
            "OUTROS_BENEFICIOS_MENSAL": self._validate_non_negative_float # Corrigido para corresponder ao JSON de exemplo
        })


    def _validate_CHAPA(self, value: Any) -> str:
        if not isinstance(value, str) or not re.match(r'^\d{5}$', value):
            raise DataValidationError("O campo 'CHAPA' deve ser uma string de 5 dígitos numéricos.")
        return value
    
    def _validate_string(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise DataValidationError("O campo deve ser uma string não vazia.")
        return value.strip()
    
    def _validate_SITUACAO_format(self, value: Any) -> str:
        valid_values = {'A', 'F', 'I', 'L', 'P', 'T'}
        if not isinstance(value, str) or len(value) != 1 or value not in valid_values:
            raise DataValidationError("O campo 'SITUACAO' deve ser uma string de 1 caractere com um dos seguintes valores: 'A', 'F', 'I', 'L', 'P', 'T'.")
        return value.strip()
    
    def _validate_CODIGO_FUNCAO_format(self, value: Any) -> str:
        if not isinstance(value, str) or not re.match(r'^\d{4}$', value):
            raise DataValidationError("O campo 'CODIGO_FUNCAO' deve ser uma string de 4 dígitos numéricos.") # Mensagem corrigida
        return value.strip()
    
    def _validate_date_format(self, value: Any) -> datetime:
        if not isinstance(value, str):
            raise DataValidationError("O campo de data deve ser uma string.")

        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(value.strip(), '%d/%m/%Y')
            except ValueError:
                raise DataValidationError("A data deve estar no formato 'YYYY-MM-DD' ou 'DD/MM/YYYY'.")

    
    def _validate_SESSAO_format(self, value: Any) -> str:
        if not isinstance(value, str) or not re.match(r'^\d{2}\.\d{2}\.\d\.\d{2}\.\d{2}\.\d{3}$', value):
            raise DataValidationError("O campo 'SESSAO' deve estar no formato 'XX.XX.X.XX.XX.XXX'.")
        return value.strip()
    
    def _validate_JORNADA_format(self, value: Any) -> str:
        valid_values = {'220', '150', '75'}
        if not isinstance(value, str) or value not in valid_values:
            raise DataValidationError("O campo 'JORNADA' deve ser uma string com um dos seguintes valores: '220', '150', '075'.")
        return value.strip()
    
    def _validate_CPF_format(self, value: Any) -> str:
        if not isinstance(value, str):
            raise DataValidationError("O CPF deve ser fornecido como uma string.")

        value = value.strip()

        if not value:
            raise DataValidationError("O CPF deve conter 11 dígitos.")

        if not re.match(r'^[0-9.\-]+$', value):
            raise DataValidationError("O CPF deve conter apenas números ou os formatos válidos (XXX.XXX.XXX-XX).")

        cpf = re.sub(r'\D', '', value)

        if len(cpf) != 11:
            raise DataValidationError("O CPF deve conter 11 dígitos.")

        if cpf in [str(i) * 11 for i in range(10)]:
            raise DataValidationError("O CPF fornecido é inválido.")

        if not self._is_valid_cpf(cpf):
            raise DataValidationError("Os dígitos verificadores do CPF são inválidos.")

        return cpf

    def _is_valid_cpf(self, cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        primeiro_digito = (soma * 10) % 11
        if primeiro_digito == 10:
            primeiro_digito = 0

        if primeiro_digito != int(cpf[9]):
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        segundo_digito = (soma * 10) % 11
        if segundo_digito == 10:
            segundo_digito = 0

        if segundo_digito != int(cpf[10]):
            return False

        return True
    
    def _validate_CENTRO_CUSTO_format(self, value: Any) -> str:
        if not isinstance(value, str) or not re.match(r'^\d{9}$', value):
            raise DataValidationError("O campo 'CENTRO_CUSTO' deve ser uma string de 9 dígitos numéricos.")
        return value.strip()

    def _validate_non_negative_float(self, value: Any) -> float:
        try:
            val = float(value)
            if val < 0:
                raise ValueError("Valor não pode ser negativo.")
            return val
        except (ValueError, TypeError) as e:
            raise DataValidationError(f"Valor numérico inválido: '{value}'. Deve ser um número válido e não negativo. Erro: {e}")

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida os dados do empregado.
        Converte as chaves de entrada para MAIÚSCULAS antes da validação interna.
        Retorna os dados validados com chaves em MINÚSCULAS.
        """
        # AQUI É A MUDANÇA CRÍTICA: Normaliza TODAS as chaves de entrada para MAIÚSCULAS
        normalized_data = {k.upper(): v for k, v in data.items()}

        validated_data = {}
        errors = []

        for key in self.required_keys:
            # Agora 'key' (em maiúsculas) é procurado em 'normalized_data' (que tem chaves em maiúsculas)
            if key not in normalized_data:
                errors.append(f"O campo obrigatório '{key}' está ausente.")
        
        if errors:
            raise DataValidationError(", ".join(errors))

        # Percorre normalized_data para aplicar as regras
        for key, value in normalized_data.items():
            if key in self.validation_rules:
                try:
                    validated_data[key] = self.validation_rules[key](value)
                except DataValidationError as e:
                    errors.append(f"Erro no campo '{key}': {e}")
            else:
                 # Se a chave não tem regra de validação, ela é incluída como está
                 validated_data[key] = value

        if errors:
            raise DataValidationError("Erros de validação encontrados: " + "; ".join(errors))
        
        # Converte as chaves de volta para minúsculas para o dicionário de retorno
        return {k.lower(): v for k, v in validated_data.items()}

class FunctionDataValidator:
    """Valida os dados de entrada para a entidade Funcao."""
    def __init__(self):
        # Mantenha required_keys em MAIÚSCULAS
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
        """
        Valida os dados de entrada para a entidade Funcao.
        Converte as chaves de entrada para MAIÚSCULAS antes da validação interna.
        Retorna os dados validados com chaves em MINÚSCULAS.
        """
        # AQUI É A MUDANÇA CRÍTICA: Normaliza TODAS as chaves de entrada para MAIÚSCULAS
        normalized_data = {k.upper(): v for k, v in data.items()}

        validated_data = {}
        errors = []

        for key in self.required_keys:
            # Agora 'key' (em maiúsculas) é procurado em 'normalized_data' (que tem chaves em maiúsculas)
            if key not in normalized_data:
                errors.append(f"O campo obrigatório '{key}' está ausente.")

        if errors:
            raise DataValidationError(", ".join(errors))

        for key, value in normalized_data.items():
            if key in self.validation_rules:
                try:
                    validated_data[key] = self.validation_rules[key](value)
                except DataValidationError as e:
                    errors.append(f"Erro no campo '{key}': {e}")
            else:
                validated_data[key] = value

        if errors:
            raise DataValidationError("Erros de validação encontrados: " + "; ".join(errors))
        
        # Converte as chaves de volta para minúsculas para o dicionário de retorno
        return {k.lower(): v for k, v in validated_data.items()}