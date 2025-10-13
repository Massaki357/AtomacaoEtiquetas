import pandas as pd
import random
import os
from datetime import datetime

class ExcelService:
    def random_number(self):
        return random.randint(1, 1000)

    def comparar_tabelas(self, arquivo1, arquivo2):
        # Carregar os arquivos Excel
        name_file = arquivo1.filename.split(".")[0]
        df1 = pd.read_excel(arquivo1)
        df2 = pd.read_excel(arquivo2)

        df1['Nome'] = df1['Nome'].fillna('indefinido')
        df2['Nome'] = df2['Nome'].fillna('indefinido')

        # Comparar as tabelas
        df1['Código'] = df1['Código'].fillna(self.random_number())
        df1['Valor'] = df1['Valor'].fillna(0)
        df1 = df1.loc[df1.groupby('Código')['Valor'].idxmax()]

        df2['Código'] = df2['Código'].fillna(self.random_number())
        df2['Valor'] = df2['Valor'].fillna(0)
        df2 = df2.loc[df2.groupby('Código')['Valor'].idxmax()]

        novos_valores = df2.set_index('Código')['Valor'].to_dict()

        tabela_atualizada = df1.copy()

        tabela_atualizada['Valor'] = tabela_atualizada.apply(
            lambda row: novos_valores.get(row['Código'], row['Valor']),
            axis=1
        )

        comparacaoDf = pd.merge(df1, df2, on="Código", suffixes=('_antigo', '_novo'))
        

        apenasDiferencas = comparacaoDf[comparacaoDf['Valor_antigo'] != comparacaoDf['Valor_novo']].copy()
        apenasDiferencas['Barato'] = apenasDiferencas.apply(
            lambda row: 'x' if row['Valor_novo'] < row['Valor_antigo'] else '', axis=1
        )
        apenasDiferencas = apenasDiferencas[['Nome_antigo','Código', 'Valor_antigo', 'Valor_novo', 'Barato']]
        # Criar pasta com timestamp para salvar os arquivos
        base_dir = os.getcwd()
        excel_dir = os.path.join(base_dir, 'excel')
        data_dir = datetime.now().strftime("%d-%m-%y")
        save_dir = os.path.join(excel_dir, data_dir)
        os.makedirs(save_dir, exist_ok=True)

        #Salvar Arquivos
        tabela_atualizada.columns = [
            "" if str(col).startswith("Unnamed") else col for col in tabela_atualizada.columns
        ]
        tabela_completa_path = os.path.join(save_dir, 'COMPLETO_'+name_file+'.xlsx')
        diferencas_path = os.path.join(save_dir, f"DIFERANÇAS_{name_file}.xlsx")
        tabela_atualizada.to_excel(tabela_completa_path, index=False)
        apenasDiferencas[['Nome_antigo','Código', 'Valor_antigo', 'Valor_novo', 'Barato']].to_excel(diferencas_path, index=False)

        return apenasDiferencas[['Nome_antigo','Código', 'Valor_antigo', 'Valor_novo', 'Barato']]
    
    

    def two_excel(self ,file1, file2, output_path, code):
        # Lendo os arquivos Excel
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        merged_df = pd.merge(df1, df2, on='Código', how='left')

        # Extrai o código base (antes do '-')
        if merged_df['Código'].astype(str).str.contains('-').any():
            merged_df['CodigoBase'] = merged_df['Código'].astype(str).str.split('-').str[0]
        else:
            merged_df['CodigoBase'] = merged_df['Código']

        # Usa o nome do primeiro excel (df1), que após o merge vira 'Nome_x'
        if 'Nome_x' in merged_df.columns:
            merged_df['Nome'] = merged_df['Nome_x']
        elif 'Nome' in merged_df.columns:
            merged_df['Nome'] = merged_df['Nome']
        else:
            merged_df['Nome'] = ''

        if code:
            merged_df['Nome'] = merged_df['Nome'].astype(str) + ' - ' + merged_df['CodigoBase'].astype(str).str.split('.').str[0]

        # Agrupa pelo código base, soma quantidade, pega o maior valor e o primeiro nome
        result_df = merged_df.groupby('CodigoBase').agg({
            'Nome': 'first',
            'Quantidade': 'sum',
            'Valor': 'max',
        }).reset_index()

        # Remove linhas onde quantidade é igual a 0
        result_df = result_df[result_df['Quantidade'] != 0]

        # Cria o diretório de saída se não existir
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        dateNow = datetime.now().strftime("%d-%m-%y")
        output_file = os.path.join(output_path, 'pedido-e-venda-'+dateNow+'.xlsx')
        result_df.to_excel(output_file, index=False)

        print('Arquivos mesclados com sucesso e salvos em:', output_file)

        return result_df