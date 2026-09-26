import requests
import xml.etree.ElementTree as ET
import json
import re
import time
import os
from typing import List, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from rss_storage import (
    daily_data_path,
    existing_complete_by_link,
    load_json_list,
    merge_procedimentos_by_link,
)

def fetch_rss_feed(url: str) -> str:
    """
    Faz fetch do conteúdo XML do RSS feed
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erro ao fazer fetch do RSS feed: {e}")
        return None

def setup_driver():
    """
    Configura e retorna o driver do Chrome usando webdriver-manager para baixar a versão correta
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
 
    
    # Usar webdriver-manager para baixar a versão correta do Chrome WebDriver
    chrome_driver_path = ChromeDriverManager().install()
    print(f"Usando Chrome WebDriver: {chrome_driver_path}")
    
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fetch_procedure_details(url: str) -> Dict[str, str]:
    """
    Extrai detalhes de um procedimento específico a partir da URL
    """
    driver = None
    try:
        driver = setup_driver()
        print(f"Acessando: {url}")
        
        driver.get(url)
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Aguardar um pouco mais para garantir que o JavaScript carregou
        time.sleep(5)
        
        # Obter o HTML renderizado
        page_source = driver.page_source
        
        # Salvar HTML para debug
        with open('debug_page_rendered.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        # Usar BeautifulSoup para parsear o HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Procurar pelo texto específico
        possible_texts = [
            "1 - IDENTIFICAÇÃO E CONTACTOS DA ENTIDADE ADJUDICANTE",
            "IDENTIFICAÇÃO E CONTACTOS DA ENTIDADE ADJUDICANTE",
            "IDENTIFICAÇÃO"
        ]
        
        target_element = None
        for text in possible_texts:
            target_element = soup.find(string=re.compile(text, re.IGNORECASE))
            if target_element:
                break
        
        if target_element:
            # Encontrar o div pai que contém as informações
            parent_div = target_element.find_parent('div')
            if parent_div:
                # Extrair todo o texto do div pai
                details_text = parent_div.get_text(separator='\n', strip=True)
                
                # Extrair informações específicas usando regex
                extracted_info = {}
                
                # Padrões para extrair informações específicas
                patterns = {
                    'entidade': r'Designação da entidade adjudicante:\s*(.+?)(?:\n|$)',
                    'nipc': r'NIPC:\s*(\d+)',
                    'distrito': r'Distrito:\s*(.+?)(?:\n|$)',
                    'concelho': r'Concelho:\s*(.+?)(?:\n|$)',
                    'freguesia': r'Freguesia:\s*(.+?)(?:\n|$)',
                    'site': r'Endereço da Entidade \(URL\):\s*(.+?)(?:\n|$)',
                    'email': r'Endereço Eletrónico:\s*(.+?)(?:\n|$)',
                    'designacao_contrato': r'Designação do contrato:\s*(.+?)(?:\n|$)',
                    'descricao': r'Descrição:\s*(.+?)(?:\n|$)',
                    'preco_base': r'Preço base s/IVA:\s*(.+?)(?:\n|$)',
                    'prazo_execucao': r'Prazo de execução do contrato:\s*(.+?)(?:\n|$)',
                    'prazo_apresentacao_propostas': r'Prazo para apresentação das propostas:\s*(.+?)(?:\n|$)',
                    'fundos_eu': r'Têm fundos EU\?\s*(.+?)(?:\n|$)',
                    'plataforma_eletronica': r'Plataforma eletrónica utilizada pela entidade adjudicante:\s*(.+?)(?:\n|$)',
                    'url_procedimento': r'URL para Apresentação:\s*(.+?)(?:\n|$)',
                    'autor_nome': r'28 - IDENTIFICAÇÃO DO\(S\) AUTOR\(ES\) DE ANÚNCIO\nNome:\s*(.+?)(?:\n|$)',
                    'autor_cargo': r'Cargo:\s*(.+?)(?:\n|$)'
                }
                
                for field, pattern in patterns.items():
                    match = re.search(pattern, details_text, re.MULTILINE | re.DOTALL)
                    if match:
                        value = match.group(1).strip()
                        value = re.sub(r'\s+', ' ', value)
                        extracted_info[field] = value
                    else:
                        extracted_info[field] = None
                
                return {
                    'detalhes_completos': details_text,
                    **extracted_info
                }
        
        print("Não foi possível encontrar as informações específicas")
        return None
        
    except Exception as e:
        print(f"Erro ao extrair detalhes: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def extract_procedure_info(title: str, description: str) -> Dict[str, str]:
    """
    Extrai número do procedimento e entidade do título/descrição
    """
    # Padrão para extrair número do procedimento
    numero_match = re.search(r'n\.º\s*(\d+)/\d+', title)
    numero_procedimento = numero_match.group(1) if numero_match else "N/A"
    
    # Extrair entidade (geralmente está no título após o número)
    entidade = title.strip()
    
    return {
        "numero_procedimento": numero_procedimento,
        "entidade": entidade
    }

def parse_rss_to_json(xml_content: str) -> List[Dict[str, str]]:
    """
    Faz parse do XML do RSS feed e extrai informações dos procedimentos
    """
    try:
        root = ET.fromstring(xml_content)
        
        # Namespace para RSS
        ns = {'rss': 'http://purl.org/rss/1.0/'}
        
        extracted_data = []
        
        # Encontrar todos os items
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            description_elem = item.find('description')
            link_elem = item.find('link')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ""
                description = description_elem.text if description_elem is not None else ""
                link = link_elem.text or ""
                
                # Limpar CDATA se presente
                title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                description = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', description)
                
                # Extrair informações do procedimento
                procedure_info = extract_procedure_info(title, description)
                
                item_data = {
                    "numero_procedimento": procedure_info["numero_procedimento"],
                    "entidade": procedure_info["entidade"],
                    "link": link
                }
                
                extracted_data.append(item_data)
        
        return extracted_data
        
    except ET.ParseError as e:
        print(f"Erro ao fazer parse do XML: {e}")
        return []

def save_to_json(data: List[Dict[str, str]], filename: str = "procedimentos_dre.json"):
    """
    Salva os dados extraídos em formato JSON
    """
    try:
        # Garantir que o diretório RSS existe
        os.makedirs('../RSS', exist_ok=True)
        
        filepath = os.path.join('../RSS', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos com sucesso em {filepath}")
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")

def save_to_json_with_date(data: List[Dict[str, str]]):
    """
    Salva os dados extraídos em formato JSON na pasta data/ com nome baseado
    na data atual em Europe/Lisbon (DD-MM-YYYY).
    """
    try:
        os.makedirs('../data', exist_ok=True)
        filepath = daily_data_path('../data')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos com sucesso em {filepath}")
        return filepath
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON com data: {e}")
        return None

def main():
    """
    Função principal que executa todo o processo
    """
    rss_url = "https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml"
    
    print("Fazendo fetch do RSS feed do Diário da República...")
    xml_content = fetch_rss_feed(rss_url)
    
    if xml_content is None:
        print("Não foi possível obter o conteúdo do RSS feed")
        return
    
    print("Extraindo informações dos procedimentos...")
    extracted_data = parse_rss_to_json(xml_content)
    
    if not extracted_data:
        print("Nenhum dado foi extraído")
        return
    
    print(f"Extraídos {len(extracted_data)} procedimentos")

    # Reutilizar o JSON do dia (Europe/Lisbon) para não perder publicações
    # já recolhidas em execuções anteriores — o RSS do DRE só tem o próprio dia.
    existing_today = load_json_list(daily_data_path('../data'))
    already_complete = existing_complete_by_link(existing_today)
    print(
        f"📂 Procedimentos já guardados hoje: {len(existing_today)} "
        f"({len(already_complete)} com detalhes)"
    )
    
    # Salvar dados básicos em JSON
    save_to_json(extracted_data, "procedimentos_basicos.json")
    
    # Extrair detalhes apenas dos procedimentos ainda não recolhidos
    print("\nExtraindo detalhes de cada procedimento...")
    procedimentos_completos = []
    reused = 0
    scraped = 0
    
    for i, item in enumerate(extracted_data):
        print(f"\nProcessando procedimento {i+1}/{len(extracted_data)}: {item['numero_procedimento']}")
        link = (item.get('link') or '').strip()

        if link in already_complete:
            procedimentos_completos.append(already_complete[link])
            reused += 1
            print("  ↷ Já recolhido hoje; a reutilizar detalhes")
            continue

        details = fetch_procedure_details(item['link'])
        scraped += 1
        
        if details:
            item_completo = {**item, **details}
            procedimentos_completos.append(item_completo)
            print("  ✓ Detalhes extraídos com sucesso")
        else:
            procedimentos_completos.append(item)
            print("  ✗ Não foi possível extrair detalhes")

    procedimentos_completos = merge_procedimentos_by_link(
        existing_today, procedimentos_completos
    )
    print(
        f"\n📊 Recolha incremental: {reused} reutilizados, "
        f"{scraped} novos, {len(procedimentos_completos)} no total do dia"
    )
    
    # Salvar dados completos em JSON
    save_to_json(procedimentos_completos, "procedimentos_completos.json")
    
    # Salvar dados completos em JSON com data na pasta data/
    print("\n📅 Salvando dados com data atual...")
    data_file_path = save_to_json_with_date(procedimentos_completos)
    
    # Atualizar arquivo ativos.json
    print("\n🔄 Atualizando arquivo ativos.json...")
    try:
        from gerir_ativos import update_ativos_from_date_file, merge_with_existing_ativos, save_ativos
        
        if data_file_path:
            # Obter procedimentos ativos do arquivo de data
            procedimentos_ativos = update_ativos_from_date_file(data_file_path)
            
            # Combinar com procedimentos ativos existentes
            ativos_finais = merge_with_existing_ativos(procedimentos_ativos)
            
            # Salvar arquivo ativos.json
            ativos_file_path = save_ativos(ativos_finais)
            
            if ativos_file_path:
                print(f"✅ Arquivo ativos.json atualizado com sucesso!")
                print(f"📊 Total de procedimentos ativos: {len(ativos_finais)}")
            else:
                print("❌ Erro ao salvar arquivo ativos.json")
        else:
            print("❌ Não foi possível obter caminho do arquivo de data")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar ativos.json: {e}")
    
    # Gerar automaticamente o feed RSS
    print("\n🔄 Gerando feed RSS automaticamente...")
    try:
        import subprocess
        import sys
        
        print("Executando conversor JSON para RSS...")
        result = subprocess.run([sys.executable, "json_to_rss_converter.py"], 
                              capture_output=True, text=True, check=True)
        
        print("✅ Feed RSS gerado com sucesso!")
        print("📄 Arquivo criado: ../RSS/feed_rss_procedimentos.xml")
        
        # Mostrar estatísticas do feed RSS
        if "Total de procedimentos processados:" in result.stdout:
            print("\n📊 Estatísticas do Feed RSS:")
            for line in result.stdout.split('\n'):
                if "Estatísticas:" in line or "procedimentos" in line:
                    print(f"  {line}")
                    
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar feed RSS: {e}")
        print(f"Erro: {e.stderr}")
    except Exception as e:
        print(f"❌ Erro inesperado ao gerar feed RSS: {e}")
    
    print(f"\n🎉 Processo completo finalizado!")
    print(f"Procedimentos processados: {len(procedimentos_completos)}")
    print(f"📁 Arquivos gerados:")
    print(f"  - ../RSS/procedimentos_basicos.json (dados do RSS)")
    print(f"  - ../RSS/procedimentos_completos.json (dados + detalhes)")
    if data_file_path:
        print(f"  - {data_file_path} (dados completos com data)")
    print(f"  - ../data/ativos.json (procedimentos ativos)")
    print(f"  - ../RSS/feed_rss_procedimentos.xml (feed RSS completo)")

if __name__ == "__main__":
    main() 