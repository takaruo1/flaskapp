from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

def calculate_profit(data):
    try:
        width = float(data.get('width', 0))
        edge_width = float(data.get('edge_width', 12))
        weft_density1 = float(data.get('weft_density1', 0))
        weft_density2 = float(data.get('weft_density2', 0)) if 'weft_density2' in data else 0
        head_count = float(data.get('head_count', 0))
        warp_d = float(data.get('warp_d', 0))
        weft_d1 = float(data.get('weft_d1', 0))
        weft_d2 = float(data.get('weft_d2', 0)) if 'weft_d2' in data else 0
        warp_price = float(data.get('warp_price', 0))
        weft_price1 = float(data.get('weft_price1', 0))
        weft_price2 = float(data.get('weft_price2', 0)) if 'weft_price2' in data else 0
        machine_speed = float(data.get('machine_speed', 0))
        efficiency = float(data.get('efficiency', 92)) / 100
        shrinkage = float(data.get('shrinkage', 0))
        warping_cost = float(data.get('warping_cost', 0))
        invoice_price = data.get('invoice_price', None)

        if any(x < 0 for x in [width, weft_density1, head_count, warp_d, weft_d1, warp_price, weft_price1, machine_speed, warping_cost]):
            return {'error': '所有输入值必须为非负数'}
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
                return {'error': '开票价格必须为非负数'}
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
            result['warning'] = '日利润为负，建议调整开票价格或降低成本'
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
                            <div class="input-wrapper">
                                <input type="number" name="width" step="0.1" required>
                                <span class="icon icon-width"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>边幅 (厘米)</label>
                            <div class="input-wrapper">
                                <input type="number" name="edge_width" step="0.1" value="12" required>
                                <span class="icon icon-width"></span>
                            </div>
                        </div>
                    </fieldset>

                    <!-- 纱线参数 -->
                    <fieldset class="input-group-set">
                        <legend>纱线参数</legend>
                        <div class="input-group">
                            <label>头份 (根)</label>
                            <div class="input-wrapper">
                                <input type="number" name="head_count" required>
                                <span class="icon icon-head"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>经纱D数 (D)</label>
                            <div class="input-wrapper">
                                <input type="number" name="warp_d" step="0.1" required>
                                <span class="icon icon-warp"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>纬密1 (根/厘米)</label>
                            <div class="input-wrapper">
                                <input type="number" name="weft_density1" step="0.1" required>
                                <span class="icon icon-weft"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>纬纱D数1 (D)</label>
                            <div class="input-wrapper">
                                <input type="number" name="weft_d1" step="0.1" required>
                                <span class="icon icon-weft"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>经纱价格 (元/KG)</label>
                            <div class="input-wrapper">
                                <input type="number" name="warp_price" step="0.01" required>
                                <span class="icon icon-price"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>纬纱价格1 (元/KG)</label>
                            <div class="input-wrapper">
                                <input type="number" name="weft_price1" step="0.01" required>
                                <span class="icon icon-price"></span>
                            </div>
                        </div>
                        <div class="input-group toggle-group">
                            <label>使用第二纬纱</label>
                            <label class="switch">
                                <input type="checkbox" id="weft2-toggle" onchange="toggleWeft2()">
                                <span class="slider round"></span>
                            </label>
                        </div>
                        <div id="weft2-group">
                            <div class="input-group">
                                <label>纬密2 (根/厘米)</label>
                                <div class="input-wrapper">
                                    <input type="number" name="weft_density2" step="0.1" value="0">
                                    <span class="icon icon-weft"></span>
                                </div>
                            </div>
                            <div class="input-group">
                                <label>纬纱D数2 (D)</label>
                                <div class="input-wrapper">
                                    <input type="number" name="weft_d2" step="0.1" value="0">
                                    <span class="icon icon-weft"></span>
                                </div>
                            </div>
                            <div class="input-group">
                                <label>纬纱价格2 (元/KG)</label>
                                <div class="input-wrapper">
                                    <input type="number" name="weft_price2" step="0.01" value="0">
                                    <span class="icon icon-price"></span>
                                </div>
                            </div>
                        </div>
                    </fieldset>

                    <!-- 机器与成本 -->
                    <fieldset class="input-group-set">
                        <legend>机器与成本</legend>
                        <div class="input-group">
                            <label>车速 (转/分钟)</label>
                            <div class="input-wrapper">
                                <input type="number" name="machine_speed" step="0.1" required>
                                <span class="icon icon-speed"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>开机效率 (%) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <div class="input-wrapper">
                                    <input type="number" name="efficiency" step="0.1" value="92" required>
                                    <span class="icon icon-efficiency"></span>
                                </div>
                                <span class="tooltiptext">开机效率是指织机实际运行时间占总时间的百分比，默认值为92%，可根据实际情况调整。</span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>缩率 (%) <span class="question-mark">?</span></label>
                            <div class="input-with-tooltip">
                                <div class="input-wrapper">
                                    <input type="number" name="shrinkage" step="0.01" required>
                                    <span class="icon icon-shrinkage"></span>
                                </div>
                                <span class="tooltiptext">缩率：1 = 1% = ×1.01，3 = 3% = ×1.03，10 = 10% = ×1.1</span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>整经费用 (元)</label>
                            <div class="input-wrapper">
                                <input type="number" name="warping_cost" step="0.01" required>
                                <span class="icon icon-cost"></span>
                            </div>
                        </div>
                        <div class="input-group">
                            <label>开票价格 (元/米)</label>
                            <div class="input-wrapper">
                                <input type="number" name="invoice_price" step="0.01">
                                <span class="icon icon-invoice"></span>
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
                resultSection.innerHTML = `<h2>计算结果</h2><p style="color: #ff3b30;">错误：${data.error}</p>`;
                showFeedback('计算失败：' + data.error, 'error');
            } else {
                resultSection.innerHTML = `
                    <h2>计算结果 - ${fabricName}</h2>
                    <div class="result-card">
                        <span class="result-icon icon-warp"></span>
                        <span>经向克重: ${data.warp_weight} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-weft"></span>
                        <span>纬向克重 (纬纱1): ${data.weft_weight1} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-weft"></span>
                        <span>纬向克重 (纬纱2): ${data.weft_weight2} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-weft"></span>
                        <span>总纬向克重: ${data.weft_weight} 克</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-cost"></span>
                        <span>经纱成本: ${data.warp_cost} 元</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-cost"></span>
                        <span>纬纱成本: ${data.weft_cost} 元</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-price"></span>
                        <span>成本价: ${data.cost_price} 元/米</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-output"></span>
                        <span>日产量: ${data.daily_output} 米</span>
                    </div>
                    <div class="result-card">
                        <span class="result-icon icon-profit"></span>
                        <span>日利润: ${data.daily_profit !== null ? data.daily_profit + ' 元' : '未定义（需输入开票价格）'}</span>
                    </div>
                    ${data.warning ? `<p style="color: #ff9500; margin-top: 10px;">${data.warning}</p>` : ''}
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

            document.querySelectorAll('.question-mark').forEach(item => {
                item.addEventListener('mouseenter', () => {
                    const tooltip = item.closest('.input-group').querySelector('.tooltiptext');
                    tooltip.style.visibility = 'visible';
                    tooltip.style.opacity = '1';
                });
                item.addEventListener('mouseleave', () => {
                    const tooltip = item.closest('.input-group').querySelector('.tooltiptext');
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.opacity = '0';
                });
            });
        });
    </script>
</body>
</html>
"""

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
        <h1>历史记录</h1>
        <div class="history-section">
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
            <div id="history_table_container">
                <table id="history_table">
                    <thead>
                        <tr>
                            <th>布种名称</th>
                            <th>时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="history_tbody"></tbody>
                </table>
            </div>
            <button onclick="window.location.href='/'" class="back-btn">返回计算器</button>
        </div>
    </div>
    <script>
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
            }
        }

        function updateHistoryTable() {
            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');
            const tbody = document.getElementById('history_tbody');
            const search = document.getElementById('history_search').value.toLowerCase();
            const dateStart = document.getElementById('date_start').value;
            const dateEnd = document.getElementById('date_end').value;
            tbody.innerHTML = '';
            Object.keys(history)
                .filter(name => name.toLowerCase().includes(search))
                .filter(name => {
                    const timestamp = new Date(history[name].timestamp);
                    if (dateStart && timestamp < new Date(dateStart)) return false;
                    if (dateEnd && timestamp > new Date(dateEnd)) return false;
                    return true;
                })
                .sort((a, b) => new Date(history[b].timestamp) - new Date(history[a].timestamp))
                .forEach(fabricName => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td onclick="loadHistory('${fabricName}')">${fabricName}</td>
                        <td onclick="loadHistory('${fabricName}')">${history[fabricName].timestamp}</td>
                        <td><button class="delete-history-btn" onclick="deleteHistory('${fabricName}')">删除</button></td>
                    `;
                    tbody.appendChild(row);
                });
        }

        function filterHistory() {
            updateHistoryTable();
        }

        document.addEventListener('DOMContentLoaded', () => {
            updateHistoryTable();
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)