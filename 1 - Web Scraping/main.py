import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile

#Contantes
URL_SCRAPING = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
PASTA_DESTINO = "pdfs"
ZIP_FILE = "compactado.zip"

#Funções auxiliares.
def acessar_pagina(url):
    resposta = requests.get(url)
    print("INFO: Iniciando scraping.")
    if resposta.status_code != 200:
        print(f"Erro ao acessar a página: {resposta.status_code}")
        exit()
    return resposta.text

def extrair_url_pdf(conteudo_html):
    arquivos_download = {}
    print("INFO: Fazendo a varredura em busca dos arquivos")
    for link in conteudo_html.find_all("a", href=True):
        url = link['href']
        texto_link = link.get_text(strip=True)

        if re.search(r"Anexo\s*I", texto_link, re.IGNORECASE) and url.endswith(".pdf"):
            arquivos_download[texto_link] = url

    if len(arquivos_download) != 2:
        print("Não foi possível encontrar o conteúdo solicitado.")
        exit()

    return arquivos_download

def criar_pasta():
    if not os.path.exists(PASTA_DESTINO):
        print(f"Pasta inexistente, criando a pasta: {PASTA_DESTINO}")
        os.makedirs(PASTA_DESTINO)
        print("Prosseguindo com o download.")
    else:
        print("Pasta já existe, prosseguindo com o download.")    

def baixar_arquivo(arquivos_download):
    criar_pasta()
    
    for chave, valor in arquivos_download.items():
        print(f"INFO: Iniciando download de {chave}")
        resposta = requests.get(valor, stream=True)
        if resposta.status_code == 200:
            caminho_arquivo = os.path.join(PASTA_DESTINO, chave + "pdf")
            with open(caminho_arquivo, "wb") as f:
                for chunk in resposta.iter_content(4096):
                    f.write(chunk)
            print(f"Download concluído: {caminho_arquivo}")
        else:
            print(f"Erro ao baixar {chave}: {resposta.status_code}")
            exit()
    comprimir_pasta()

def comprimir_pasta():
    with zipfile.ZipFile(ZIP_FILE, "w") as zipf:
        for arquivo in os.listdir(PASTA_DESTINO):
            caminho_arquivo = os.path.join(PASTA_DESTINO, arquivo)

            zipf.write(caminho_arquivo, os.path.basename(caminho_arquivo))
            print(f"Arquivo {arquivo} adicionado ao ZIP.")    

def main():
    conteudo_html = acessar_pagina(URL_SCRAPING)
    
    soup = BeautifulSoup(conteudo_html, "html.parser")
    
    arquivos_download = extrair_url_pdf(soup)            
    baixar_arquivo(arquivos_download)
if __name__ == "__main__":
    main()
