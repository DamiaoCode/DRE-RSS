import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Dict, List, Optional
import os

def extract_field_from_details(details_text: str, field_name: str) -> Optional[str]:
    """
    Extrai um campo específico do texto de detalhes usando regex
    """
    patterns = {
        'entidade_adjudicante': r'Designação da entidade adjudicante:\s*(.+?)(?:\n|$)',
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
    
    if field_name not in patterns:
        return None
    
    pattern = patterns[field_name]
    match = re.search(pattern, details_text, re.MULTILINE | re.DOTALL)
    
    if match:
        value = match.group(1).strip()
        # Limpar quebras de linha e espaços extras
        value = re.sub(r'\s+', ' ', value)
        # Remover caracteres especiais HTML
        value = value.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return value
    
    return None

def parse_procedimento(proc: Dict) -> Dict:
    """
    Processa um procedimento e extrai as informações específicas
    """
    # Informações básicas
    numero = proc.get('numero_procedimento', 'N/A')
    entidade = proc.get('entidade', 'N/A')
    link = proc.get('link', '')
    
    # Extrair informações dos detalhes
    detalhes_text = proc.get('detalhes_completos', '')
    
    # Se não há detalhes_completos, tentar usar os campos individuais
    if not detalhes_text:
        return {
            'numero_procedimento': numero,
            'entidade': entidade,
            'link': link,
            'nipc': proc.get('nipc', 'N/A'),
            'distrito': proc.get('distrito', 'N/A'),
            'concelho': proc.get('concelho', 'N/A'),
            'freguesia': proc.get('freguesia', 'N/A'),
            'site': proc.get('site', 'N/A'),
            'email': proc.get('email', 'N/A'),
            'designacao_contrato': proc.get('designacao_contrato', 'N/A'),
            'descricao': proc.get('descricao', 'N/A'),
            'preco_base': proc.get('preco_base', 'N/A'),
            'prazo_execucao': proc.get('prazo_execucao', 'N/A'),
            'prazo_apresentacao_propostas': proc.get('prazo_apresentacao_propostas', 'N/A'),
            'fundos_eu': proc.get('fundos_eu', 'N/A'),
            'plataforma_eletronica': proc.get('plataforma_eletronica', 'N/A'),
            'url_procedimento': proc.get('url_procedimento', 'N/A'),
            'autor_nome': proc.get('autor_nome', 'N/A'),
            'autor_cargo': proc.get('autor_cargo', 'N/A')
        }
    
    # Extrair informações específicas do texto de detalhes
    extracted_info = {}
    fields = [
        'entidade_adjudicante', 'nipc', 'distrito', 'concelho', 'freguesia',
        'site', 'email', 'designacao_contrato', 'descricao', 'preco_base',
        'prazo_execucao', 'prazo_apresentacao_propostas', 'fundos_eu', 'plataforma_eletronica', 'url_procedimento',
        'autor_nome', 'autor_cargo'
    ]
    
    for field in fields:
        value = extract_field_from_details(detalhes_text, field)
        extracted_info[field] = value if value else 'N/A'
    
    return {
        'numero_procedimento': numero,
        'entidade': entidade,
        'link': link,
        **extracted_info
    }

def create_rss_feed(procedimentos: List[Dict]) -> str:
    """
    Cria um feed RSS a partir dos procedimentos processados
    """
    # Criar elemento raiz do RSS
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    # Criar canal
    channel = ET.SubElement(rss, 'channel')
    
    # Informações do canal
    title = ET.SubElement(channel, 'title')
    title.text = 'Feed RSS - Procedimentos DRE'
    
    description = ET.SubElement(channel, 'description')
    description.text = 'Feed RSS com procedimentos do Diário da República - Série II - Parte L'
    
    link = ET.SubElement(channel, 'link')
    link.text = 'https://joaodamiao.github.io/RSS-DRE/'
    
    # Link atom para auto-descoberta
    atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', 'https://joaodamiao.github.io/RSS-DRE/feed_rss_procedimentos.xml')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    language = ET.SubElement(channel, 'language')
    language.text = 'pt-PT'
    
    pub_date = ET.SubElement(channel, 'lastBuildDate')
    pub_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # Adicionar cada procedimento como item
    for i, proc in enumerate(procedimentos):
        item = ET.SubElement(channel, 'item')
        
        # Título do item
        item_title = ET.SubElement(item, 'title')
        item_title.text = f"Procedimento {i+1}: {proc.get('designacao_contrato', proc.get('entidade', 'N/A'))}"
        
        # Link do item
        item_link = ET.SubElement(item, 'link')
        item_link.text = proc.get('link', '')
        
        # GUID
        guid = ET.SubElement(item, 'guid')
        guid.text = proc.get('link', f"proc_{proc.get('numero_procedimento', i)}")
        guid.set('isPermaLink', 'true')
        
        # Data de publicação (usar data atual)
        pub_date_item = ET.SubElement(item, 'pubDate')
        pub_date_item.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Descrição detalhada - apenas as informações específicas pedidas
        description_text = f"""
        <h3>Informações do Procedimento</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr><td><strong>Entidade Adjudicante:</strong></td><td>{proc.get('entidade_adjudicante', proc.get('entidade', 'N/A'))}</td></tr>
            <tr><td><strong>NIPC:</strong></td><td>{proc.get('nipc', 'N/A')}</td></tr>
            <tr><td><strong>Distrito:</strong></td><td>{proc.get('distrito', 'N/A')}</td></tr>
            <tr><td><strong>Concelho:</strong></td><td>{proc.get('concelho', 'N/A')}</td></tr>
            <tr><td><strong>Freguesia:</strong></td><td>{proc.get('freguesia', 'N/A')}</td></tr>
            <tr><td><strong>Site:</strong></td><td><a href="{proc.get('site', '')}">{proc.get('site', 'N/A')}</a></td></tr>
            <tr><td><strong>E-mail:</strong></td><td><a href="mailto:{proc.get('email', '')}">{proc.get('email', 'N/A')}</a></td></tr>
            <tr><td><strong>Designação do contrato:</strong></td><td>{proc.get('designacao_contrato', 'N/A')}</td></tr>
            <tr><td><strong>Descrição:</strong></td><td>{proc.get('descricao', 'N/A')}</td></tr>
            <tr><td><strong>Preço base s/IVA:</strong></td><td>{proc.get('preco_base', 'N/A')}</td></tr>
            <tr><td><strong>Prazo de execução:</strong></td><td>{proc.get('prazo_execucao', 'N/A')}</td></tr>
            <tr><td><strong>Prazo para apresentação das propostas:</strong></td><td>{proc.get('prazo_apresentacao_propostas', 'N/A')}</td></tr>
            <tr><td><strong>Tem fundos EU:</strong></td><td>{proc.get('fundos_eu', 'N/A')}</td></tr>
            <tr><td><strong>Plataforma eletrónica:</strong></td><td>{proc.get('plataforma_eletronica', 'N/A')}</td></tr>
            <tr><td><strong>URL procedimento:</strong></td><td><a href="{proc.get('url_procedimento', '')}">{proc.get('url_procedimento', 'N/A')}</a></td></tr>
            <tr><td><strong>Autor do anúncio - Nome:</strong></td><td>{proc.get('autor_nome', 'N/A')}</td></tr>
            <tr><td><strong>Autor do anúncio - Cargo:</strong></td><td>{proc.get('autor_cargo', 'N/A')}</td></tr>
        </table>
        """
        
        item_description = ET.SubElement(item, 'description')
        item_description.text = description_text
    
    # Converter para string XML formatada
    rough_string = ET.tostring(rss, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main():
    """
    Função principal
    """
    # Carregar dados do JSON
    json_file = '../RSS/procedimentos_completos.json'
    
    if not os.path.exists(json_file):
        print(f"❌ Arquivo {json_file} não encontrado!")
        print("Execute primeiro o script rss_dre_extractor.py")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar {json_file}: {e}")
        return
    
    print(f"Carregados {len(dados)} procedimentos do JSON")
    
    # Processar cada procedimento
    procedimentos_processados = []
    for i, proc in enumerate(dados):
        print(f"Processando procedimento {i+1}/{len(dados)}...")
        proc_processado = parse_procedimento(proc)
        procedimentos_processados.append(proc_processado)
        
        # Mostrar exemplo do primeiro procedimento
        if i == 0:
            print(f"  Exemplo - Entidade: {proc_processado.get('entidade', 'N/A')}")
            print(f"  Exemplo - NIPC: {proc_processado.get('nipc', 'N/A')}")
            print(f"  Exemplo - Preço: {proc_processado.get('preco_base', 'N/A')}")
    
    # Criar feed RSS
    print("\nCriando feed RSS...")
    rss_content = create_rss_feed(procedimentos_processados)
    
    # Salvar feed RSS
    output_file = '../RSS/feed_rss_procedimentos.xml'
    try:
        # Garantir que o diretório existe
        os.makedirs('../RSS', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        
        print(f"Feed RSS criado com sucesso: {output_file}")
        print(f"Total de procedimentos processados: {len(procedimentos_processados)}")
        
        # Estatísticas
        print("\nEstatísticas:")
        print(f"- Procedimentos com entidade: {len([p for p in procedimentos_processados if p.get('entidade') != 'N/A'])}")
        print(f"- Procedimentos com NIPC: {len([p for p in procedimentos_processados if p.get('nipc') != 'N/A'])}")
        print(f"- Procedimentos com preço: {len([p for p in procedimentos_processados if p.get('preco_base') != 'N/A'])}")
        print(f"- Procedimentos com fundos EU: {len([p for p in procedimentos_processados if p.get('fundos_eu') and p.get('fundos_eu') != 'N/A'])}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar feed RSS: {e}")

if __name__ == "__main__":
    main() 