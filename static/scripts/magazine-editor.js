// Magazine Editor JavaScript

// Global variables
let currentArticleId = null;
let currentMagazineId = null;
let currentArticleData = null;
let contentBlocks = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    currentMagazineId = document.getElementById('magazineId').value;
    
    // Load first article if exists
    const firstArticle = document.querySelector('.article-item');
    if (firstArticle) {
        const articleId = firstArticle.dataset.articleId;
        loadArticle(articleId);
    }
});

// Create new article
function createArticle() {
    if (!currentMagazineId) return;
    
    const title = prompt('Enter article title:');
    if (!title) return;
    
    fetch(`${languagePrefix}/magazine/${currentMagazineId}/article/create/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error creating article: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating article');
    });
}

// Load article
function loadArticle(articleId) {
    currentArticleId = articleId;
    
    // Update active state
    document.querySelectorAll('.article-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-article-id="${articleId}"]`).classList.add('active');
    
    // Show editor
    document.getElementById('articleEditor').style.display = 'block';
    document.getElementById('emptyState').style.display = 'none';
    
    // Load article data
    fetch(`${languagePrefix}/magazine/article/${articleId}/data/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentArticleData = data.article;
                populateArticleForm(data.article);
                loadContentBlocks(data.article.content_blocks || []);
                updateLivePreview(); // Update preview after loading
            }
        })
        .catch(error => {
            console.error('Error loading article:', error);
        });
}

// Populate article form
function populateArticleForm(article) {
    document.getElementById('articleTitle').value = article.title || '';
    document.getElementById('articleCategory').value = article.category || '';
    document.getElementById('articleTeaser').value = article.teaser || '';
    document.getElementById('isMainStory').checked = article.is_main_story || false;
    document.getElementById('currentArticleId').value = article.id;
}

// Load content blocks
function loadContentBlocks(blocks) {
    contentBlocks = blocks;
    const container = document.getElementById('contentBlocks');
    container.innerHTML = '';
    
    if (blocks.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-edit fa-2x mb-2"></i>
                <p class="small mb-0">No content yet. Add text or images to begin.</p>
            </div>
        `;
        updateLivePreview(); // Update even if empty
        return;
    }
    
    blocks.forEach((block, index) => {
        const blockHtml = createBlockHtml(block, index);
        container.insertAdjacentHTML('beforeend', blockHtml);
    });
    
    updateLivePreview(); // Update after loading blocks
}

// Create block HTML
function createBlockHtml(block, index) {
    if (block.block_type === 'text') {
        return `
            <div class="content-block mb-3" data-block-id="${block.id}" data-block-index="${index}">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div class="text-muted small">
                                <i class="fas fa-paragraph me-1"></i> Text Block
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-secondary" onclick="moveBlockUp(${index})" ${index === 0 ? 'disabled' : ''}>
                                    <i class="fas fa-arrow-up"></i>
                                </button>
                                <button class="btn btn-outline-secondary" onclick="moveBlockDown(${index})" ${index === contentBlocks.length - 1 ? 'disabled' : ''}>
                                    <i class="fas fa-arrow-down"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteBlock(${block.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <textarea class="form-control" rows="5" id="block-text-${block.id}" onchange="updateBlock(${block.id})">${block.text_content || ''}</textarea>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <select class="form-select form-select-sm" id="block-align-${block.id}" onchange="updateBlock(${block.id})">
                                    <option value="left" ${block.alignment === 'left' ? 'selected' : ''}>Align Left</option>
                                    <option value="center" ${block.alignment === 'center' ? 'selected' : ''}>Align Center</option>
                                    <option value="right" ${block.alignment === 'right' ? 'selected' : ''}>Align Right</option>
                                    <option value="justify" ${block.alignment === 'justify' ? 'selected' : ''}>Justify</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <select class="form-select form-select-sm" id="block-size-${block.id}" onchange="updateBlock(${block.id})">
                                    <option value="sm" ${block.font_size === 'sm' ? 'selected' : ''}>Small</option>
                                    <option value="base" ${block.font_size === 'base' || !block.font_size ? 'selected' : ''}>Normal</option>
                                    <option value="lg" ${block.font_size === 'lg' ? 'selected' : ''}>Large</option>
                                    <option value="xl" ${block.font_size === 'xl' ? 'selected' : ''}>Extra Large</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (block.block_type === 'image') {
        return `
            <div class="content-block mb-3" data-block-id="${block.id}" data-block-index="${index}">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div class="text-muted small">
                                <i class="fas fa-image me-1"></i> Image Block
                            </div>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-secondary" onclick="moveBlockUp(${index})" ${index === 0 ? 'disabled' : ''}>
                                    <i class="fas fa-arrow-up"></i>
                                </button>
                                <button class="btn btn-outline-secondary" onclick="moveBlockDown(${index})" ${index === contentBlocks.length - 1 ? 'disabled' : ''}>
                                    <i class="fas fa-arrow-down"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteBlock(${block.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        ${block.image_url || block.image ? `<img src="${block.image_url || block.image}" class="img-fluid mb-2 rounded" alt="">` : ''}
                        <input type="text" class="form-control mb-2" id="block-imgurl-${block.id}" placeholder="Image URL" value="${block.image_url || ''}" onchange="updateBlock(${block.id})">
                        <input type="text" class="form-control form-control-sm" id="block-caption-${block.id}" placeholder="Image caption (optional)" value="${block.image_caption || ''}" onchange="updateBlock(${block.id})">
                    </div>
                </div>
            </div>
        `;
    }
}

// Add text block
function addTextBlock() {
    if (!currentArticleId) return;
    
    fetch(`${languagePrefix}/magazine/article/${currentArticleId}/block/create/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            block_type: 'text',
            text_content: 'Enter your text here...'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadArticle(currentArticleId);
            // Scroll to new block after content loads
            setTimeout(() => {
                const contentBlocks = document.getElementById('contentBlocks');
                if (contentBlocks && contentBlocks.lastElementChild) {
                    contentBlocks.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 300);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Add image block
function addImageBlock() {
    if (!currentArticleId) return;
    
    // Create file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Show loading indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'alert alert-info';
        loadingMsg.textContent = 'Uploading image...';
        document.getElementById('contentBlocks').appendChild(loadingMsg);
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('image', file);
        formData.append('block_type', 'image');
        
        try {
            const response = await fetch(`${languagePrefix}/magazine/article/${currentArticleId}/block/create/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                loadArticle(currentArticleId);
                // Scroll to new block after content loads
                setTimeout(() => {
                    const contentBlocks = document.getElementById('contentBlocks');
                    if (contentBlocks && contentBlocks.lastElementChild) {
                        contentBlocks.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 300);
            } else {
                alert('Error uploading image: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error uploading image');
        } finally {
            loadingMsg.remove();
        }
    };
    
    // Trigger file picker
    input.click();
}

// Update block
function updateBlock(blockId) {
    const textContent = document.getElementById(`block-text-${blockId}`)?.value;
    const alignment = document.getElementById(`block-align-${blockId}`)?.value;
    const fontSize = document.getElementById(`block-size-${blockId}`)?.value;
    const imageUrl = document.getElementById(`block-imgurl-${blockId}`)?.value;
    const caption = document.getElementById(`block-caption-${blockId}`)?.value;
    
    const data = {};
    if (textContent !== undefined) data.text_content = textContent;
    if (alignment !== undefined) data.alignment = alignment;
    if (fontSize !== undefined) data.font_size = fontSize;
    if (imageUrl !== undefined) data.image_url = imageUrl;
    if (caption !== undefined) data.image_caption = caption;
    
    // Update local contentBlocks array for live preview
    const blockIndex = contentBlocks.findIndex(b => b.id === blockId);
    if (blockIndex !== -1) {
        contentBlocks[blockIndex] = { ...contentBlocks[blockIndex], ...data };
        updateLivePreview(); // Update preview immediately
    }
    
    fetch(`${languagePrefix}/magazine/block/${blockId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Error updating block');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Delete block
function deleteBlock(blockId) {
    if (!confirm('Delete this content block?')) return;
    
    fetch(`${languagePrefix}/magazine/block/${blockId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadArticle(currentArticleId);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Move block up
function moveBlockUp(index) {
    if (index === 0) return;
    
    // Swap blocks in array
    const temp = contentBlocks[index];
    contentBlocks[index] = contentBlocks[index - 1];
    contentBlocks[index - 1] = temp;
    
    // Update order in backend
    updateBlockOrders();
    
    // Reload to reflect changes
    loadContentBlocks(contentBlocks);
}

// Move block down
function moveBlockDown(index) {
    if (index >= contentBlocks.length - 1) return;
    
    // Swap blocks in array
    const temp = contentBlocks[index];
    contentBlocks[index] = contentBlocks[index + 1];
    contentBlocks[index + 1] = temp;
    
    // Update order in backend
    updateBlockOrders();
    
    // Reload to reflect changes
    loadContentBlocks(contentBlocks);
}

// Update block orders in backend
function updateBlockOrders() {
    if (!currentArticleId) return;
    
    const blockOrders = contentBlocks.map((block, index) => ({
        id: block.id,
        order: index
    }));
    
    fetch(`${languagePrefix}/magazine/article/${currentArticleId}/reorder-blocks/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ blocks: blockOrders })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Error updating block order');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Save article
function saveArticle() {
    if (!currentArticleId) return;
    
    const data = {
        title: document.getElementById('articleTitle').value,
        category: document.getElementById('articleCategory').value,
        teaser: document.getElementById('articleTeaser').value,
        is_main_story: document.getElementById('isMainStory').checked
    };
    
    fetch(`${languagePrefix}/magazine/article/${currentArticleId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Article saved successfully!');
            window.location.reload();
        } else {
            alert('Error saving article: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving article');
    });
}

// Delete article
function deleteArticle(articleId, event) {
    event.stopPropagation();
    
    if (!confirm('Delete this article?')) return;
    
    fetch(`${languagePrefix}/magazine/article/${articleId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error deleting article');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting article');
    });
}

// Open config modal
function openConfigModal() {
    const modal = new bootstrap.Modal(document.getElementById('configModal'));
    
    // Sync modal values with sidebar values
    const sidebarPrimaryFont = document.getElementById('sidebarPrimaryFont');
    const sidebarSecondaryFont = document.getElementById('sidebarSecondaryFont');
    const sidebarTextColor = document.getElementById('sidebarTextColor');
    const sidebarBodyTextColor = document.getElementById('sidebarBodyTextColor');
    
    const configPrimaryFont = document.getElementById('configPrimaryFont');
    const configSecondaryFont = document.getElementById('configSecondaryFont');
    const configTextColor = document.getElementById('configTextColor');
    const configBodyTextColor = document.getElementById('configBodyTextColor');
    
    if (sidebarPrimaryFont && configPrimaryFont) configPrimaryFont.value = sidebarPrimaryFont.value;
    if (sidebarSecondaryFont && configSecondaryFont) configSecondaryFont.value = sidebarSecondaryFont.value;
    if (sidebarTextColor && configTextColor) configTextColor.value = sidebarTextColor.value;
    if (sidebarBodyTextColor && configBodyTextColor) configBodyTextColor.value = sidebarBodyTextColor.value;
    
    modal.show();
    
    // Highlight currently selected background and show/hide gradient colors
    setTimeout(() => {
        const currentBg = document.getElementById('configCoverBackground').value;
        const isGradient = !currentBg || currentBg === '';
        
        // Show/hide gradient color sections
        document.getElementById('gradientColorsSection').style.display = isGradient ? 'block' : 'none';
        document.getElementById('primaryColorSection').style.display = isGradient ? 'block' : 'none';
        document.getElementById('secondaryColorSection').style.display = isGradient ? 'block' : 'none';
        
        // Highlight selected background
        document.querySelectorAll('.background-option').forEach(option => {
            option.classList.remove('selected');
            if (option.dataset.bg === currentBg || (isGradient && option.dataset.bg === 'gradient')) {
                option.classList.add('selected');
            }
        });
    }, 100);
}

// Select background from gallery
function selectBackground(bgValue) {
    const input = document.getElementById('configCoverBackground');
    
    if (bgValue === 'gradient') {
        input.value = '';
        // Show gradient color pickers
        document.getElementById('gradientColorsSection').style.display = 'block';
        document.getElementById('primaryColorSection').style.display = 'block';
        document.getElementById('secondaryColorSection').style.display = 'block';
    } else {
        input.value = bgValue;
        // Hide gradient color pickers
        document.getElementById('gradientColorsSection').style.display = 'none';
        document.getElementById('primaryColorSection').style.display = 'none';
        document.getElementById('secondaryColorSection').style.display = 'none';
    }
    
    // Update selection UI
    document.querySelectorAll('.background-option').forEach(option => {
        option.classList.remove('selected');
        if (option.dataset.bg === bgValue) {
            option.classList.add('selected');
        }
    });
    
    // Trigger live preview update
    updateLivePreview();
}

// Debounced save typography to backend
let typographySaveTimeout;
function saveTypographyToBackend() {
    clearTimeout(typographySaveTimeout);
    typographySaveTimeout = setTimeout(() => {
        const primaryFont = document.getElementById('sidebarPrimaryFont').value;
        const secondaryFont = document.getElementById('sidebarSecondaryFont').value;
        const textColor = document.getElementById('sidebarTextColor').value;
        const bodyTextColor = document.getElementById('sidebarBodyTextColor').value;
        
        const data = {
            primary_font: primaryFont,
            secondary_font: secondaryFont,
            text_color: textColor,
            background_color: bodyTextColor
        };
        
        fetch(`${languagePrefix}/magazine/${currentMagazineId}/update/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Typography saved');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }, 1000); // Save after 1 second of no changes
}

// Update magazine typography from sidebar controls - instant preview
function updateMagazineTypography() {
    // Sync with modal inputs if they exist
    const primaryFont = document.getElementById('sidebarPrimaryFont').value;
    const secondaryFont = document.getElementById('sidebarSecondaryFont').value;
    const textColor = document.getElementById('sidebarTextColor').value;
    const bodyTextColor = document.getElementById('sidebarBodyTextColor').value;
    
    const configPrimaryFont = document.getElementById('configPrimaryFont');
    const configSecondaryFont = document.getElementById('configSecondaryFont');
    const configTextColor = document.getElementById('configTextColor');
    const configBodyTextColor = document.getElementById('configBodyTextColor');
    
    if (configPrimaryFont) configPrimaryFont.value = primaryFont;
    if (configSecondaryFont) configSecondaryFont.value = secondaryFont;
    if (configTextColor) configTextColor.value = textColor;
    if (configBodyTextColor) configBodyTextColor.value = bodyTextColor;
    
    // Update live preview immediately
    updateLivePreview();
    
    // Save to backend with debounce
    saveTypographyToBackend();
}

// Save magazine config
function saveMagazineConfig() {
    // Get typography values from sidebar
    const primaryFont = document.getElementById('sidebarPrimaryFont').value;
    const secondaryFont = document.getElementById('sidebarSecondaryFont').value;
    const textColor = document.getElementById('sidebarTextColor').value;
    const bodyTextColor = document.getElementById('sidebarBodyTextColor').value;
    
    const data = {
        title: document.getElementById('configTitle').value,
        issue_number: document.getElementById('configIssue').value,
        tagline: document.getElementById('configTagline').value,
        primary_color: document.getElementById('configPrimaryColor')?.value || '#667eea',
        secondary_color: document.getElementById('configSecondaryColor')?.value || '#764ba2',
        categories: document.getElementById('configCategories').value,
        cover_background_image: document.getElementById('configCoverBackground').value,
        cover_header_position: document.getElementById('configHeaderPosition').value,
        primary_font: primaryFont,
        secondary_font: secondaryFont,
        text_color: textColor,
        background_color: bodyTextColor
    };
    
    fetch(`${languagePrefix}/magazine/${currentMagazineId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Settings saved successfully!');
            window.location.reload();
        } else {
            alert('Error saving settings');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving settings');
    });
}

// ============ LIVE PREVIEW FUNCTIONS ============

// Toggle preview panel
function togglePreview() {
    const previewCol = document.getElementById('livePreviewColumn');
    const editorContainer = document.querySelector('.magazine-editor');
    
    if (previewCol.classList.contains('hidden')) {
        previewCol.classList.remove('hidden');
        editorContainer.classList.remove('preview-hidden');
        updateLivePreview();
    } else {
        previewCol.classList.add('hidden');
        editorContainer.classList.add('preview-hidden');
    }
}

// Update live preview in real-time
async function updateLivePreview() {
    const previewContainer = document.getElementById('livePreview');
    
    // Get magazine data
    const magazineTitle = document.getElementById('magazineTitle').textContent;
    const magazineIssue = document.getElementById('magazineIssue').textContent;
    const primaryColor = document.getElementById('configPrimaryColor')?.value || '#667eea';
    const secondaryColor = document.getElementById('configSecondaryColor')?.value || '#764ba2';
    const tagline = document.getElementById('configTagline')?.value || '';
    const coverBackground = document.getElementById('configCoverBackground')?.value || '';
    const headerPosition = document.getElementById('configHeaderPosition')?.value || 'center';
    
    // Get typography from SIDEBAR (real-time controls)
    const primaryFont = document.getElementById('sidebarPrimaryFont')?.value || 'Playfair Display';
    const secondaryFont = document.getElementById('sidebarSecondaryFont')?.value || 'Lato';
    const textColor = document.getElementById('sidebarTextColor')?.value || '#2d2d2d';
    const bodyTextColor = document.getElementById('sidebarBodyTextColor')?.value || '#333333';
    
    // Get current article values from form (for live editing)
    const currentTitle = document.getElementById('articleTitle')?.value || '';
    const currentCategory = document.getElementById('articleCategory')?.value || '';
    const currentTeaser = document.getElementById('articleTeaser')?.value || '';
    const currentIsMainStory = document.getElementById('isMainStory')?.checked || false;
    
    // Get all articles from sidebar
    const articleItems = document.querySelectorAll('.article-item');
    const allArticlesData = [];
    
    // Load all articles data
    for (let item of articleItems) {
        const articleId = item.dataset.articleId;
        const isActive = item.classList.contains('active');
        
        if (isActive && currentArticleData) {
            // Use live data for currently edited article
            allArticlesData.push({
                id: articleId,
                title: currentTitle || 'Untitled',
                category: currentCategory || 'Uncategorized',
                teaser: currentTeaser,
                is_main_story: currentIsMainStory,
                content_blocks: contentBlocks,
                isActive: true
            });
        } else {
            // Fetch data for other articles
            try {
                const response = await fetch(`${languagePrefix}/magazine/article/${articleId}/data/`);
                const data = await response.json();
                if (data.success) {
                    allArticlesData.push({
                        ...data.article,
                        isActive: false
                    });
                }
            } catch (error) {
                console.error('Error loading article:', error);
            }
        }
    }
    
    // Find main story for cover
    const mainStory = allArticlesData.find(a => a.is_main_story);
    
    // Build professional magazine-style preview HTML with all pages
    // Cover page background - use image if set, otherwise gradient
    // Add dark overlay for better text readability
    const coverStyle = coverBackground 
        ? `background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('${coverBackground}') center/cover no-repeat;`
        : `background: linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%);`;
    
    // Cover page alignment based on header position
    const alignItems = headerPosition === 'top' ? 'flex-start' : 
                       headerPosition === 'bottom' ? 'flex-end' : 
                       'center';
    const paddingTop = headerPosition === 'top' ? '80px' : '40px';
    const paddingBottom = headerPosition === 'bottom' ? '80px' : '40px';
    
    let html = `
        <!-- COVER PAGE -->
        <div class="preview-magazine-page" style="${coverStyle} display: flex; align-items: ${alignItems}; justify-content: center; text-align: center; min-height: 700px; padding: 80px 60px; padding-top: ${paddingTop}; padding-bottom: ${paddingBottom};">
            <div style="width: 100%;">
                <h1 style="font-family: '${primaryFont}', serif; color: ${textColor}; font-size: 4rem; font-weight: 900; margin-bottom: 1rem; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3); letter-spacing: 2px;">
                    ${magazineTitle}
                </h1>
                ${mainStory ? `
                    <div style="margin-top: 60px; padding-top: 40px; border-top: 2px solid rgba(128, 128, 128, 0.3);">
                        <h2 style="font-family: '${primaryFont}', serif; color: ${textColor}; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">${mainStory.title}</h2>
                        ${mainStory.teaser ? `<p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; font-size: 1.125rem; opacity: 0.9;">${mainStory.teaser}</p>` : ''}
                    </div>
                ` : ''}
                <div style="margin-top: 30px; padding-top: 10px; padding-bottom: 10px; border-top: 1px solid ${bodyTextColor}; border-bottom: 1px solid ${bodyTextColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; opacity: 0.75; font-size: 1rem; margin: 0; flex: 1; text-align: left;">Issue ${magazineIssue}</p>
                        ${tagline ? `<p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; opacity: 0.75; font-size: 1rem; margin: 0; flex: 1; text-align: center;">${tagline}</p>` : ''}
                        <p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; opacity: 0.75; font-size: 1rem; margin: 0; flex: 1; text-align: right;">${new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- TABLE OF CONTENTS -->
        <div class="preview-magazine-page" style="min-height: 700px; padding: 60px 50px; background: white;">
            <h1 style="font-family: '${primaryFont}', serif; font-size: 2.5rem; font-weight: 700; margin-bottom: 2rem; text-align: center; color: ${textColor};">
                Contents
            </h1>
            <div style="margin-top: 30px;">
    `;
    
    // Add TOC items
    allArticlesData.forEach((article, index) => {
        html += `
            <div style="padding: 20px 0; border-bottom: 1px solid #e0e0e0; transition: all 0.2s; ${article.isActive ? 'background: #f8f9fa; padding-left: 15px;' : ''}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h5 style="font-family: '${primaryFont}', serif; font-size: 1.3rem; font-weight: 700; margin-bottom: 5px; color: ${textColor};">
                            ${article.title || 'Untitled'}
                        </h5>
                        <p style="font-family: '${secondaryFont}', sans-serif; margin: 0; margin-bottom: ${article.teaser ? '4px' : '0'}; font-size: 0.875rem; color: ${bodyTextColor};">${article.category}</p>
                        ${article.teaser ? `<p style="font-family: '${secondaryFont}', sans-serif; margin: 0; margin-top: 4px; font-size: 0.875rem; color: ${bodyTextColor};">${article.teaser}</p>` : ''}
                    </div>
                    <div style="margin-left: 20px;">
                        <span style="background: #6c757d; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem;">
                            Page ${index + 3}
                        </span>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    // Add all article pages
    allArticlesData.forEach((article, index) => {
        html += `
            <!-- ARTICLE PAGE ${index + 1} -->
            <div class="preview-magazine-page" style="position: relative; min-height: 700px; padding: 60px 50px; padding-bottom: 80px; background: white; ${article.isActive ? 'border: 3px solid ' + primaryColor + ';' : ''}">
                <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid ${primaryColor};">
                    <p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; text-transform: uppercase; font-size: 0.875rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 0.5rem;">
                        ${article.category || 'Uncategorized'}
                    </p>
                    <h1 style="font-family: '${primaryFont}', serif; color: ${textColor}; font-size: 2.8rem; line-height: 1.2; margin-bottom: 15px; font-weight: 700;">
                        ${article.title || 'Untitled Article'}
                    </h1>
                    ${article.teaser ? `<p style="font-family: '${secondaryFont}', sans-serif; color: #666; font-size: 1rem;">${article.teaser}</p>` : ''}
                </div>
                
                <div class="preview-article-content">
        `;
        
        // Add content blocks
        if (article.content_blocks && article.content_blocks.length > 0) {
            article.content_blocks.forEach(block => {
                if (block.block_type === 'text') {
                    const fontSize = block.font_size === 'sm' ? '0.875rem' : 
                                   block.font_size === 'lg' ? '1.125rem' : 
                                   block.font_size === 'xl' ? '1.5rem' : '1.1rem';
                    const fontWeight = block.font_size === 'xl' ? '700' : 'normal';
                    const textColor = block.text_color || '#333';
                    const textAlign = block.alignment || 'justify';
                    
                    html += `
                        <div style="margin-bottom: 20px;">
                            <p style="font-family: '${secondaryFont}', sans-serif; font-size: ${fontSize}; font-weight: ${fontWeight}; color: ${bodyTextColor}; line-height: 1.8; text-align: ${textAlign}; margin-bottom: 15px;">
                                ${(block.text_content || '').replace(/\n/g, '<br>')}
                            </p>
                        </div>
                    `;
                } else if (block.block_type === 'image') {
                    const imageUrl = block.image_url || (block.image ? block.image : '');
                    if (imageUrl) {
                        html += `
                            <div style="margin: 30px 0; text-align: center;">
                                <img src="${imageUrl}" alt="${block.image_caption || ''}" style="max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                                ${block.image_caption ? `<p style="font-family: '${secondaryFont}', sans-serif; color: ${bodyTextColor}; font-size: 0.9rem; font-style: italic; margin-top: 10px;">${block.image_caption}</p>` : ''}
                            </div>
                        `;
                    }
                }
            });
        } else {
            html += `<p style="color: #999; font-style: italic; text-align: center; margin-top: 50px;">No content yet</p>`;
        }
        
        html += `
                </div>
                
                <!-- Page Number -->
                <div style="position: absolute; bottom: 30px; left: 0; right: 0; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
                    <small style="color: #666; font-size: 0.9rem;">${index + 3}</small>
                </div>
            </div>
        `;
    });
    
    previewContainer.innerHTML = html;
}

// Add event listeners for real-time updates
document.addEventListener('DOMContentLoaded', function() {
    // Update preview on input changes
    const titleInput = document.getElementById('articleTitle');
    const categorySelect = document.getElementById('articleCategory');
    const teaserTextarea = document.getElementById('articleTeaser');
    
    if (titleInput) {
        titleInput.addEventListener('input', updateLivePreview);
    }
    if (categorySelect) {
        categorySelect.addEventListener('change', updateLivePreview);
    }
    if (teaserTextarea) {
        teaserTextarea.addEventListener('input', updateLivePreview);
    }
    
    // Update preview when cover background changes in settings
    const coverBackgroundInput = document.getElementById('configCoverBackground');
    if (coverBackgroundInput) {
        coverBackgroundInput.addEventListener('input', debounce(updateLivePreview, 500));
    }
    
    // Update preview when header position changes
    const headerPositionSelect = document.getElementById('configHeaderPosition');
    if (headerPositionSelect) {
        headerPositionSelect.addEventListener('change', updateLivePreview);
    }
    
    // Sidebar typography controls - instant preview
    const sidebarPrimaryFont = document.getElementById('sidebarPrimaryFont');
    const sidebarSecondaryFont = document.getElementById('sidebarSecondaryFont');
    const sidebarTextColor = document.getElementById('sidebarTextColor');
    const sidebarBodyTextColor = document.getElementById('sidebarBodyTextColor');
    
    if (sidebarPrimaryFont) {
        sidebarPrimaryFont.addEventListener('change', updateMagazineTypography);
    }
    if (sidebarSecondaryFont) {
        sidebarSecondaryFont.addEventListener('change', updateMagazineTypography);
    }
    if (sidebarTextColor) {
        sidebarTextColor.addEventListener('input', updateMagazineTypography);
    }
    if (sidebarBodyTextColor) {
        sidebarBodyTextColor.addEventListener('input', updateMagazineTypography);
    }
});

// Debounce helper function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Dark Mode Toggle
function toggleDarkMode() {
    const body = document.body;
    const icon = document.getElementById('darkModeIcon');
    
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Load dark mode preference on page load
document.addEventListener('DOMContentLoaded', function() {
    const darkMode = localStorage.getItem('darkMode');
    const icon = document.getElementById('darkModeIcon');
    
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
        if (icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
});
