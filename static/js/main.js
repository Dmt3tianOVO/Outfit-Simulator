// 全局变量
let currentFilepath = null;
let currentContext = '休闲';
let currentStyles = {
    top: '',
    bottom: '',
    shoes: ''
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initUpload();
    initContextSelector();
    initAnalyze();
    initHistoryRefresh();
    loadHistory();
});

// ==================== 上传功能 ====================
function initUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // 点击上传区域
    uploadArea.addEventListener('click', () => fileInput.click());

    // 文件选择
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // 拖拽上传
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
}

function handleFileUpload(file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        showMessage('请上传图片文件！', 'error');
        return;
    }

    // 检查文件大小（16MB）
    if (file.size > 16 * 1024 * 1024) {
        showMessage('文件太大，最大支持16MB！', 'error');
        return;
    }

    // 上传文件
    const formData = new FormData();
    formData.append('file', file);

    showLoading();

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            currentFilepath = data.filepath;
            document.getElementById('analyzeBtn').disabled = false;
            
            // 更新上传区域显示
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.innerHTML = `
                <div class="upload-preview">
                    <img src="${data.url}" alt="预览">
                    <button class="btn-remove" id="removeBtn">×</button>
                </div>
            `;
            
            // 绑定移除按钮
            document.getElementById('removeBtn').addEventListener('click', function(e) {
                e.stopPropagation();
                resetUploadArea();
            });
            
            showMessage('上传成功：' + data.filename, 'success');
        } else {
            showMessage('上传失败：' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showMessage('上传失败：' + error.message, 'error');
    });
}

function resetUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.innerHTML = `
        <div class="upload-placeholder" id="uploadPlaceholder">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <p class="upload-text">点击上传图片</p>
            <p class="upload-hint">支持 PNG, JPG, GIF, BMP 格式</p>
        </div>
    `;
    
    fileInput.value = '';
    currentFilepath = null;
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('resultsSection').style.display = 'none';
}

// ==================== 场景选择 ====================
function initContextSelector() {
    const contextBtns = document.querySelectorAll('.context-btn');
    
    contextBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            contextBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentContext = this.getAttribute('data-context');
            
            // 根据场景自动填充款式建议
            autoFillStyles(currentContext);
        });
    });
    
    // 初始化款式选择器
    initStyleSelector();
}

function autoFillStyles(context) {
    // 根据场景自动填充款式建议
    const styleMap = {
        '休闲': { top: 'T恤', bottom: '牛仔裤', shoes: '运动鞋' },
        '工作': { top: '衬衫', bottom: '休闲裤', shoes: '皮鞋' },
        '正式场合': { top: '衬衫', bottom: '休闲裤', shoes: '皮鞋' },
        '运动': { top: 'T恤', bottom: '运动裤', shoes: '运动鞋' }
    };
    
    const styles = styleMap[context] || styleMap['休闲'];
    
    // 更新选择器
    document.getElementById('topStyle').value = styles.top;
    document.getElementById('bottomStyle').value = styles.bottom;
    document.getElementById('shoeStyle').value = styles.shoes;
    
    // 更新全局变量
    currentStyles = {
        top: styles.top,
        bottom: styles.bottom,
        shoes: styles.shoes
    };
}

function initStyleSelector() {
    const topStyle = document.getElementById('topStyle');
    const bottomStyle = document.getElementById('bottomStyle');
    const shoeStyle = document.getElementById('shoeStyle');
    
    [topStyle, bottomStyle, shoeStyle].forEach(select => {
        select.addEventListener('change', function() {
            currentStyles.top = topStyle.value;
            currentStyles.bottom = bottomStyle.value;
            currentStyles.shoes = shoeStyle.value;
        });
    });
}

// ==================== 分析功能 ====================
function initAnalyze() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const reanalyzeBtn = document.getElementById('reanalyzeBtn');
    
    analyzeBtn.addEventListener('click', performAnalysis);
    reanalyzeBtn.addEventListener('click', performAnalysis);
}

function performAnalysis() {
    if (!currentFilepath) {
        showMessage('请先上传图片！', 'error');
        return;
    }

    showLoading();
    
    // 构建款式对象，只包含非空值
    const styles = {};
    if (currentStyles.top) styles.top = currentStyles.top;
    if (currentStyles.bottom) styles.bottom = currentStyles.bottom;
    if (currentStyles.shoes) styles.shoes = currentStyles.shoes;
    
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filepath: currentFilepath,
            context: { type: currentContext },
            styles: Object.keys(styles).length > 0 ? styles : null
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            displayAnalysisResult(data);
            loadHistory();
        } else {
            showMessage('分析失败：' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showMessage('分析失败：' + error.message, 'error');
    });
}

function displayAnalysisResult(data) {
    // 显示结果区域
    document.getElementById('resultsSection').style.display = 'block';
    
    // 显示评分
    const score = data.rule_evaluation ? data.rule_evaluation.score : 
                  (data.color_evaluation ? data.color_evaluation.score : 0);
    displayScore(score);
    
    // 显示颜色分析
    displayColors(data.colors, data.color_evaluation);
    
    // 显示款式识别
    if (data.style_predictions && data.style_predictions.length > 0) {
        displayStyles(data.style_predictions);
    }
    
    // 显示规则评估
    if (data.rule_evaluation) {
        displayRules(data.rule_evaluation);
    }
    
    // 显示建议
    displaySuggestions(data);
    
    // 滚动到结果区域
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function displayScore(score) {
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreStatus = document.getElementById('scoreStatus');
    
    scoreValue.textContent = Math.round(score);
    
    // 更新样式
    scoreCircle.className = 'score-circle';
    if (score >= 80) {
        scoreCircle.classList.add('score-high');
        scoreStatus.textContent = '搭配优秀';
        scoreStatus.className = 'score-status status-good';
    } else if (score >= 60) {
        scoreCircle.classList.add('score-medium');
        scoreStatus.textContent = '搭配良好';
        scoreStatus.className = 'score-status status-ok';
    } else {
        scoreCircle.classList.add('score-low');
        scoreStatus.textContent = '需要改进';
        scoreStatus.className = 'score-status status-bad';
    }
}

function displayColors(colors, evaluation) {
    const colorsGrid = document.getElementById('colorsGrid');
    colorsGrid.innerHTML = '';
    
    colors.forEach(color => {
        const colorItem = document.createElement('div');
        colorItem.className = 'color-item';
        colorItem.innerHTML = `
            <div class="color-swatch" style="background-color: rgb(${color.rgb[0]}, ${color.rgb[1]}, ${color.rgb[2]})"></div>
            <div class="color-info">
                <div class="color-name">${color.name}</div>
                <div class="color-percent">${color.percentage}%</div>
                <div class="color-tone">${color.tone}</div>
            </div>
        `;
        colorsGrid.appendChild(colorItem);
    });
    
    // 显示颜色评估建议
    if (evaluation && evaluation.suggestions) {
        const colorEval = document.getElementById('colorEvaluation');
        colorEval.innerHTML = '';
        
        evaluation.suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            colorEval.appendChild(item);
        });
    }
}

function displayStyles(predictions) {
    const styleCard = document.getElementById('styleCard');
    const styleList = document.getElementById('styleList');
    
    styleCard.style.display = 'block';
    styleList.innerHTML = '';
    
    predictions.forEach(pred => {
        const item = document.createElement('div');
        item.className = 'style-item';
        item.innerHTML = `
            <span class="style-name">${pred.class}</span>
            <span class="style-confidence">${(pred.confidence * 100).toFixed(1)}%</span>
        `;
        styleList.appendChild(item);
    });
}

function displayRules(ruleEvaluation) {
    const ruleCard = document.getElementById('ruleCard');
    const rulesList = document.getElementById('rulesList');
    
    ruleCard.style.display = 'block';
    rulesList.innerHTML = '';
    
    ruleEvaluation.results.forEach(rule => {
        const item = document.createElement('div');
        item.className = 'rule-item ' + (rule.passed ? 'passed' : 'failed');
        item.innerHTML = `
            <div class="rule-header">
                <span class="rule-name">${rule.rule_name}</span>
                <span class="rule-score">${rule.score.toFixed(1)}分</span>
            </div>
            <div class="rule-message">${rule.message}</div>
        `;
        rulesList.appendChild(item);
    });
}

function displaySuggestions(data) {
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    
    const suggestions = [];
    
    // 收集颜色建议
    if (data.color_evaluation && data.color_evaluation.suggestions) {
        data.color_evaluation.suggestions.forEach(s => {
            suggestions.push({ text: s, severity: 'info' });
        });
    }
    
    // 收集规则建议
    if (data.rule_evaluation && data.rule_evaluation.suggestions) {
        data.rule_evaluation.suggestions.forEach(s => {
            suggestions.push({ text: s.suggestion, severity: s.severity });
        });
    }
    
    if (suggestions.length === 0) {
        const item = document.createElement('li');
        item.className = 'suggestion-item';
        item.textContent = '搭配很好，无需改进！';
        suggestionsList.appendChild(item);
    } else {
        suggestions.forEach(s => {
            const item = document.createElement('li');
            item.className = 'suggestion-item severity-' + s.severity;
            item.textContent = s.text;
            suggestionsList.appendChild(item);
        });
    }
}

// ==================== 历史记录 ====================
function initHistoryRefresh() {
    const refreshBtn = document.getElementById('refreshHistoryBtn');
    refreshBtn.addEventListener('click', loadHistory);
}

function loadHistory() {
    const historyGrid = document.getElementById('historyGrid');
    
    fetch('/wardrobe')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayHistory(data.images);
            } else {
                historyGrid.innerHTML = '<p class="empty-state">加载失败</p>';
            }
        })
        .catch(error => {
            historyGrid.innerHTML = '<p class="empty-state">加载失败</p>';
        });
}

function displayHistory(images) {
    const historyGrid = document.getElementById('historyGrid');
    
    if (images.length === 0) {
        historyGrid.innerHTML = '<p class="empty-state">暂无历史记录</p>';
        return;
    }
    
    historyGrid.innerHTML = '';
    images.forEach(image => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <img src="${image.url}" alt="${image.filename}">
            <div class="history-overlay">
                <button class="btn-view">查看</button>
            </div>
        `;
        
        item.addEventListener('click', function() {
            currentFilepath = image.url.replace('/images/uploads/', 'static/images/uploads/');
            
            // 更新上传区域
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.innerHTML = `
                <div class="upload-preview">
                    <img src="${image.url}" alt="预览">
                    <button class="btn-remove" id="removeBtn">×</button>
                </div>
            `;
            
            document.getElementById('removeBtn').addEventListener('click', function(e) {
                e.stopPropagation();
                resetUploadArea();
            });
            
            document.getElementById('analyzeBtn').disabled = false;
            
            // 滚动到上传区域
            document.querySelector('.upload-section').scrollIntoView({ behavior: 'smooth' });
        });
        
        historyGrid.appendChild(item);
    });
}

// ==================== 工具函数 ====================
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showMessage(text, type = 'info') {
    // 简单的消息提示（可以改进为更好的UI）
    console.log(`[${type.toUpperCase()}] ${text}`);
}
