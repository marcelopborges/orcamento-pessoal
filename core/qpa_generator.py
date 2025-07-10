# core/qpa_generator.py

import csv
from collections import defaultdict
from typing import List, Dict, Any
from core.entities import Employee # Importa o modelo Employee (supondo que está em core/entities.py)

class QPAGenerator:
    """
    Classe responsável por gerar resumos do Quadro de Pessoal Autorizado (QPA).
    Agrupa funcionários por empresa, equipe e função, e pode exportar para CSV.
    """
    def generate_qpa_summary(self, employees: List[Employee]) -> List[Dict[str, Any]]:
        """
        Gera um resumo QPA a partir de uma lista de objetos Employee,
        agrupando por empresa, equipe e função.
        """
        qpa_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for emp in employees:
            # Atenção: Aqui usamos emp.empresa, emp.equipe, emp.funcao.
            # Certifique-se de que seu objeto Employee (core/entities.py)
            # tenha esses atributos preenchidos.
            # No nosso main.py, esses campos são adicionados ao Employee ao carregar do JSON.
            # certifique-se de que são minúsculas se você converte as chaves do JSON para minúsculas.
            qpa_summary[emp.empresa][emp.equipe][emp.funcao] += 1
        
        output_data = []
        for empresa, equipes in qpa_summary.items():
            for equipe, funcoes in equipes.items():
                for funcao, quantidade in funcoes.items():
                    output_data.append({
                        "empresa": empresa,
                        "equipe": equipe,
                        "funcao": funcao,
                        "quantidade": quantidade
                    })
        return output_data

    def export_qpa_to_csv(self, qpa_data: List[Dict[str, Any]], file_path: str):
        """Exporta os dados QPA resumidos para um arquivo CSV."""
        if not qpa_data:
            print(f"Aviso: Nenhum dado QPA para exportar para '{file_path}'. Arquivo não será criado.")
            return

        # Cabeçalhos do CSV
        fieldnames = ["empresa", "equipe", "funcao", "quantidade"]
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader() # Escreve os cabeçalhos
                writer.writerows(qpa_data) # Escreve as linhas de dados
            print(f"QPA exportado com sucesso para '{file_path}'.")
        except IOError as e:
            print(f"Erro ao exportar QPA para CSV em '{file_path}': {e}.")