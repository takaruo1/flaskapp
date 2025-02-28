from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# 嵌入计算器模板
CALCULATOR_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>纺织品价格计算器</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="flex justify-end mb-4">
            <button id="theme-toggle" class="theme-toggle-btn">切换模式</button>
        </div>
        <h1>纺织品价格计算器</h1>
        <div class="calculator">
            <div class="input-section">
                <form id="calcForm" method="post">
                    <!-- 布料参数 -->
                    <fieldset class="input-group-set">
                        <legend>布料参数</legend>
                        <div class="input-group">
                            <label>布种编号/名称</label>
                            <input type="text" name="fabric_name" id="fabric_name" required>
                        </div>
                        <div class="input-group">
                            <label>门幅 (厘米)</label>
                            <input type="number" name="width" step="0.1" required>
                        </div>
                        <div class="input-group">
                            <label>边幅 (厘米) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <input type="number" name="edge_width" step="0.1" value="12" required>
                                <span class="icon icon-width"></span>
                                <span class="tooltiptext">边幅默认值为 12 厘米，可根据实际情况调整。</span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>头份 (根)</label>
                            <input type="number" name="head_count" required>
                        </div>
                    </fieldset>

                    <!-- 经纱参数 -->
                    <fieldset class="input-group-set">
                        <legend>经纱参数</legend>
                        <div class="input-group">
                            <label>经纱D数 (D)</label>
                            <input type="number" name="warp_d" step="0.1" required>
                        </div>
                        <div class="input-group">
                            <label>经纱价格 (元/KG)</label>
                            <input type="number" name="warp_price" step="0.01" required>
                        </div>
                    </fieldset>

                    <!-- 纬纱参数 -->
                    <fieldset class="input-group-set">
                        <legend>纬纱参数</legend>
                        <div class="input-group">
                            <label>纬密 (根/厘米)</label>
                            <input type="number" name="weft_density1" step="0.1" required>
                        </div>
                        <div class="input-group">
                            <label>纬纱D数 (D)</label>
                            <input type="number" name="weft_d1" step="0.1" required>
                        </div>
                        <div class="input-group">
                            <label>纬纱价格 (元/KG)</label>
                            <input type="number" name="weft_price1" step="0.01" required>
                        </div>
                        <div class="input-group">
                            <label>使用第二纬纱</label>
                            <label class="switch">
                                <input type="checkbox" id="weft2-toggle" onchange="toggleWeft2()">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div id="weft2-group">
                            <div class="input-group">
                                <label>纬密 (根/厘米)</label>
                                <input type="number" name="weft_density2" step="0.1" value="0">
                            </div>
                            <div class="input-group">
                                <label>纬纱D数 (D)</label>
                                <input type="number" name="weft_d2" step="0.1" value="0">
                            </div>
                            <div class="input-group">
                                <label>纬纱价格 (元/KG)</label>
                                <input type="number" name="weft_price2" step="0.01" value="0">
                            </div>
                        </div>
                    </fieldset>

                    <!-- 机器与成本 -->
                    <fieldset class="input-group-set">
                        <legend>机器与成本</legend>
                        <div class="input-group">
                            <label>车速 (转/分钟)</label>
                            <input type="number" name="machine_speed" step="0.1" required>
                        </div>
                        <div class="input-group">
                            <label>开机效率 (%) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <input type="number" name="efficiency" step="0.1" value="92" required>
                                <span class="icon icon-efficiency"></span>
                                <span class="tooltiptext">开机效率是指织机实际运行时间占总时间的百分比，默认值为92%，可根据实际情况调整。</span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>缩率 (%) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <input type="number" name="shrinkage" step="0.01" required>
                                <span class="icon icon-shrinkage"></span>
                                <span class="tooltiptext">缩率：1 = 1% = ×1.01，3 = 3% = ×1.03，10 = 10% = ×1.1</span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>整经费用 (元)</label>
                            <input type="number" name="warping_cost" step="0.01" required>
                        </div>
                        <div class="input-group">
                            <label>开票定价 (元/米) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <input type="number" name="invoice_price" step="0.01">
                                <span class="icon icon-invoice"></span>
                                <span class="tooltiptext">开票定价用于计算单台机台的日利润，如不输入，可计算其他数据。</span>
                            </div>
                        </div>
                    </fieldset>

                    <div class="button-group">
                        <input type="submit" value="计算" class="submit-btn">
                        <button type="button" id="reset-button" onclick="resetForm()">清零</button>
                        <button type="button" onclick="window.location.href='/history'">查看历史记录</button>
                    </div>
                </form>
                <div class="loader" id="loader"><span>计算中...</span></div>
                <div id="feedback" class="feedback-message"></div>
            </div>
            <div class="result-section">
                <h2>计算结果</h2>
                <p>输入参数后点击“计算”查看结果！</p>
                <button id="save-button" style="display: none;" onclick="saveHistory()">保存记录</button>
                <button id="delete-button" style="display: none;" onclick="deleteHistory()">删除记录</button>
            </div>
        </div>
    </div>
    <script>
        // 深色模式切换
        const themeToggle = document.getElementById('theme-toggle');
        const body = document.body;

        function toggleTheme() {
            body.dataset.theme = body.dataset.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', body.dataset.theme);
        }

        // 加载用户保存的主题偏好
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.dataset.theme = savedTheme;

        themeToggle.addEventListener('click', toggleTheme);

        // 实时验证
        function validateInput(input) {
            const value = input.value;
            if (value < 0 || isNaN(value)) {
                input.style.borderColor = 'red';
                showFeedback('输入值必须为非负数', 'error');
                return false;
            } else {
                input.style.borderColor = '';
                return true;
            }
        }

        // 工具提示
        document.querySelectorAll('.question-mark').forEach(item => {
            const tooltip = item.closest('.input-group').querySelector('.tooltiptext');
            item.addEventListener('mouseenter', (e) => {
                const rect = item.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                const windowHeight = window.innerHeight;

                if (rect.top - tooltipRect.height < 0) {
                    tooltip.style.top = '20px';
                    tooltip.style.transform = 'translateX(-50%)';
                } else {
                    tooltip.style.top = '-50px';
                    tooltip.style.transform = 'translateX(-50%)';
                }

                tooltip.style.visibility = 'visible';
                tooltip.style.opacity = '1';
            });
            item.addEventListener('mouseleave', (e) => {
                tooltip.style.visibility = 'hidden';
                tooltip.style.opacity = '0';
            });
        });

        function toggleWeft2() {
            const weft2Group = document.getElementById('weft2-group');
            const toggle = document.getElementById('weft2-toggle');
            if (toggle.checked) {
                weft2Group.style.display = 'block';
            } else {
                weft2Group.style.display = 'none';
                document.querySelector('input[name="weft_density2"]').value = '0';
                document.querySelector('input[name="weft_d2"]').value = '0';
                document.querySelector('input[name="weft_price2"]').value = '0';
            }
        }

        function resetForm() {
            document.getElementById('calcForm').reset();
            document.getElementById('fabric_name').value = '';
            document.querySelector('input[name="efficiency"]').value = '92';
            document.querySelector('input[name="edge_width"]').value = '12';
            document.getElementById('weft2-group').style.display = 'none';
            document.getElementById('weft2-toggle').checked = false;
            document.querySelector('input[name="weft_density2"]').value = '0';
            document.querySelector('input[name="weft_d2"]').value = '0';
            document.querySelector('input[name="weft_price2"]').value = '0';
            localStorage.removeItem('current_fabric');
            document.querySelector('.result-section').innerHTML = '<h2>计算结果</h2><p>输入参数后点击“计算”查看结果！</p>';
            document.getElementById('save-button').style.display = 'none';
            document.getElementById('delete-button').style.display = 'none';
            showFeedback('表单已重置', 'success');
        }

        function saveHistory() {
            const fabricName = document.getElementById('fabric_name').value.trim();
            if (!fabricName) {
                showFeedback('请填写布种编号/名称', 'error');
                return;
            }
            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
            const inputs = {};
            const formData = new FormData(document.getElementById('calcForm'));
            formData.forEach((value, key) => {
                if (key !== 'fabric_name') inputs[key] = value;
            });
            const result = JSON.parse(localStorage.getItem('current_result') || '{}');
            history[fabricName] = {
                inputs: inputs,
                result: result,
                timestamp: new Date().toLocaleString()
            };
            localStorage.setItem('fabric_history', JSON.stringify(history));
            showFeedback('记录已保存', 'success');
        }

        function deleteHistory() {
            const fabricName = document.getElementById('fabric_name').value.trim();
            if (!fabricName) {
                showFeedback('请填写布种编号/名称', 'error');
                return;
            }
            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
            if (history[fabricName]) {
                delete history[fabricName];
                localStorage.setItem('fabric_history', JSON.stringify(history));
                resetForm();
                showFeedback('记录已删除', 'success');
            }
        }

        function loadHistoryFromStorage() {
            const selectedFabric = localStorage.getItem('selected_fabric');
            if (selectedFabric) {
                const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
                const record = history[selectedFabric];
                if (record) {
                    document.getElementById('fabric_name').value = selectedFabric;
                    const inputs = document.getElementById('calcForm').querySelectorAll('input[type="number"]');
                    inputs.forEach(input => {
                        input.value = record.inputs[input.name] || (input.name === 'efficiency' ? '92' : input.name === 'edge_width' ? '12' : input.name === 'weft_d2' || input.name === 'weft_price2' || input.name === 'weft_density2' ? '0' : '');
                    });
                    if (record.inputs.weft_d2 && parseFloat(record.inputs.weft_d2) > 0) {
                        document.getElementById('weft2-group').style.display = 'block';
                        document.getElementById('weft2-toggle').checked = true;
                    } else {
                        document.getElementById('weft2-group').style.display = 'none';
                        document.getElementById('weft2-toggle').checked = false;
                    }
                    displayResult(record.result, selectedFabric);
                }
                localStorage.removeItem('selected_fabric');
            }
        }

        function displayResult(data, fabricName) {
            const resultSection = document.querySelector('.result-section');
            if (data.error) {
                resultSection.innerHTML = `<h2>计算结果</h2><p style="color: red;">${data.error}</p>`;
                showFeedback('计算失败：' + data.error, 'error');
            } else {
                let profitStyle = 'color: var(--primary); font-weight: bold;';
                if (data.daily_profit !== null) {
                    if (data.daily_profit > 0) {
                        profitStyle = 'color: #4caf50; font-weight: bold;'; // 绿色表示正利润
                    } else if (data.daily_profit < 0) {
                        profitStyle = 'color: #f44336; font-weight: bold;'; // 红色表示负利润
                    } else {
                        profitStyle = 'color: #ff9800; font-weight: bold;'; // 黄色表示未定义或零
                    }
                }
                resultSection.innerHTML = `
                    <h2>计算结果 - ${fabricName}</h2>
                    <div class="result-card">
                        <span class="icon icon-warp"></span>
                        <span>经向克重: ${data.warp_weight} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-weft"></span>
                        <span>纬向克重: ${data.weft_weight1} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-weft"></span>
                        <span>第二纬向克重: ${data.weft_weight2} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-weft"></span>
                        <span>总纬向克重: ${data.weft_weight} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-cost"></span>
                        <span>经纱成本: ${data.warp_cost} 元</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-cost"></span>
                        <span>纬纱成本: ${data.weft_cost} 元</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-price"></span>
                        <span>成本价: ${data.cost_price} 元/米</span>
                    </div>
                    <div class="result-card">
                        <span class="icon icon-output"></span>
                        <span>日产量: ${data.daily_output} 米</span>
                    </div>
                    <div class="result-card" style="${profitStyle}">
                        <span class="icon icon-profit"></span>
                        <span>日利润: ${data.daily_profit !== null ? data.daily_profit + ' 元' : '未定义（需输入开票定价）'}</span>
                    </div>
                    ${data.warning ? `<p style="color: orange; margin-top: 10px;">${data.warning}</p>` : ''}
                    <button id="save-button" onclick="saveHistory()">保存记录</button>
                    <button id="delete-button" onclick="deleteHistory()">删除记录</button>`;
                showFeedback('计算完成', 'success');
            }
        }

        function showFeedback(message, type) {
            const feedback = document.getElementById('feedback');
            feedback.textContent = message;
            feedback.className = `feedback-message ${type}`;
            feedback.style.display = 'block';
            setTimeout(() => {
                feedback.style.display = 'none';
            }, 3000);
        }

        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('calcForm');
            const loader = document.getElementById('loader');

            loadHistoryFromStorage();

            form.querySelectorAll('input[type="number"]').forEach(input => {
                input.addEventListener('input', () => validateInput(input));
            });

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                loader.style.display = 'flex';
                const formData = new FormData(form);
                const fabricName = formData.get('fabric_name').trim();
                if (!fabricName) {
                    alert('请填写布种编号/名称');
                    loader.style.display = 'none';
                    return;
                }
                let isValid = true;
                form.querySelectorAll('input[type="number"]').forEach(input => {
                    if (!validateInput(input)) isValid = false;
                });
                if (!isValid) {
                    loader.style.display = 'none';
                    return;
                }
                fetch('/calculate', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                  .then(data => {
                      loader.style.display = 'none';
                      localStorage.setItem('current_result', JSON.stringify(data));
                      displayResult(data, fabricName);
                  }).catch(error => {
                      loader.style.display = 'none';
                      showFeedback('计算失败，请重试', 'error');
                  });
            });
        });
    </script>
</body>
</html>
"""

# 嵌入历史记录模板
HISTORY_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>历史记录</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="flex justify-end mb-4">
            <button id="theme-toggle" class="theme-toggle-btn">切换模式</button>
        </div>
        <h1>历史记录</h1>
        <div class="input-group">
            <label>搜索布种</label>
            <input type="text" id="history_search" placeholder="输入布种名称..." oninput="filterHistory()">
        </div>
        <div class="input-group">
            <label>日期范围</label>
            <input type="date" id="date_start" onchange="filterHistory()">
            <span>至</span>
            <input type="date" id="date_end" onchange="filterHistory()">
        </div>
        <div id="history_table_container" class="history-table-container">
            <table id="history_table">
                <thead>
                    <tr>
                        <th onclick="sortHistory('name')">布种名称</th>
                        <th onclick="sortHistory('timestamp')">时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="history_tbody"></tbody>
            </table>
        </div>
        <div class="button-group">
            <button class="back-btn" onclick="window.location.href='/'">返回计算器</button>
        </div>
    </div>
    <script>
        // 深色模式切换
        const themeToggle = document.getElementById('theme-toggle');
        const body = document.body;

        function toggleTheme() {
            body.dataset.theme = body.dataset.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', body.dataset.theme);
        }

        // 加载用户保存的主题偏好
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.dataset.theme = savedTheme;

        themeToggle.addEventListener('click', toggleTheme);

        let sortDirection = 1;
        let lastSortKey = 'timestamp';

        function loadHistory(fabricName) {
            localStorage.setItem('selected_fabric', fabricName);
            window.location.href = '/';
        }

        function deleteHistory(fabricName) {
            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
            if (history[fabricName]) {
                delete history[fabricName];
                localStorage.setItem('fabric_history', JSON.stringify(history));
                updateHistoryTable();
                showFeedback('记录已删除', 'success');
            }
        }

        function sortHistory(key) {
            if (lastSortKey === key) {
                sortDirection *= -1;
            } else {
                sortDirection = 1;
            }
            lastSortKey = key;
            updateHistoryTable();
        }

        function updateHistoryTable() {
            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
            const tbody = document.getElementById('history_tbody');
            const search = document.getElementById('history_search').value.toLowerCase();
            const dateStart = document.getElementById('date_start').value;
            const dateEnd = document.getElementById('date_end').value;
            tbody.innerHTML = '';
            const filteredHistory = Object.keys(history)
                .filter(name => name.toLowerCase().includes(search))
                .filter(name => {
                    const timestamp = new Date(history[name].timestamp);
                    if (dateStart && timestamp < new Date(dateStart)) return false;
                    if (dateEnd && timestamp > new Date(dateEnd)) return false;
                    return true;
                });
            filteredHistory.sort((a, b) => {
                const valueA = history[a][lastSortKey];
                const valueB = history[b][lastSortKey];
                if (lastSortKey === 'timestamp') {
                    return (new Date(valueA) - new Date(valueB)) * sortDirection;
                } else {
                    return valueA.localeCompare(valueB) * sortDirection;
                }
            });
            filteredHistory.forEach(fabricName => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td onclick="loadHistory('${fabricName}')">${fabricName}</td>
                    <td onclick="loadHistory('${fabricName}')">${history[fabricName].timestamp}</td>
                    <td><button class="delete-history-btn" onclick="deleteHistory('${fabricName}')">删除</button></td>
                `;
                tbody.appendChild(row);
            });
        }

        function showFeedback(message, type) {
            const feedback = document.createElement('div');
            feedback.textContent = message;
            feedback.className = `feedback-message ${type === 'success' ? 'success' : 'error'}`;
            feedback.style.background = type === 'success' ? '#6b8e23' : '#ff3b30';
            document.body.appendChild(feedback);
            setTimeout(() => {
                feedback.style.opacity = '0';
                setTimeout(() => feedback.remove(), 300);
            }, 3000);
        }

        document.addEventListener('DOMContentLoaded', () => {
            updateHistoryTable();
        });

        function filterHistory() {
            updateHistoryTable();
        }
    </script>
</body>
</html>
"""

# 嵌入 CSS 文件
STYLE_CSS = """
:root {
    --background: #ffffff;
    --text: #333333;
    --card-bg: #f5f5f5;
    --border: #d2d6dc;
    --primary: #6b8e23;
    --secondary: #556b2f;
    --error: #ff3b30;
    --warning: #ff9500;
    --input-bg: #ffffff;
    --input-border: #d2d6dc;
}

[data-theme="dark"] {
    --background: #1a202c;
    --text: #f7fafc;
    --card-bg: #2d3748;
    --border: #4a5568;
    --primary: #48bb78;
    --secondary: #38a169;
    --error: #e53e3e;
    --warning: #f6ad55;
    --input-bg: #4a5568;
    --input-border: #4a5568;
}

body {
    font-family: 'Inter', sans-serif;
    margin: 0;
    padding: 40px 20px;
    background: var(--background);
    color: var(--text);
    min-height: 100vh;
    transition: all 0.3s ease;
}

.flex {
    display: flex;
}

.justify-end {
    justify-content: flex-end;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    background: var(--card-bg);
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

h1 {
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    text-align: center;
    margin-bottom: 40px;
}

.calculator {
    display: flex;
    flex-direction: column;
    gap: 40px;
}

@media (min-width: 768px) {
    .calculator {
        flex-direction: row;
    }
    .input-section, .result-section {
        width: 50%;
    }
}

@media (max-width: 767px) {
    .calculator {
        padding: 20px;
    }
    .input-section, .result-section {
        width: 100%;
    }
}

.input-group-set {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    background: var(--card-bg);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.input-group-set legend {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    padding: 0 10px;
}

.input-group {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
}

label {
    width: 140px;
    text-align: right;
    font-size: 16px;
    font-weight: 400;
    color: var(--text);
}

input[type="number"], input[type="text"] {
    padding: 10px 30px 10px 10px;
    border: 1px solid var(--input-border);
    border-radius: 8px;
    font-size: 16px;
    width: 160px;
    box-sizing: border-box;
    background: var(--input-bg);
    color: var(--text);
    transition: border-color 0.2s, box-shadow 0.2s;
}

input[type="number"]:focus, input[type="text"]:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(107, 142, 35, 0.2);
    outline: none;
}

.icon {
    position: absolute;
    left: 10px;
    width: 16px;
    height: 16px;
    background-size: contain;
    background-repeat: no-repeat;
}

/* 注释掉 background-image 属性以避免 404 错误 */
/* 
.icon-width { background-image: url('../icons/width.svg'); }
.icon-weft { background-image: url('../icons/weft.svg'); }
.icon-head { background-image: url('../icons/head.svg'); }
.icon-warp { background-image: url('../icons/warp.svg'); }
.icon-price { background-image: url('../icons/price.svg'); }
.icon-speed { background-image: url('../icons/speed.svg'); }
.icon-efficiency { background-image: url('../icons/efficiency.svg'); }
.icon-shrinkage { background-image: url('../icons/shrinkage.svg'); }
.icon-cost { background-image: url('../icons/cost.svg'); }
.icon-invoice { background-image: url('../icons/invoice.svg'); }
.icon-output { background-image: url('../icons/output.svg'); }
.icon-profit { background-image: url('../icons/profit.svg'); }
*/

.question-mark {
    cursor: pointer;
    color: var(--primary);
    font-size: 14px;
    font-weight: 600;
    margin-left: 4px;
    vertical-align: middle;
}

.input-with-tooltip {
    position: relative;
    display: inline-block;
}

.tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: rgba(0, 0, 0, 0.85);
    color: #fff;
    text-align: center;
    padding: 8px 12px;
    border-radius: 8px;
    position: absolute;
    z-index: 1000;
    top: -50px;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s, visibility 0s linear 0.3s;
    font-size: 14px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.input-with-tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
    transition-delay: 0s;
}

#weft2-group {
    display: none;
    padding: 15px;
    border-radius: 8px;
    margin-top: 10px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.switch {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 20px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.slider:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input:checked + .slider {
    background-color: var(--primary);
}

input:checked + .slider:before {
    transform: translateX(20px);
}

.button-group {
    display: flex;
    justify-content: flex-end;
    gap: 20px;
    margin-top: 30px;
}

.submit-btn, #reset-button, #save-button, #delete-button, .back-btn {
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.1s, box-shadow 0.2s;
}

.submit-btn {
    background: var(--primary);
    color: #fff;
    box-shadow: 0 2px 5px rgba(107, 142, 35, 0.3);
}

.submit-btn:hover {
    background: var(--secondary);
    box-shadow: 0 4px 8px rgba(107, 142, 35, 0.4);
}

.submit-btn:active {
    transform: scale(0.95);
    box-shadow: 0 1px 3px rgba(107, 142, 35, 0.2);
}

#reset-button {
    background: none;
    color: var(--primary);
    border: 1px solid var(--primary);
    box-shadow: 0 2px 5px rgba(107, 142, 35, 0.1);
}

#reset-button:hover {
    background: rgba(107, 142, 35, 0.1);
    box-shadow: 0 4px 8px rgba(107, 142, 35, 0.2);
}

#save-button {
    background: var(--primary);
    color: #fff;
    box-shadow: 0 2px 5px rgba(107, 142, 35, 0.3);
}

#save-button:hover {
    background: var(--secondary);
    box-shadow: 0 4px 8px rgba(107, 142, 35, 0.4);
}

#delete-button {
    background: none;
    color: var(--error);
    border: 1px solid var(--error);
    box-shadow: 0 2px 5px rgba(255, 59, 48, 0.1);
}

#delete-button:hover {
    background: rgba(255, 59, 48, 0.1);
    box-shadow: 0 4px 8px rgba(255, 59, 48, 0.2);
}

.back-btn {
    background: var(--primary);
    color: #fff;
    box-shadow: 0 2px 5px rgba(107, 142, 35, 0.3);
}

.back-btn:hover {
    background: var(--secondary);
    box-shadow: 0 4px 8px rgba(107, 142, 35, 0.4);
}

.back-btn:active {
    transform: scale(0.95);
    box-shadow: 0 1px 3px rgba(107, 142, 35, 0.2);
}

.result-section h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 20px;
}

.result-card {
    background: var(--card-bg);
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 16px;
    color: var(--text);
    border: 1px solid var(--border);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: background 0.2s, box-shadow 0.2s;
}

.result-card:hover {
    background: var(--card-bg);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.loader {
    display: none;
    justify-content: center;
    align-items: center;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.9);
    padding: 12px 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    font-size: 14px;
    color: var(--primary);
    z-index: 1000;
}

.loader::before {
    content: '';
    width: 16px;
    height: 16px;
    border: 2px solid rgba(245, 245, 245, 0.9);
    border-top: 2px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.feedback-message {
    display: none;
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 14px;
    color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: opacity 0.3s, transform 0.3s;
    z-index: 1000;
}

.feedback-message.success {
    background: var(--primary);
}

.feedback-message.error {
    background: var(--error);
}

.theme-toggle-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 20px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    background: linear-gradient(45deg, #6b8e23, #556b2f);
    color: #fff;
    box-shadow: 0 2px 5px rgba(107, 142, 35, 0.3);
    transition: background 0.3s, transform 0.1s, box-shadow 0.2s;
}

.theme-toggle-btn:hover {
    background: linear-gradient(45deg, #556b2f, #486b2f);
    box-shadow: 0 4px 8px rgba(107, 142, 35, 0.4);
}

.theme-toggle-btn:active {
    transform: scale(0.95);
    box-shadow: 0 1px 3px rgba(107, 142, 35, 0.2);
}

.theme-toggle-btn.dark {
    background: linear-gradient(45deg, #48bb78, #38a169);
}

.theme-toggle-btn.dark:hover {
    background: linear-gradient(45deg, #38a169, #2d8b5f);
}

.history-table-container {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 20px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--card-bg);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

#history_table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

#history_table th, #history_table td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    transition: background 0.2s, box-shadow 0.2s;
}

#history_table th {
    background: var(--primary);
    color: #fff;
    cursor: pointer;
    position: sticky;
    top: 0;
    z-index: 10;
}

#history_table th:hover {
    background: var(--secondary);
}

#history_table td {
    cursor: pointer;
}

#history_table td:hover {
    background: rgba(107, 142, 35, 0.1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

#history_table tr:last-child td {
    border-bottom: none;
}

#history_search {
    padding: 10px;
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 10px;
    border: 1px solid var(--input-border);
    border-radius: 8px;
    background: var(--input-bg);
    color: var(--text);
    transition: border-color 0.2s, box-shadow 0.2s;
}

#history_search:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(107, 142, 35, 0.2);
    outline: none;
}

.delete-history-btn {
    padding: 6px 12px;
    border: 1px solid var(--error);
    border-radius: 8px;
    background: none;
    color: var(--error);
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s, box-shadow 0.2s;
}

.delete-history-btn:hover {
    background: rgba(255, 59, 48, 0.1);
    box-shadow: 0 2px 4px rgba(255, 59, 48, 0.2);
}
"""

# 计算逻辑保持不变
def calculate_profit(data):
    try:
        # 布料参数
        width = float(data.get('width', 0))
        edge_width = float(data.get('edge_width', 12))
        head_count = float(data.get('head_count', 0))  # 在布料参数中

        # 经纱参数
        warp_d = float(data.get('warp_d', 0))
        warp_price = float(data.get('warp_price', 0))

        # 纬纱1参数（默认必填）
        weft_density1 = float(data.get('weft_density1', 0))
        weft_d1 = float(data.get('weft_d1', 0))
        weft_price1 = float(data.get('weft_price1', 0))

        # 纬纱2参数（可选）
        weft_density2 = float(data.get('weft_density2', 0)) if 'weft_density2' in data else 0
        weft_d2 = float(data.get('weft_d2', 0)) if 'weft_d2' in data else 0
        weft_price2 = float(data.get('weft_price2', 0)) if 'weft_price2' in data else 0

        # 机器与成本参数
        machine_speed = float(data.get('machine_speed', 0))
        efficiency = float(data.get('efficiency', 92)) / 100
        shrinkage = float(data.get('shrinkage', 0))
        warping_cost = float(data.get('warping_cost', 0))
        invoice_price = data.get('invoice_price', None)

        # 验证输入
        if any(x < 0 for x in [width, head_count, warp_d, warp_price, weft_density1, weft_d1, weft_price1, machine_speed, warping_cost]):
            return {'error': '所有必填输入值必须为非负数'}
        if edge_width < 0:
            return {'error': '边幅必须为非负数'}
        if weft_density2 < 0 or (weft_d2 < 0 and weft_d2 != 0) or weft_price2 < 0:
            return {'error': '纬纱2参数必须为非负数'}
        if efficiency < 0 or efficiency > 1:
            return {'error': '开机效率必须在0-100%之间'}
        if shrinkage < -100:
            return {'error': '缩率不能小于 -100%'}

        total_weft_density = weft_density1 + weft_density2
        if total_weft_density <= 0:
            return {'error': '总纬密必须大于0'}

        # 计算
        warp_weight = head_count * warp_d / 9000
        weft_weight1 = weft_density1 * (width + edge_width) / 9000 * weft_d1
        weft_weight2 = weft_density2 * (width + edge_width) / 9000 * weft_d2 if weft_d2 > 0 else 0
        weft_weight = weft_weight1 + weft_weight2

        warp_cost = (warp_weight * (warp_price / 1000) + warping_cost) * (1 + shrinkage / 100)
        weft_cost = (weft_weight1 * (weft_price1 / 1000)) + (weft_weight2 * (weft_price2 / 1000))
        cost_price = warp_cost + weft_cost

        daily_output = machine_speed * 24 * 60 * efficiency / total_weft_density / 100

        daily_profit = None
        if invoice_price is not None and invoice_price.strip():
            invoice_price = float(invoice_price)
            if invoice_price < 0:
                return {'error': '开票定价必须为非负数'}
            daily_profit = (invoice_price - cost_price) * daily_output

        result = {
            'warp_weight': round(warp_weight, 2),
            'weft_weight1': round(weft_weight1, 2),
            'weft_weight2': round(weft_weight2, 2),
            'weft_weight': round(weft_weight, 2),
            'warp_cost': round(warp_cost, 2),
            'weft_cost': round(weft_cost, 2),
            'cost_price': round(cost_price, 2),
            'daily_output': round(daily_output, 2),
            'daily_profit': round(daily_profit, 2) if daily_profit is not None else None
        }
        if daily_profit is not None and daily_profit < 0:
            result['warning'] = '日利润为负，建议调整开票定价或降低成本'
        return result
    except Exception as e:
        return {'error': str(e)}

@app.route('/', methods=['GET'])
def index():
    return render_template_string(CALCULATOR_HTML)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.form
    result = calculate_profit(data)
    return jsonify(result)

@app.route('/history', methods=['GET'])
def history():
    return render_template_string(HISTORY_HTML)

# 创建静态目录和 CSS 文件
import os
if not os.path.exists('static'):
    os.makedirs('static/css')
with open('static/css/style.css', 'w') as f:
    f.write(STYLE_CSS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)