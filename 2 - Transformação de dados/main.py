import os
import pandas as pd
import tabula
import zipfile

PDF_PATH = "pdf/Anexo I.pdf"
CVS_FILENAME = "Rol_de_Procedimentos.csv"
ZIP_FILENAME = "Teste_gabriel_brito.zip"

def extrair_tabelas_do_pdf():
    tabelas = tabula.read_pdf(
        PDF_PATH,
        pages='all',
        multiple_tables=True,
        lattice=True,
        pandas_options={'header': None}
    )
    
    conjunto_tabelas = []
    
    for tabela in tabelas:
        if tabela.shape[1] >= 10:
            index_header = None
    
            for index, linha in tabela.iterrows():
                if 'PROCEDIMENTO' in str(linha.values):
                    index_header = index
                    break
    
            if index_header is not None:
                headers = tabela.iloc[index_header].tolist()
                dados = tabela.iloc[index_header + 1:]
    
            else:
                headers = ['PROCEDIMENTO', 'RN', 'VIGÊNCIA', 'OD', 'AMB', 'HCO', 'HSO', 'REF', 'PAC', 'OUT', 'SUBGRUPO', 'GRUPO', 'CAPÍTULO']
                dados = tabela
            dados = dados.reset_index(drop=True)

            if len(headers) == dados.shape[1]:
                dados.columns = headers
                conjunto_tabelas.append(dados)
    
    if conjunto_tabelas:
        dados_combinados = pd.concat(conjunto_tabelas, ignore_index=True)
        dados_combinados = dados_combinados.dropna(how='all')
        dados_combinados = dados_combinados[dados_combinados['PROCEDIMENTO'].notna()]
        return dados_combinados
    
    return pd.DataFrame()

def alterar_silgas(df):
    od_map = {
        'OD': 'Seg. Odontológica',
    }
    
    amb_map = {
        'AMB': 'Seg. Ambulatorial'
    }
    if 'OD' in df.columns:
        df['OD'] = df['OD'].map(lambda x: od_map.get(x, x))

    if 'AMB' in df.columns:
        df['AMB'] = df['AMB'].map(lambda x: amb_map.get(x, x))
    
    return df

def main():
    print("Extraindo tabelas do PDF...")
    dados = extrair_tabelas_do_pdf()
    
    if dados.empty:
        print("Não foi possível extrair dados do PDF.")
        return
    
    print("Substituindo abreviações...")
    dados = alterar_silgas(dados)    
    print(f"Salvando dados em {CVS_FILENAME}...")
    dados.to_csv(CVS_FILENAME, index=False, encoding='utf-8-sig', sep=";")
    
    print(f"Compactando em {ZIP_FILENAME}...")
    with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(CVS_FILENAME)
    
    print(f"Processo concluído! O arquivo {ZIP_FILENAME} foi criado com sucesso.")
    
    os.remove(CVS_FILENAME)
    print(f"Arquivo temporário {CVS_FILENAME} removido.")

if __name__ == "__main__":
    main()