let allProcedimentos = []; // Variável global para armazenar todos os procedimentos
let filteredProcedimentos = []; // Variável global para procedimentos filtrados
let currentTags = []; // Tags atuais no modal
let activeSeedCode = null; // Código da seed ativa
let allSeeds = []; // Todas as seeds salvas

// Variáveis para ordenação
let currentSortColumn = null;
let currentSortDirection = 'asc';

function loadProcedimentos() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const tableContainer = document.getElementById('tableContainer');
    
    loading.style.display = 'block';
    error.style.display = 'none';
    tableContainer.style.display = 'none';

    fetch('data/ativos.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Arquivo não encontrado');
            }
            return response.json();
        })
        .then(data => {
            loading.style.display = 'none';
            allProcedimentos = data; // Armazenar todos os procedimentos
            filteredProcedimentos = data; // Inicialmente, mostrar todos
            
            // Aplicar ordenação padrão por data de publicação (mais recente primeiro)
            currentSortColumn = 'publicacao';
            currentSortDirection = 'desc';
            const sortedProcedimentos = sortProcedimentos(data, 'publicacao', 'desc');
            
            displayProcedimentos(sortedProcedimentos);
        })
        .catch(err => {
            loading.style.display = 'none';
            error.style.display = 'block';
            console.error('Erro:', err);
        });
}

function filterProcedimentos() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    
    console.log('🔍 Filtrando procedimentos...');
    console.log('📝 Termo de pesquisa:', searchTerm);
    console.log('🌱 Seed ativa:', activeSeedCode);
    
    // Primeiro filtrar por termo de pesquisa
    let filtered = allProcedimentos;
    
    if (searchTerm !== '') {
        filtered = allProcedimentos.filter(proc => {
            // Criar uma string com todos os campos para pesquisa
            const searchableText = [
                proc.descricao || '',
                proc.designacao_contrato || '',
                proc.entidade || '',
                proc.entidade_adjudicante || '',
                proc.plataforma_eletronica || '',
                proc.preco_base || '',
                proc.prazo_apresentacao_propostas || '',
                proc.nipc || '',
                proc.distrito || '',
                proc.concelho || '',
                proc.freguesia || '',
                proc.site || '',
                proc.email || '',
                proc.numero_procedimento || '',
                proc.prazo_execucao || '',
                proc.fundos_eu || '',
                proc.autor_nome || '',
                proc.autor_cargo || '',
                extractPublicationDate(proc.detalhes_completos) || ''
            ].join(' ').toLowerCase();
            
            return searchableText.includes(searchTerm);
        });
        
        console.log('📊 Após pesquisa por termo:', filtered.length, 'procedimentos');
    }
    
    // Depois filtrar por seed ativa
    if (activeSeedCode) {
        const beforeSeedFilter = filtered.length;
        filtered = filtered.filter(proc => procedureMatchesSeed(proc));
        console.log('🌱 Após filtro de seed:', filtered.length, 'procedimentos (removidos:', beforeSeedFilter - filtered.length, ')');
    }
    
    filteredProcedimentos = filtered;
    
    // Aplicar ordenação atual se existir
    if (currentSortColumn && currentSortDirection) {
        console.log('🔄 Aplicando ordenação:', currentSortColumn, currentSortDirection);
        const sortedProcedimentos = sortProcedimentos(filteredProcedimentos, currentSortColumn, currentSortDirection);
        displayProcedimentos(sortedProcedimentos);
    } else {
        console.log('📋 Exibindo sem ordenação');
        displayProcedimentos(filteredProcedimentos);
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    filteredProcedimentos = allProcedimentos;
    
    // Aplicar ordenação atual se existir
    if (currentSortColumn && currentSortDirection) {
        const sortedProcedimentos = sortProcedimentos(allProcedimentos, currentSortColumn, currentSortDirection);
        displayProcedimentos(sortedProcedimentos);
    } else {
        displayProcedimentos(allProcedimentos);
    }
}

function formatDeadline(deadlineStr) {
    if (!deadlineStr || deadlineStr === 'N/A') return 'N/A';
    
    // Procurar por padrões de data e hora
    const dateTimeMatch = deadlineStr.match(/(\d{1,2})-(\d{1,2})-(\d{4})\s+(\d{1,2}):(\d{2})/);
    if (dateTimeMatch) {
        const [, day, month, year, hour, minute] = dateTimeMatch;
        return `
            <span class="deadline-date">${day}/${month}/${year}</span>
            <span class="deadline-time">${hour}:${minute}</span>
        `;
    }
    
    // Se não encontrar o padrão, retornar o original
    return deadlineStr;
}

function formatPrice(priceStr) {
    if (!priceStr || priceStr === 'N/A') return 'N/A';
    
    // Substituir EUR por €
    return priceStr.replace(/EUR/g, '€').replace(/eur/g, '€');
}

function extractPublicationDate(detalhesCompletos) {
    if (!detalhesCompletos) return 'N/A';
    
    // Procurar por "Data de Envio do Anúncio: DD-MM-YYYY"
    const dateMatch = detalhesCompletos.match(/Data de Envio do Anúncio:\s*(\d{1,2}-\d{1,2}-\d{4})/);
    if (dateMatch) {
        const [, dateStr] = dateMatch;
        // Converter DD-MM-YYYY para DD/MM/YYYY
        return dateStr.replace(/-/g, '/');
    }
    
    return 'N/A';
}

function sortProcedimentos(procedimentos, column, direction) {
    const sortedProcedimentos = [...procedimentos];
    
    sortedProcedimentos.sort((a, b) => {
        let valueA, valueB;
        
        switch (column) {
            case 'descricao':
                valueA = (a.descricao || a.designacao_contrato || '').toLowerCase();
                valueB = (b.descricao || b.designacao_contrato || '').toLowerCase();
                break;
            case 'entidade':
                valueA = (a.entidade || a.entidade_adjudicante || '').toLowerCase();
                valueB = (b.entidade || b.entidade_adjudicante || '').toLowerCase();
                break;
            case 'plataforma':
                valueA = (a.plataforma_eletronica || '').toLowerCase();
                valueB = (b.plataforma_eletronica || '').toLowerCase();
                break;
            case 'publicacao':
                valueA = extractPublicationDate(a.detalhes_completos);
                valueB = extractPublicationDate(b.detalhes_completos);
                // Converter datas para comparação
                if (valueA !== 'N/A' && valueB !== 'N/A') {
                    const dateA = new Date(valueA.split('/').reverse().join('-'));
                    const dateB = new Date(valueB.split('/').reverse().join('-'));
                    valueA = dateA.getTime();
                    valueB = dateB.getTime();
                }
                break;
            case 'prazo':
                valueA = a.prazo_apresentacao_propostas || '';
                valueB = b.prazo_apresentacao_propostas || '';
                // Converter datas para comparação
                if (valueA && valueB) {
                    const dateA = new Date(valueA.split(' ')[0].split('-').reverse().join('-'));
                    const dateB = new Date(valueB.split(' ')[0].split('-').reverse().join('-'));
                    valueA = dateA.getTime();
                    valueB = dateB.getTime();
                }
                break;
            case 'preco':
                valueA = parseFloat((a.preco_base || '0').replace(/[^\d,]/g, '').replace(',', '.'));
                valueB = parseFloat((b.preco_base || '0').replace(/[^\d,]/g, '').replace(',', '.'));
                break;
            default:
                return 0;
        }
        
        if (valueA < valueB) return direction === 'asc' ? -1 : 1;
        if (valueA > valueB) return direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    return sortedProcedimentos;
}

function handleSort(column) {
    let newDirection = 'asc';
    
    if (currentSortColumn === column) {
        newDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    }
    
    currentSortColumn = column;
    currentSortDirection = newDirection;
    
    // Atualizar indicadores visuais
    updateSortIndicators();
    
    // Ordenar os procedimentos filtrados atuais
    const sortedProcedimentos = sortProcedimentos(filteredProcedimentos, column, newDirection);
    displayProcedimentos(sortedProcedimentos);
}

function updateSortIndicators() {
    // Remover todas as classes de ordenação
    document.querySelectorAll('.procedures-table th.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Adicionar classe apropriada ao cabeçalho ativo
    if (currentSortColumn) {
        const activeHeader = document.querySelector(`[data-sort="${currentSortColumn}"]`);
        if (activeHeader) {
            activeHeader.classList.add(currentSortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
        }
    }
}

function displayProcedimentos(procedimentos) {
    const tableBody = document.getElementById('proceduresTableBody');
    const tableContainer = document.getElementById('tableContainer');
    
    tableBody.innerHTML = '';

    if (procedimentos.length === 0) {
        const isMobile = window.innerWidth <= 768;
        const colspan = isMobile ? 6 : 7;
        tableBody.innerHTML = `<tr><td colspan="${colspan}" style="text-align: center; padding: 2rem; color: #666;">Nenhum procedimento encontrado</td></tr>`;
        tableContainer.style.display = 'block';
        return;
    }

    procedimentos.forEach((proc, index) => {
        // Linha principal do procedimento
        const mainRow = document.createElement('tr');
        mainRow.className = 'procedure-row';
        mainRow.onclick = () => toggleRow(index);
        
        mainRow.innerHTML = `
            <td style="text-align: center; width: 50px;">
                <div class="expand-icon">▼</div>
            </td>
            <td style="text-align: left;">
                <div class="procedure-title">${proc.descricao || proc.designacao_contrato || 'Sem descrição'}</div>
            </td>
            <td style="text-align: left;">
                <div class="entity-name">${proc.entidade || proc.entidade_adjudicante || 'N/A'}</div>
            </td>
            <td style="text-align: left;">
                <div class="procedure-platform">${proc.plataforma_eletronica || 'N/A'}</div>
            </td>
            <td style="text-align: center;">
                <div class="publication-date">${extractPublicationDate(proc.detalhes_completos)}</div>
            </td>
            <td style="text-align: center;">
                <div class="deadline">${formatDeadline(proc.prazo_apresentacao_propostas)}</div>
            </td>
            <td style="text-align: left;">
                <div class="price">${formatPrice(proc.preco_base)}</div>
            </td>
        `;
        
        // Linha de detalhes (inicialmente oculta)
        const detailsRow = document.createElement('tr');
        detailsRow.className = 'details-row';
        detailsRow.id = `details-${index}`;
        
        const detailsCell = document.createElement('td');
        detailsCell.className = 'details-cell';
        // Ajustar colSpan baseado no tamanho da tela
        const isMobile = window.innerWidth <= 768;
        detailsCell.colSpan = isMobile ? 6 : 7;
        
        detailsCell.innerHTML = `
            <div class="details-grid">
                <div class="detail-group">
                    <h4>Informações da Entidade</h4>
                    <div class="detail-item">
                        <span class="detail-label">NIPC:</span>
                        <span class="detail-value">${proc.nipc || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Distrito:</span>
                        <span class="detail-value">${proc.distrito || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Concelho:</span>
                        <span class="detail-value">${proc.concelho || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Freguesia:</span>
                        <span class="detail-value">${proc.freguesia || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Site:</span>
                        <span class="detail-value">
                            ${proc.site ? `<a href="${proc.site}" target="_blank">${proc.site}</a>` : 'N/A'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Email:</span>
                        <span class="detail-value">
                            ${proc.email ? `<a href="mailto:${proc.email}">${proc.email}</a>` : 'N/A'}
                        </span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h4>Detalhes do Contrato</h4>
                    <div class="detail-item">
                        <span class="detail-label">Número:</span>
                        <span class="detail-value">${proc.numero_procedimento || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Prazo de Execução:</span>
                        <span class="detail-value">${proc.prazo_execucao || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Fundos EU:</span>
                        <span class="detail-value">${proc.fundos_eu || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">URL do Procedimento:</span>
                        <span class="detail-value">
                            ${proc.link ? `<a href="${proc.link}" target="_blank">Ver no DRE</a>` : 'N/A'}
                        </span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h4>Informações Adicionais</h4>
                    <div class="detail-item">
                        <span class="detail-label">Autor:</span>
                        <span class="detail-value">${proc.autor_nome || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Cargo:</span>
                        <span class="detail-value">${proc.autor_cargo || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">URL Procedimento:</span>
                        <span class="detail-value">
                            ${proc.url_procedimento ? `<a href="${proc.url_procedimento}" target="_blank">Aceder</a>` : 'N/A'}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        detailsRow.appendChild(detailsCell);
        
        tableBody.appendChild(mainRow);
        tableBody.appendChild(detailsRow);
    });
    
    tableContainer.style.display = 'block';
    
    // Atualizar indicadores de ordenação
    updateSortIndicators();
}

function toggleRow(index) {
    const detailsRow = document.getElementById(`details-${index}`);
    const mainRow = detailsRow.previousElementSibling;
    
    if (detailsRow.classList.contains('show')) {
        detailsRow.classList.remove('show');
        mainRow.classList.remove('expanded');
    } else {
        // Fechar todos os outros
        document.querySelectorAll('.details-row').forEach(row => {
            row.classList.remove('show');
        });
        document.querySelectorAll('.procedure-row').forEach(row => {
            row.classList.remove('expanded');
        });
        
        // Abrir o selecionado
        detailsRow.classList.add('show');
        mainRow.classList.add('expanded');
    }
}

// Funções para gerenciar seeds
function openSeedModal() {
    document.getElementById('seedModal').classList.add('show');
    document.getElementById('seedInput').focus();
    document.getElementById('districtSelect').value = '';
    currentTags = [];
    updateTagsDisplay();
}

function closeSeedModal() {
    document.getElementById('seedModal').classList.remove('show');
    document.getElementById('seedInput').value = '';
    document.getElementById('districtSelect').value = '';
    currentTags = [];
    updateTagsDisplay();
}

function handleSeedInput(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const input = document.getElementById('seedInput');
        const value = input.value.trim();
        
        if (value) {
            addTag(value);
            input.value = '';
        }
    } else if (event.key === ',') {
        event.preventDefault();
        const input = document.getElementById('seedInput');
        const value = input.value.trim();
        
        if (value) {
            addTag(value);
            input.value = '';
        }
    }
}

function addTag(tagText) {
    const cleanTag = tagText.trim().toLowerCase();
    if (cleanTag && !currentTags.includes(cleanTag)) {
        currentTags.push(cleanTag);
        updateTagsDisplay();
    }
}

function removeTag(tagIndex) {
    currentTags.splice(tagIndex, 1);
    updateTagsDisplay();
}

function updateTagsDisplay() {
    const container = document.getElementById('tagsContainer');
    container.innerHTML = '';
    
    currentTags.forEach((tag, index) => {
        const tagElement = document.createElement('div');
        tagElement.className = 'tag';
        tagElement.innerHTML = `
            ${tag}
            <button class="tag-remove" onclick="removeTag(${index})">&times;</button>
        `;
        container.appendChild(tagElement);
    });
}

function saveSeed() {
    const tags = currentTags;
    const district = document.getElementById('districtSelect').value;
    
    if (tags.length === 0) {
        alert('Adicione pelo menos uma palavra-chave.');
        return;
    }
    
    const seedCode = generateSeedCode();
    const seedName = tags.slice(0, 2).join(', ') + (tags.length > 2 ? '...' : '');
    
    const newSeed = {
        code: seedCode,
        tags: tags,
        district: district,
        name: seedName,
        created: new Date().toISOString()
    };
    
    allSeeds.push(newSeed);
    saveSeedsToFile();
    
    // Mostrar modal com detalhes da seed criada
    showSeedCreatedModal(newSeed);
    
    closeSeedModal();
}

function generateSeedCode() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = 'SEED';
    for (let i = 0; i < 6; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

function saveSeedsToFile() {
    // Salvar seeds no localStorage (método principal)
    localStorage.setItem('dre_seeds', JSON.stringify(allSeeds));
    console.log('Seeds salvas no localStorage:', allSeeds.length);
}

function loadSeedsFromFile() {
    // Carregar seeds do localStorage (prioridade)
    const saved = localStorage.getItem('dre_seeds');
    if (saved) {
        try {
            allSeeds = JSON.parse(saved);
            console.log('Seeds carregadas do localStorage:', allSeeds.length);
            return;
        } catch (err) {
            console.log('Erro ao carregar seeds do localStorage:', err);
        }
    }
    
    // Fallback para o ficheiro JSON (se existir)
    fetch('data/seeds.json')
        .then(response => {
            if (!response.ok) {
                console.log('Ficheiro seeds.json não encontrado');
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                allSeeds = data;
                console.log('Seeds carregadas do ficheiro:', allSeeds.length);
                // Salvar no localStorage para futuras sessões
                localStorage.setItem('dre_seeds', JSON.stringify(allSeeds));
            }
        })
        .catch(err => {
            console.log('Erro ao carregar seeds do ficheiro:', err);
        });
}

function searchBySeed() {
    const seedCode = document.getElementById('seedSearchInput').value.trim().toUpperCase();
    
    if (!seedCode) {
        alert('Digite um código de seed válido.');
        return;
    }

    const seed = allSeeds.find(s => s.code === seedCode);
    if (!seed) {
        alert('Seed não encontrada. Verifique o código e tente novamente.');
        return;
    }

    activeSeedCode = seedCode;
    updateActiveSeedDisplay();
    
    // Aplicar filtragem das seeds primeiro, depois ordenação
    filterProcedimentos();
}

function clearSeedSearch() {
    activeSeedCode = null;
    document.getElementById('seedSearchInput').value = '';
    updateActiveSeedDisplay();
    
    // Aplicar filtragem sem seeds, depois ordenação
    filterProcedimentos();
}

function clearActiveSeeds() {
    activeSeedCode = null;
    document.getElementById('seedSearchInput').value = '';
    updateActiveSeedDisplay();
    
    // Aplicar filtragem sem seeds, depois ordenação
    filterProcedimentos();
}

function showAvailableSeeds() {
    showSeedsListModal();
}

function updateActiveSeedDisplay() {
    const filterContainer = document.getElementById('seedFilter');
    const activeSeedsContainer = document.getElementById('activeSeeds');
    
    if (!activeSeedCode) {
        filterContainer.style.display = 'none';
        return;
    }
    
    const seed = allSeeds.find(s => s.code === activeSeedCode);
    if (!seed) {
        filterContainer.style.display = 'none';
        return;
    }
    
    filterContainer.style.display = 'block';
    activeSeedsContainer.innerHTML = '';
    
    const seedElement = document.createElement('div');
    seedElement.className = 'active-seed';
    const districtInfo = seed.district ? ` (${seed.district})` : ' (Todos os distritos)';
    seedElement.innerHTML = `
        <span>${seed.code} - ${seed.name}${districtInfo}</span>
        <button onclick="clearSeedSearch()" style="background: #dc3545; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 3px; font-size: 0.75rem; cursor: pointer; margin-left: 0.5rem;">✕</button>
    `;
    activeSeedsContainer.appendChild(seedElement);
}

// Função para verificar se um procedimento corresponde à seed ativa
function procedureMatchesSeed(procedure) {
    if (!activeSeedCode) return true;
    
    const seed = allSeeds.find(s => s.code === activeSeedCode);
    if (!seed) return true;
    
    console.log('🔍 Verificando procedimento:', procedure.entidade, 'contra seed:', seed.code);
    console.log('🏷️ Tags da seed:', seed.tags);
    console.log('📍 Distrito da seed:', seed.district);
    console.log('📍 Distrito do procedimento:', procedure.distrito);
    
    // Verificar se o procedimento está no distrito correto
    if (seed.district && seed.district !== '') {
        const procedureDistrict = (procedure.distrito || '').toLowerCase();
        const seedDistrict = seed.district.toLowerCase();
        
        console.log('📍 Comparando distritos:', procedureDistrict, 'vs', seedDistrict);
        
        // Verificar se o distrito do procedimento corresponde ao distrito da seed
        if (procedureDistrict !== seedDistrict) {
            console.log('❌ Distrito não corresponde');
            return false;
        }
        
        console.log('✅ Distrito corresponde');
    }
    
    // Verificar se alguma tag da seed aparece no procedimento
    const procedureText = [
        procedure.descricao || '',
        procedure.designacao_contrato || '',
        procedure.entidade || '',
        procedure.entidade_adjudicante || '',
        procedure.plataforma_eletronica || '',
        procedure.preco_base || '',
        procedure.prazo_apresentacao_propostas || '',
        procedure.nipc || '',
        procedure.distrito || '',
        procedure.concelho || '',
        procedure.freguesia || '',
        procedure.site || '',
        procedure.email || '',
        procedure.numero_procedimento || '',
        procedure.prazo_execucao || '',
        procedure.fundos_eu || '',
        procedure.autor_nome || '',
        procedure.autor_cargo || '',
        extractPublicationDate(procedure.detalhes_completos) || ''
    ].join(' ').toLowerCase();
    
    console.log('📝 Texto do procedimento (primeiros 200 chars):', procedureText.substring(0, 200));
    
    const matches = seed.tags.some(tag => {
        const tagFound = procedureText.includes(tag.toLowerCase());
        console.log('🏷️ Tag:', tag, '->', tagFound ? '✅ Encontrada' : '❌ Não encontrada');
        return tagFound;
    });
    
    console.log('🎯 Resultado final:', matches ? '✅ Procedimento corresponde à seed' : '❌ Procedimento não corresponde à seed');
    
    return matches;
}

// Funções para os novos modais
function showSeedCreatedModal(seed) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.display = 'flex';
    modal.innerHTML = `
        <div class="modal" style="max-width: 500px;">
            <div class="modal-header">
                <h3 class="modal-title">✅ Seed Criada com Sucesso!</h3>
                <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <div style="margin-bottom: 1rem;">
                    <strong>Nome:</strong> ${seed.name}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Distrito:</strong> ${seed.district || 'Todos os distritos'}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Tags:</strong> ${seed.tags.join(', ')}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Código da Seed:</strong>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                        <span class="seed-code" onclick="copyToClipboard('${seed.code}')" style="cursor: pointer;">${seed.code}</span>
                        <button onclick="copyToClipboard('${seed.code}')" style="background: #28a745; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">Copiar</button>
                    </div>
                </div>
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 6px; border-left: 4px solid #2196f3; font-size: 0.9rem; color: #1976d2;">
                    💡 Guarde este código para usar na pesquisa de seeds!
                </div>
            </div>
            
            <div class="modal-actions">
                <button class="cancel-btn" onclick="this.closest('.modal-overlay').remove()">Fechar</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function showSeedsListModal() {
    const modal = document.getElementById('seedsListModal');
    const container = document.getElementById('seedsListContainer');
    
    container.innerHTML = '';
    
    if (allSeeds.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #6c757d;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🌱</div>
                <h4 style="margin-bottom: 0.5rem;">Nenhuma seed criada ainda</h4>
                <p style="font-size: 0.9rem;">Crie uma nova seed usando o botão "Criar Seed" para começar a filtrar procedimentos automaticamente.</p>
            </div>
        `;
    } else {
        allSeeds.forEach((seed, index) => {
            const seedElement = document.createElement('div');
            seedElement.className = 'seed-item';
            
            const districtInfo = seed.district ? seed.district : 'Todos os distritos';
            const createdDate = new Date(seed.created).toLocaleDateString('pt-PT');
            
            seedElement.innerHTML = `
                <div class="seed-header">
                    <div class="seed-name">${seed.name}</div>
                    <div class="seed-code" onclick="copyToClipboard('${seed.code}')" title="Clique para copiar">${seed.code}</div>
                </div>
                <div class="seed-details">
                    <div class="seed-detail">
                        <strong>Distrito:</strong> ${districtInfo}
                    </div>
                    <div class="seed-detail">
                        <strong>Criada:</strong> ${createdDate}
                    </div>
                    <div class="seed-detail" style="grid-column: 1 / -1;">
                        <strong>Tags:</strong> ${seed.tags.join(', ')}
                    </div>
                </div>
            `;
            
            container.appendChild(seedElement);
        });
    }
    
    modal.classList.add('show');
}

function closeSeedsListModal() {
    document.getElementById('seedsListModal').classList.remove('show');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showCopyFeedback('Código copiado!');
    }).catch(() => {
        // Fallback para navegadores mais antigos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showCopyFeedback('Código copiado!');
    });
}

function showCopyFeedback(message) {
    const feedback = document.createElement('div');
    feedback.className = 'copy-feedback';
    feedback.textContent = message;
    document.body.appendChild(feedback);
    
    setTimeout(() => {
        feedback.remove();
    }, 2000);
}

// Carregar procedimentos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    loadSeedsFromFile();
    loadProcedimentos();
    
    // Adicionar event listeners para ordenação
    document.querySelectorAll('.procedures-table th.sortable').forEach(th => {
        th.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            handleSort(column);
        });
    });
    
    // Listener para redimensionamento da janela
    window.addEventListener('resize', function() {
        // Reajustar colSpan das linhas de detalhes existentes
        const detailsRows = document.querySelectorAll('.details-row');
        const isMobile = window.innerWidth <= 768;
        const newColSpan = isMobile ? 6 : 7;
        
        detailsRows.forEach(row => {
            const cell = row.querySelector('.details-cell');
            if (cell) {
                cell.colSpan = newColSpan;
            }
        });
    });
});
