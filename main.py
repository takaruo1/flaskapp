from flask import Flask, request, render_template_string
from flask_caching import Cache
from flask_assets import Environment, Bundle

# 初始化 Flask 应用
app = Flask(__name__)

# 配置缓存
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

# 配置静态资源管理
app.config['ASSETS_DEBUG'] = False  # 生产环境设为 False，开发环境可设为 True
assets = Environment(app)
css = Bundle('css/style.css', output='gen/style.min.css', filters='cssmin')
assets.register('css_all', css)

# 路由
@cache.cached(timeout=300, forced_update=True)
@app.route('/', methods=['GET'])
def index():
    return render_template_string(CALCULATOR_HTML, result=None)

@cache.cached(timeout=300, forced_update=True)
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.form
    result = calculate_profit(data)
    return render_template_string(CALCULATOR_HTML, result=result)

# 保持 calculate_profit 和路由逻辑不变
# ...

CALCULATOR_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>纺织品价格计算器</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='gen/style.min.css') }}">
    <style>
        .loader {
            border: 8px solid #f3f3f3;
            border-top: 8px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
            display: none;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>纺织品价格计算器</h1>
    <div class="calculator">
        <div class="input-section">
            <form id="calcForm" method="post" action="/calculate">
                <div class="input-group">
                    <label>门幅 (厘米):</label>
                    <input type="number" name="width" step="0.1" required value="{{ width or '' }}">
                </div>
                <!-- 保持其他输入组相同 -->
                <div class="input-group">
                    <label>缩率:</label>
                    <div class="tooltip">
                        <input type="number" name="shrinkage" step="0.01" required value="{{ shrinkage or '' }}">
                        <span class="question-mark">?</span>
                        <span class="tooltiptext">缩率的含义：1 个缩率 = 1% = 乘以 1.01，3 个缩率 = 3% = 乘以 1.03，10 个缩率 = 10% = 乘以 1.1。请直接输入缩率数字（如 3，而不是 3%）。</span>
                    </div>
                </div>
                <div class="button-group">
                    <input type="submit" value="计算">
                    <button type="button" id="reset-button" onclick="resetForm()">清零</button>
                </div>
            </form>
            <div class="loader" id="loader"></div>
        </div>
        <div class="result-section">
            <h3>计算结果</h3>
            {% if result %}
                {% if result.error %}
                    <p style="color: red;">错误：{{ result.error }}</p>
                {% else %}
                    <table class="result-table">
                        <tr><th>项目</th><th>值</th></tr>
                        <tr><td>经向克重</td><td>{{ result.warp_weight }} 克</td></tr>
                        <tr><td>纬向克重</td><td>{{ result.weft_weight }} 克</td></tr>
                        <tr><td>经纱成本</td><td>{{ result.warp_cost }} 元</td></tr>
                        <tr><td>纬纱成本</td><td>{{ result.weft_cost }} 元</td></tr>
                        <tr><td>成本价</td><td>{{ result.cost_price }} 元/米</td></tr>
                        <tr><td>日产量</td><td>{{ result.daily_output }} 米</td></tr>
                        <tr><td>日利润</td><td>{{ result.daily_profit }} 元</td></tr>
                    </table>
                {% endif %}
            {% else %}
                <p>输入参数后点击“计算”查看结果！</p>
            {% endif %}
        </div>
    </div>
    <script>
        function resetForm() {
            document.getElementById('calcForm').reset();
            window.location.href = '/';
            localStorage.clear();
        }

        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('calcForm');
            const loader = document.getElementById('loader');
            const inputs = form.querySelectorAll('input[type="number"]');

            // 加载保存的输入
            inputs.forEach(input => {
                const savedValue = localStorage.getItem(input.name);
                if (savedValue) input.value = savedValue;
            });

            // 保存输入
            form.addEventListener('input', (e) => {
                localStorage.setItem(e.target.name, e.target.value);
            });

            // 处理表单提交并显示加载动画
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                loader.style.display = 'block';
                const formData = new FormData(form);
                fetch('/calculate', {
                    method: 'POST',
                    body: formData
                }).then(response => response.text())
                  .then(html => {
                      document.body.innerHTML = html;
                      loader.style.display = 'none';
                  }).catch(error => {
                      alert('计算失败，请重试');
                      loader.style.display = 'none';
                  });
            });
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)