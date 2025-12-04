// ==================== 配置 ====================
// 从 localStorage 读取 API 地址，如果没有则使用默认值
let API_BASE_URL = localStorage.getItem('apiBaseUrl') || '';

// 全局变量
let currentFilepath = null;
let currentContext = '休闲';
let currentStyles = {
    top: '',
    bottom: '',
    shoes: ''
};

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    initApiConfig();
    initUpload();
    initSceneSelector();
    initStyleSelector();
    initAnalyze();
    
    // 如果没有配置 API，显示提示
    if (!API_BASE_URL) {
        showMessage('请先配置后端 API 地址', 'error');
    }
});

// ==================== API 配置 ====================
function initApiConfig() {
    const apiInput = document.getElementById('apiUrl');
    const saveBtn = document.getElementById('saveApiBtn');
    
    // 加载保存的 API 地址
    if (API_BASE_URL) {
        apiInput.value = API_BASE_URL;
    }
    
    // 保存 API 地址
    saveBtn.addEventListener('click', function() {
        const url = apiInput.value.trim();
        if (!url) {
            showMessage('请输入 API 地址', 'error');
            return;
        }
        
        // 移除末尾的斜杠
        API_BASE_URL = url.replace(/\/$/, '');
        localStorage.setItem('apiBaseUrl', API_BASE_URL);
        showMessage('API 地址已保存', 'success');
    });
}

// ==================== 上传功能 ====================
function initUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // 点击上传
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

async function handleFileUpload(file) {
    // 检查 API 配置
    if (!API_BASE_URL) {
        showMessage('请先配置后端 API 地址', 'error');
        return;
    }
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        showMessage('请上传图片文件', 'error');
        return;
    }

    // 检查文件大小（16MB）
    if (file.size > 16 * 1024 * 1024) {
        showMessage('文件太大，最大支持 16MB', 'error');
        return;
    }

    // 上传文件
    const formData = new FormData();
    formData.append('file', file);

    showLoading('上传中...');

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            currentFilepath = data.filepath;
            
            // 显示预览
            const imagePreview = document.getElementById('imagePreview');
            const previewImage = document.getElementById('previewImage');
            
            previewImage.src = `${API_BASE_URL}${data.url}`;
            imagePreview.style.display = 'block';
            
            // 隐藏上传区域
            document.getElementById('uploadArea').style.display = 'none';
            
            // 启用分析按钮
            document.getElementById('analyzeBtn').disabled = false;
            
            showMessage('上传成功', 'success');
        } else {
            showMessage('上传失败: ' + data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('上传失败: ' + error.message, 'error');
    }
}

// ==================== 场景选择 ====================
function initSceneSelector() {
    const sceneBtns = document.querySelectorAll('.scene-btn');
    
    sceneBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            sceneBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentContext = this.getAttribute('data-scene');
            
            // 自动填充款式
            autoFillStyles(currentContext);
        });
    });
}

function autoFillStyles(context) {
    const styleMap = {
        '休闲': { top: 'T恤', bottom: '牛仔裤', shoes: '运动鞋' },
        '工作': { top: '衬衫', bottom: '休闲裤', shoes: '皮鞋' },
        '正式场合': { top: '衬衫', bottom: '休闲裤', shoes: '皮鞋' },
        '运动': { top: 'T恤', bottom: '运动裤', shoes: '运动鞋' }
    };
    
    const styles = styleMap[context] || styleMap['休闲'];
    
    document.getElementById('topStyle').value = styles.top;
    document.getElementById('bottomStyle').value = styles.bottom;
    document.getElementById('shoesStyle').value = styles.shoes;
    
    currentStyles = { ...styles };
}

// ==================== 款式选择 ====================
function initStyleSelector() {
    const topStyle = document.getElementById('topStyle');
    const bottomStyle = document.getElementById('bottomStyle');
    const shoesStyle = document.getElementById('shoesStyle');
    
    [topStyle, bottomStyle, shoesStyle].forEach(select => {
        select.addEventListener('change', function() {
            currentStyles.top = topStyle.value;
            currentStyles.bottom = bottomStyle.value;
            currentStyles.shoes = shoesStyle.value;
        });
    });
}

// ==================== 分析功能 ====================
function initAnalyze() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.addEventListener('click', performAnalysis);
}

async function performAnalysis() {
    if (!API_BASE_URL) {
        showMessage('请先配置后端 API 地址', 'error');
        return;
    }
    
    if (!currentFilepath) {
        showMessage('请先上传图片', 'error');
        return;
    }

    showLoading('分析中...');
    
    // 构建款式对象
    const styles = {};
    if (currentStyles.top) styles.top = currentStyles.top;
    if (currentStyles.bottom) styles.bottom = currentStyles.bottom;
    if (currentStyles.shoes) styles.shoes = currentStyles.shoes;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filepath: currentFilepath,
                context: { type: currentContext },
                styles: Object.keys(styles).length > 0 ? styles : null
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            displayAnalysisResult(data);
        } else {
            showMessage('分析失败: ' + data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('分析失败: ' + error.message, 'error');
    }
}

function displayAnalysisResult(data) {
    // 显示结果区域
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';
    
    // 显示评分
    const score = data.rule_evaluation ? data.rule_evaluation.score : 
                  (data.color_evaluation ? data.color_evaluation.score : 0);
    displayScore(score);
    
    // 显示颜色分析
    displayColors(data.colors);
    
    // 显示规则评估
    if (data.rule_evaluation) {
        displayRules(data.rule_evaluation);
    }
    
    // 显示建议
    displaySuggestions(data);
    
    // 滚动到结果
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function displayScore(score) {
    const scoreValue = document.getElementById('scoreValue');
    scoreValue.textContent = Math.round(score);
}

function displayColors(colors) {
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
}

function displayRules(ruleEvaluation) {
    const rulesList = document.getElementById('rulesList');
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
            suggestions.push(s);
        });
    }
    
    // 收集规则建议
    if (data.rule_evaluation && data.rule_evaluation.suggestions) {
        data.rule_evaluation.suggestions.forEach(s => {
            suggestions.push(s.suggestion);
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
            item.className = 'suggestion-item';
            item.textContent = s;
            suggestionsList.appendChild(item);
        });
    }
}

// ==================== 工具函数 ====================
function showLoading(text = '加载中...') {
    const loading = document.createElement('div');
    loading.id = 'loadingOverlay';
    loading.className = 'loading';
    loading.innerHTML = `
        <div class="spinner"></div>
        <p>${text}</p>
    `;
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loadingOverlay');
    if (loading) {
        loading.remove();
    }
}

function showMessage(text, type = 'info') {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = 'message ' + type;
    message.classList.add('show');
    
    setTimeout(() => {
        message.classList.remove('show');
    }, 3000);
}
