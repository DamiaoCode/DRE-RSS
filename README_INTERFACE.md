# 📋 Interface Web - Procedimentos Ativos DRE

## 🎯 Descrição

Interface web moderna para visualizar procedimentos de contratação pública ativos do Diário da República (DRE). A interface apresenta os procedimentos em formato accordion, mostrando apenas aqueles com prazo de apresentação de propostas ainda válido.

## ✨ Funcionalidades

### 📊 **Barra de Estatísticas**

- **Total de Procedimentos**: Número total de procedimentos ativos
- **Procedimentos Ativos**: Procedimentos com prazo válido
- **Última Atualização**: Data/hora da última atualização
- **Botão Atualizar**: Recarregar dados do arquivo `ativos.json`

### 📋 **Lista Accordion**

Cada procedimento é exibido em um card expansível com:

#### **Header (Visível por padrão):**

- **Título**: Descrição ou designação do contrato
- **Entidade**: Nome da entidade adjudicante
- **Plataforma Eletrónica**: Plataforma onde o procedimento está disponível
- **Prazo de Apresentação**: Data e hora limite (em vermelho)
- **Preço Base**: Valor base do contrato (em verde)

#### **Conteúdo Expandido (ao clicar):**

- **Informações da Entidade**: NIPC, localização, site, email
- **Detalhes do Contrato**: Número, prazo de execução, fundos EU
- **Informações Adicionais**: Autor, cargo, links

## 🚀 Como Usar

### **Opção 1: Abrir diretamente no navegador**

```bash
# Navegar para o diretório DRE-RSS
cd DRE-RSS

# Abrir o arquivo index.html
start index.html  # Windows
open index.html   # macOS
xdg-open index.html  # Linux
```

### **Opção 2: Servidor local (recomendado)**

```bash
# Navegar para o diretório DRE-RSS
cd DRE-RSS

# Executar o servidor local
python serve.py
```

O servidor irá:

- Iniciar em `http://localhost:8000`
- Abrir automaticamente o navegador
- Servir todos os arquivos localmente

## 📁 Estrutura de Arquivos

```
DRE-RSS/
├── index.html          # Interface principal
├── serve.py            # Servidor local
├── data/
│   ├── ativos.json     # Procedimentos ativos
│   └── DD-MM-YYYY.json # Dados diários
└── scripts/
    ├── rss_dre_extractor.py  # Extrator principal
    └── gerir_ativos.py       # Gestor de ativos
```

## 🎨 Design

### **Características:**

- **Responsivo**: Adapta-se a diferentes tamanhos de ecrã
- **Moderno**: Design limpo e profissional
- **Acessível**: Navegação por teclado e leitores de ecrã
- **Performance**: Carregamento rápido e eficiente

### **Cores:**

- **Primária**: Azul gradiente (#667eea → #764ba2)
- **Sucesso**: Verde (#27ae60) para preços
- **Aviso**: Vermelho (#e74c3c) para prazos
- **Neutro**: Cinza (#f5f7fa) para fundo

## 🔧 Personalização

### **Modificar Estilos**

Editar a seção `<style>` no arquivo `index.html`:

```css
/* Alterar cores principais */
.header {
  background: linear-gradient(135deg, #sua-cor-1 0%, #sua-cor-2 100%);
}

/* Alterar tamanho do container */
.container {
  max-width: 1400px; /* Aumentar largura máxima */
}
```

### **Adicionar Novos Campos**

Modificar a função `displayProcedimentos()` no JavaScript:

```javascript
// Adicionar novo campo no header
<div class="procedure-new-field">${proc.novo_campo || 'N/A'}</div>

// Adicionar nova seção de detalhes
<div class="detail-group">
    <h4>Nova Seção</h4>
    <div class="detail-item">
        <span class="detail-label">Novo Campo:</span>
        <span class="detail-value">${proc.novo_campo || 'N/A'}</span>
    </div>
</div>
```

## 📱 Compatibilidade

### **Navegadores Suportados:**

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

### **Dispositivos:**

- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (< 768px)

## 🔄 Atualização de Dados

A interface carrega automaticamente os dados do arquivo `data/ativos.json`. Para atualizar:

1. **Executar o extrator**: `python scripts/rss_dre_extractor.py`
2. **Atualizar ativos**: `python scripts/gerir_ativos.py`
3. **Recarregar página**: Clicar no botão "🔄 Atualizar"

## 🐛 Resolução de Problemas

### **Erro "Arquivo não encontrado"**

- Verificar se `data/ativos.json` existe
- Executar `python scripts/gerir_ativos.py` para gerar o arquivo

### **Interface não carrega**

- Verificar se está a usar um servidor web (não abrir diretamente o arquivo)
- Executar `python serve.py` para servidor local

### **Dados desatualizados**

- Clicar no botão "🔄 Atualizar"
- Verificar se o arquivo `ativos.json` foi atualizado recentemente

## 📞 Suporte

Para questões ou sugestões:

- Abrir uma issue no GitHub
- Contactar o mantenedor do projeto

---

**Desenvolvido com ❤️ para facilitar o acesso aos procedimentos de contratação pública**
