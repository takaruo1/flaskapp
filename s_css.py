[1mdiff --git a/generated-icon.png b/generated-icon.png[m
[1mdeleted file mode 100644[m
[1mindex 758f350..0000000[m
Binary files a/generated-icon.png and /dev/null differ
[1mdiff --git a/main.py b/main.py[m
[1mindex 7dd849f..68e65ca 100644[m
[1m--- a/main.py[m
[1m+++ b/main.py[m
[36m@@ -1,36 +1,89 @@[m
[31m-from flask import Flask, request, render_template_string[m
[31m-from flask_caching import Cache[m
[31m-from flask_assets import Environment, Bundle[m
[32m+[m[32mfrom flask import Flask, request, render_template_string, jsonify[m
 [m
[31m-# 初始化 Flask 应用[m
 app = Flask(__name__)[m
 [m
[31m-# 配置缓存[m
[31m-app.config['CACHE_TYPE'] = 'simple'[m
[31m-app.config['CACHE_DEFAULT_TIMEOUT'] = 300[m
[31m-cache = Cache(app)[m
[32m+[m[32mdef calculate_profit(data):[m
[32m+[m[32m    try:[m
[32m+[m[32m        width = float(data.get('width', 0))[m
[32m+[m[32m        edge_width = float(data.get('edge_width', 12))[m
[32m+[m[32m        weft_density1 = float(data.get('weft_density1', 0))[m
[32m+[m[32m        weft_density2 = float(data.get('weft_density2', 0)) if 'weft_density2' in data else 0[m
[32m+[m[32m        head_count = float(data.get('head_count', 0))[m
[32m+[m[32m        warp_d = float(data.get('warp_d', 0))[m
[32m+[m[32m        weft_d1 = float(data.get('weft_d1', 0))[m
[32m+[m[32m        weft_d2 = float(data.get('weft_d2', 0)) if 'weft_d2' in data else 0[m
[32m+[m[32m        warp_price = float(data.get('warp_price', 0))[m
[32m+[m[32m        weft_price1 = float(data.get('weft_price1', 0))[m
[32m+[m[32m        weft_price2 = float(data.get('weft_price2', 0)) if 'weft_price2' in data else 0[m
[32m+[m[32m        machine_speed = float(data.get('machine_speed', 0))[m
[32m+[m[32m        efficiency = float(data.get('efficiency', 92)) / 100[m
[32m+[m[32m        shrinkage = float(data.get('shrinkage', 0))[m
[32m+[m[32m        warping_cost = float(data.get('warping_cost', 0))[m
[32m+[m[32m        invoice_price = data.get('invoice_price', None)[m
 [m
[31m-# 配置静态资源管理[m
[31m-app.config['ASSETS_DEBUG'] = False  # 生产环境设为 False，开发环境可设为 True[m
[31m-assets = Environment(app)[m
[31m-css = Bundle('css/style.css', output='gen/style.min.css', filters='cssmin')[m
[31m-assets.register('css_all', css)[m
[32m+[m[32m        if any(x < 0 for x in [width, weft_density1, head_count, warp_d, weft_d1, warp_price, weft_price1, machine_speed, warping_cost]):[m
[32m+[m[32m            return {'error': '所有输入值必须为非负数'}[m
[32m+[m[32m        if edge_width < 0:[m
[32m+[m[32m            return {'error': '边幅必须为非负数'}[m
[32m+[m[32m        if weft_density2 < 0 or (weft_d2 < 0 and weft_d2 != 0) or weft_price2 < 0:[m
[32m+[m[32m            return {'error': '纬纱2参数必须为非负数'}[m
[32m+[m[32m        if efficiency < 0 or efficiency > 1:[m
[32m+[m[32m            return {'error': '开机效率必须在0-100%之间'}[m
[32m+[m[32m        if shrinkage < -100:[m
[32m+[m[32m            return {'error': '缩率不能小于 -100%'}[m
[32m+[m
[32m+[m[32m        total_weft_density = weft_density1 + weft_density2[m
[32m+[m[32m        if total_weft_density <= 0:[m
[32m+[m[32m            return {'error': '总纬密必须大于0'}[m
[32m+[m
[32m+[m[32m        warp_weight = head_count * warp_d / 9000[m
[32m+[m[32m        weft_weight1 = weft_density1 * (width + edge_width) / 9000 * weft_d1[m
[32m+[m[32m        weft_weight2 = weft_density2 * (width + edge_width) / 9000 * weft_d2 if weft_d2 > 0 else 0[m
[32m+[m[32m        weft_weight = weft_weight1 + weft_weight2[m
[32m+[m
[32m+[m[32m        warp_cost = (warp_weight * (warp_price / 1000) + warping_cost) * (1 + shrinkage / 100)[m
[32m+[m[32m        weft_cost = (weft_weight1 * (weft_price1 / 1000)) + (weft_weight2 * (weft_price2 / 1000))[m
[32m+[m[32m        cost_price = warp_cost + weft_cost[m
[32m+[m
[32m+[m[32m        daily_output = machine_speed * 24 * 60 * efficiency / total_weft_density / 100[m
[32m+[m
[32m+[m[32m        daily_profit = None[m
[32m+[m[32m        if invoice_price is not None and invoice_price.strip():[m
[32m+[m[32m            invoice_price = float(invoice_price)[m
[32m+[m[32m            if invoice_price < 0:[m
[32m+[m[32m                return {'error': '开票价格必须为非负数'}[m
[32m+[m[32m            daily_profit = (invoice_price - cost_price) * daily_output[m
[32m+[m
[32m+[m[32m        result = {[m
[32m+[m[32m            'warp_weight': round(warp_weight, 2),[m
[32m+[m[32m            'weft_weight1': round(weft_weight1, 2),[m
[32m+[m[32m            'weft_weight2': round(weft_weight2, 2),[m
[32m+[m[32m            'weft_weight': round(weft_weight, 2),[m
[32m+[m[32m            'warp_cost': round(warp_cost, 2),[m
[32m+[m[32m            'weft_cost': round(weft_cost, 2),[m
[32m+[m[32m            'cost_price': round(cost_price, 2),[m
[32m+[m[32m            'daily_output': round(daily_output, 2),[m
[32m+[m[32m            'daily_profit': round(daily_profit, 2) if daily_profit is not None else None[m
[32m+[m[32m        }[m
[32m+[m[32m        if daily_profit is not None and daily_profit < 0:[m
[32m+[m[32m            result['warning'] = '日利润为负，建议调整开票价格或降低成本'[m
[32m+[m[32m        return result[m
[32m+[m[32m    except Exception as e:[m
[32m+[m[32m        return {'error': str(e)}[m
 [m
[31m-# 路由[m
[31m-@cache.cached(timeout=300, forced_update=True)[m
 @app.route('/', methods=['GET'])[m
 def index():[m
[31m-    return render_template_string(CALCULATOR_HTML, result=None)[m
[32m+[m[32m    return render_template_string(CALCULATOR_HTML)[m
 [m
[31m-@cache.cached(timeout=300, forced_update=True)[m
 @app.route('/calculate', methods=['POST'])[m
 def calculate():[m
     data = request.form[m
     result = calculate_profit(data)[m
[31m-    return render_template_string(CALCULATOR_HTML, result=result)[m
[32m+[m[32m    return jsonify(result)[m
 [m
[31m-# 保持 calculate_profit 和路由逻辑不变[m
[31m-# ...[m
[32m+[m[32m@app.route('/history', methods=['GET'])[m
[32m+[m[32mdef history():[m
[32m+[m[32m    return render_template_string(HISTORY_HTML)[m
 [m
 CALCULATOR_HTML = """[m
 <!DOCTYPE html>[m
[36m@@ -39,112 +92,464 @@[m [mCALCULATOR_HTML = """[m
     <meta charset="UTF-8">[m
     <meta name="viewport" content="width=device-width, initial-scale=1.0">[m
     <title>纺织品价格计算器</title>[m
[31m-    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">[m
[31m-    <link rel="stylesheet" href="{{ url_for('static', filename='gen/style.min.css') }}">[m
[31m-    <style>[m
[31m-        .loader {[m
[31m-            border: 8px solid #f3f3f3;[m
[31m-            border-top: 8px solid #3498db;[m
[31m-            border-radius: 50%;[m
[31m-            width: 30px;[m
[31m-            height: 30px;[m
[31m-            animation: spin 1s linear infinite;[m
[31m-            margin: 20px auto;[m
[31m-            display: none;[m
[31m-        }[m
[31m-        @keyframes spin {[m
[31m-            0% { transform: rotate(0deg); }[m
[31m-            100% { transform: rotate(360deg); }[m
[31m-        }[m
[31m-    </style>[m
[32m+[m[32m    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">[m
[32m+[m[32m    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">[m
 </head>[m
 <body>[m
[31m-    <h1>纺织品价格计算器</h1>[m
[31m-    <div class="calculator">[m
[31m-        <div class="input-section">[m
[31m-            <form id="calcForm" method="post" action="/calculate">[m
[31m-                <div class="input-group">[m
[31m-                    <label>门幅 (厘米):</label>[m
[31m-                    <input type="number" name="width" step="0.1" required value="{{ width or '' }}">[m
[31m-                </div>[m
[31m-                <!-- 保持其他输入组相同 -->[m
[31m-                <div class="input-group">[m
[31m-                    <label>缩率:</label>[m
[31m-                    <div class="tooltip">[m
[31m-                        <input type="number" name="shrinkage" step="0.01" required value="{{ shrinkage or '' }}">[m
[31m-                        <span class="question-mark">?</span>[m
[31m-                        <span class="tooltiptext">缩率的含义：1 个缩率 = 1% = 乘以 1.01，3 个缩率 = 3% = 乘以 1.03，10 个缩率 = 10% = 乘以 1.1。请直接输入缩率数字（如 3，而不是 3%）。</span>[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <h1>纺织品价格计算器</h1>[m
[32m+[m[32m        <div class="calculator">[m
[32m+[m[32m            <div class="input-section">[m
[32m+[m[32m                <form id="calcForm" method="post">[m
[32m+[m[32m                    <!-- 布料参数 -->[m
[32m+[m[32m                    <fieldset class="input-group-set">[m
[32m+[m[32m                        <legend>布料参数</legend>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>布种编号/名称</label>[m
[32m+[m[32m                            <input type="text" name="fabric_name" id="fabric_name" required>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>门幅 (厘米)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="width" step="0.1" required>[m
[32m+[m[32m                                <span class="icon icon-width"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>边幅 (厘米)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="edge_width" step="0.1" value="12" required>[m
[32m+[m[32m                                <span class="icon icon-width"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </fieldset>[m
[32m+[m
[32m+[m[32m                    <!-- 纱线参数 -->[m
[32m+[m[32m                    <fieldset class="input-group-set">[m
[32m+[m[32m                        <legend>纱线参数</legend>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>头份 (根)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="head_count" required>[m
[32m+[m[32m                                <span class="icon icon-head"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>经纱D数 (D)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="warp_d" step="0.1" required>[m
[32m+[m[32m                                <span class="icon icon-warp"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>纬密1 (根/厘米)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="weft_density1" step="0.1" required>[m
[32m+[m[32m                                <span class="icon icon-weft"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>纬纱D数1 (D)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="weft_d1" step="0.1" required>[m
[32m+[m[32m                                <span class="icon icon-weft"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>经纱价格 (元/KG)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="warp_price" step="0.01" required>[m
[32m+[m[32m                                <span class="icon icon-price"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>纬纱价格1 (元/KG)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="weft_price1" step="0.01" required>[m
[32m+[m[32m                                <span class="icon icon-price"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group toggle-group">[m
[32m+[m[32m                            <label>使用第二纬纱</label>[m
[32m+[m[32m                            <label class="switch">[m
[32m+[m[32m                                <input type="checkbox" id="weft2-toggle" onchange="toggleWeft2()">[m
[32m+[m[32m                                <span class="slider round"></span>[m
[32m+[m[32m                            </label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div id="weft2-group">[m
[32m+[m[32m                            <div class="input-group">[m
[32m+[m[32m                                <label>纬密2 (根/厘米)</label>[m
[32m+[m[32m                                <div class="input-wrapper">[m
[32m+[m[32m                                    <input type="number" name="weft_density2" step="0.1" value="0">[m
[32m+[m[32m                                    <span class="icon icon-weft"></span>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <div class="input-group">[m
[32m+[m[32m                                <label>纬纱D数2 (D)</label>[m
[32m+[m[32m                                <div class="input-wrapper">[m
[32m+[m[32m                                    <input type="number" name="weft_d2" step="0.1" value="0">[m
[32m+[m[32m                                    <span class="icon icon-weft"></span>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <div class="input-group">[m
[32m+[m[32m                                <label>纬纱价格2 (元/KG)</label>[m
[32m+[m[32m                                <div class="input-wrapper">[m
[32m+[m[32m                                    <input type="number" name="weft_price2" step="0.01" value="0">[m
[32m+[m[32m                                    <span class="icon icon-price"></span>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </fieldset>[m
[32m+[m
[32m+[m[32m                    <!-- 机器与成本 -->[m
[32m+[m[32m                    <fieldset class="input-group-set">[m
[32m+[m[32m                        <legend>机器与成本</legend>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>车速 (转/分钟)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="machine_speed" step="0.1" required>[m
[32m+[m[32m                                <span class="icon icon-speed"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>开机效率 (%) <span class="question-mark">?</span></label>[m
[32m+[m[32m                            <div class="input-with-tooltip">[m
[32m+[m[32m                                <div class="input-wrapper">[m
[32m+[m[32m                                    <input type="number" name="efficiency" step="0.1" value="92" required>[m
[32m+[m[32m                                    <span class="icon icon-efficiency"></span>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                                <span class="tooltiptext">开机效率是指织机实际运行时间占总时间的百分比，默认值为92%，可根据实际情况调整。</span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>缩率 (%) <span class="question-mark">?</span></label>[m
[32m+[m[32m                            <div class="input-with-tooltip">[m
[32m+[m[32m                                <div class="input-wrapper">[m
[32m+[m[32m                                    <input type="number" name="shrinkage" step="0.01" required>[m
[32m+[m[32m                                    <span class="icon icon-shrinkage"></span>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                                <span class="tooltiptext">缩率：1 = 1% = ×1.01，3 = 3% = ×1.03，10 = 10% = ×1.1</span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>整经费用 (元)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="warping_cost" step="0.01" required>[m
[32m+[m[32m                                <span class="icon icon-cost"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="input-group">[m
[32m+[m[32m                            <label>开票价格 (元/米)</label>[m
[32m+[m[32m                            <div class="input-wrapper">[m
[32m+[m[32m                                <input type="number" name="invoice_price" step="0.01">[m
[32m+[m[32m                                <span class="icon icon-invoice"></span>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </fieldset>[m
[32m+[m
[32m+[m[32m                    <div class="button-group">[m
[32m+[m[32m                        <input type="submit" value="计算" class="submit-btn">[m
[32m+[m[32m                        <button type="button" id="reset-button" onclick="resetForm()">清零</button>[m
[32m+[m[32m                        <button type="button" onclick="window.location.href='/history'">查看历史记录</button>[m
                     </div>[m
[31m-                </div>[m
[31m-                <div class="button-group">[m
[31m-                    <input type="submit" value="计算">[m
[31m-                    <button type="button" id="reset-button" onclick="resetForm()">清零</button>[m
[31m-                </div>[m
[31m-            </form>[m
[31m-            <div class="loader" id="loader"></div>[m
[31m-        </div>[m
[31m-        <div class="result-section">[m
[31m-            <h3>计算结果</h3>[m
[31m-            {% if result %}[m
[31m-                {% if result.error %}[m
[31m-                    <p style="color: red;">错误：{{ result.error }}</p>[m
[31m-                {% else %}[m
[31m-                    <table class="result-table">[m
[31m-                        <tr><th>项目</th><th>值</th></tr>[m
[31m-                        <tr><td>经向克重</td><td>{{ result.warp_weight }} 克</td></tr>[m
[31m-                        <tr><td>纬向克重</td><td>{{ result.weft_weight }} 克</td></tr>[m
[31m-                        <tr><td>经纱成本</td><td>{{ result.warp_cost }} 元</td></tr>[m
[31m-                        <tr><td>纬纱成本</td><td>{{ result.weft_cost }} 元</td></tr>[m
[31m-                        <tr><td>成本价</td><td>{{ result.cost_price }} 元/米</td></tr>[m
[31m-                        <tr><td>日产量</td><td>{{ result.daily_output }} 米</td></tr>[m
[31m-                        <tr><td>日利润</td><td>{{ result.daily_profit }} 元</td></tr>[m
[31m-                    </table>[m
[31m-                {% endif %}[m
[31m-            {% else %}[m
[32m+[m[32m                </form>[m
[32m+[m[32m                <div class="loader" id="loader"><span>计算中...</span></div>[m
[32m+[m[32m                <div id="feedback" class="feedback-message"></div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="result-section">[m
[32m+[m[32m                <h2>计算结果</h2>[m
                 <p>输入参数后点击“计算”查看结果！</p>[m
[31m-            {% endif %}[m
[32m+[m[32m                <button id="save-button" style="display: none;" onclick="saveHistory()">保存记录</button>[m
[32m+[m[32m                <button id="delete-button" style="display: none;" onclick="deleteHistory()">删除记录</button>[m
[32m+[m[32m            </div>[m
         </div>[m
     </div>[m
     <script>[m
[32m+[m[32m        function toggleWeft2() {[m
[32m+[m[32m            const weft2Group = document.getElementById('weft2-group');[m
[32m+[m[32m            const toggle = document.getElementById('weft2-toggle');[m
[32m+[m[32m            if (toggle.checked) {[m
[32m+[m[32m                weft2Group.style.display = 'block';[m
[32m+[m[32m            } else {[m
[32m+[m[32m                weft2Group.style.display = 'none';[m
[32m+[m[32m                document.querySelector('input[name="weft_density2"]').value = '0';[m
[32m+[m[32m                document.querySelector('input[name="weft_d2"]').value = '0';[m
[32m+[m[32m                document.querySelector('input[name="weft_price2"]').value = '0';[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
         function resetForm() {[m
             document.getElementById('calcForm').reset();[m
[31m-            window.location.href = '/';[m
[31m-            localStorage.clear();[m
[32m+[m[32m            document.getElementById('fabric_name').value = '';[m
[32m+[m[32m            document.querySelector('input[name="efficiency"]').value = '92';[m
[32m+[m[32m            document.querySelector('input[name="edge_width"]').value = '12';[m
[32m+[m[32m            document.getElementById('weft2-group').style.display = 'none';[m
[32m+[m[32m            document.getElementById('weft2-toggle').checked = false;[m
[32m+[m[32m            document.querySelector('input[name="weft_density2"]').value = '0';[m
[32m+[m[32m            document.querySelector('input[name="weft_d2"]').value = '0';[m
[32m+[m[32m            document.querySelector('input[name="weft_price2"]').value = '0';[m
[32m+[m[32m            localStorage.removeItem('current_fabric');[m
[32m+[m[32m            document.querySelector('.result-section').innerHTML = '<h2>计算结果</h2><p>输入参数后点击“计算”查看结果！</p>';[m
[32m+[m[32m            showFeedback('表单已重置', 'success');[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function saveHistory() {[m
[32m+[m[32m            const fabricName = document.getElementById('fabric_name').value.trim();[m
[32m+[m[32m            if (!fabricName) {[m
[32m+[m[32m                showFeedback('请填写布种编号/名称', 'error');[m
[32m+[m[32m                return;[m
[32m+[m[32m            }[m
[32m+[m[32m            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');[m
[32m+[m[32m            const inputs = {};[m
[32m+[m[32m            const formData = new FormData(document.getElementById('calcForm'));[m
[32m+[m[32m            formData.forEach((value, key) => {[m
[32m+[m[32m                if (key !== 'fabric_name') inputs[key] = value;[m
[32m+[m[32m            });[m
[32m+[m[32m            const result = JSON.parse(localStorage.getItem('current_result') || '{}');[m
[32m+[m[32m            history[fabricName] = {[m
[32m+[m[32m                inputs: inputs,[m
[32m+[m[32m                result: result,[m
[32m+[m[32m                timestamp: new Date().toLocaleString()[m
[32m+[m[32m            };[m
[32m+[m[32m            localStorage.setItem('fabric_history', JSON.stringify(history));[m
[32m+[m[32m            showFeedback('记录已保存', 'success');[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function deleteHistory() {[m
[32m+[m[32m            const fabricName = document.getElementById('fabric_name').value.trim();[m
[32m+[m[32m            if (!fabricName) {[m
[32m+[m[32m                showFeedback('请填写布种编号/名称', 'error');[m
[32m+[m[32m                return;[m
[32m+[m[32m            }[m
[32m+[m[32m            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');[m
[32m+[m[32m            if (history[fabricName]) {[m
[32m+[m[32m                delete history[fabricName];[m
[32m+[m[32m                localStorage.setItem('fabric_history', JSON.stringify(history));[m
[32m+[m[32m                resetForm();[m
[32m+[m[32m                showFeedback('记录已删除', 'success');[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function loadHistoryFromStorage() {[m
[32m+[m[32m            const selectedFabric = localStorage.getItem('selected_fabric');[m
[32m+[m[32m            if (selectedFabric) {[m
[32m+[m[32m                const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');[m
[32m+[m[32m                const record = history[selectedFabric];[m
[32m+[m[32m                if (record) {[m
[32m+[m[32m                    document.getElementById('fabric_name').value = selectedFabric;[m
[32m+[m[32m                    const inputs = document.getElementById('calcForm').querySelectorAll('input[type="number"]');[m
[32m+[m[32m                    inputs.forEach(input => {[m
[32m+[m[32m                        input.value = record.inputs[input.name] || (input.name === 'efficiency' ? '92' : input.name === 'edge_width' ? '12' : input.name === 'weft_d2' || input.name === 'weft_price2' || input.name === 'weft_density2' ? '0' : '');[m
[32m+[m[32m                    });[m
[32m+[m[32m                    if (record.inputs.weft_d2 && parseFloat(record.inputs.weft_d2) > 0) {[m
[32m+[m[32m                        document.getElementById('weft2-group').style.display = 'block';[m
[32m+[m[32m                        document.getElementById('weft2-toggle').checked = true;[m
[32m+[m[32m                    } else {[m
[32m+[m[32m                        document.getElementById('weft2-group').style.display = 'none';[m
[32m+[m[32m                        document.getElementById('weft2-toggle').checked = false;[m
[32m+[m[32m                    }[m
[32m+[m[32m                    displayResult(record.result, selectedFabric);[m
[32m+[m[32m                }[m
[32m+[m[32m                localStorage.removeItem('selected_fabric');[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function displayResult(data, fabricName) {[m
[32m+[m[32m            const resultSection = document.querySelector('.result-section');[m
[32m+[m[32m            if (data.error) {[m
[32m+[m[32m                resultSection.innerHTML = `<h2>计算结果</h2><p style="color: #ff3b30;">错误：${data.error}</p>`;[m
[32m+[m[32m                showFeedback('计算失败：' + data.error, 'error');[m
[32m+[m[32m            } else {[m
[32m+[m[32m                resultSection.innerHTML = `[m
[32m+[m[32m                    <h2>计算结果 - ${fabricName}</h2>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-warp"></span>[m
[32m+[m[32m                        <span>经向克重: ${data.warp_weight} 克</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-weft"></span>[m
[32m+[m[32m                        <span>纬向克重 (纬纱1): ${data.weft_weight1} 克</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-weft"></span>[m
[32m+[m[32m                        <span>纬向克重 (纬纱2): ${data.weft_weight2} 克</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-weft"></span>[m
[32m+[m[32m                        <span>总纬向克重: ${data.weft_weight} 克</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-cost"></span>[m
[32m+[m[32m                        <span>经纱成本: ${data.warp_cost} 元</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-cost"></span>[m
[32m+[m[32m                        <span>纬纱成本: ${data.weft_cost} 元</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-price"></span>[m
[32m+[m[32m                        <span>成本价: ${data.cost_price} 元/米</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-output"></span>[m
[32m+[m[32m                        <span>日产量: ${data.daily_output} 米</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <div class="result-card">[m
[32m+[m[32m                        <span class="result-icon icon-profit"></span>[m
[32m+[m[32m                        <span>日利润: ${data.daily_profit !== null ? data.daily_profit + ' 元' : '未定义（需输入开票价格）'}</span>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    ${data.warning ? `<p style="color: #ff9500; margin-top: 10px;">${data.warning}</p>` : ''}[m
[32m+[m[32m                    <button id="save-button" onclick="saveHistory()">保存记录</button>[m
[32m+[m[32m                    <button id="delete-button" onclick="deleteHistory()">删除记录</button>`;[m
[32m+[m[32m                showFeedback('计算完成', 'success');[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function showFeedback(message, type) {[m
[32m+[m[32m            const feedback = document.getElementById('feedback');[m
[32m+[m[32m            feedback.textContent = message;[m
[32m+[m[32m            feedback.className = `feedback-message ${type}`;[m
[32m+[m[32m            feedback.style.display = 'block';[m
[32m+[m[32m            setTimeout(() => {[m
[32m+[m[32m                feedback.style.display = 'none';[m
[32m+[m[32m            }, 3000);[m
         }[m
 [m
         document.addEventListener('DOMContentLoaded', () => {[m
             const form = document.getElementById('calcForm');[m
             const loader = document.getElementById('loader');[m
[31m-            const inputs = form.querySelectorAll('input[type="number"]');[m
 [m
[31m-            // 加载保存的输入[m
[31m-            inputs.forEach(input => {[m
[31m-                const savedValue = localStorage.getItem(input.name);[m
[31m-                if (savedValue) input.value = savedValue;[m
[31m-            });[m
[31m-[m
[31m-            // 保存输入[m
[31m-            form.addEventListener('input', (e) => {[m
[31m-                localStorage.setItem(e.target.name, e.target.value);[m
[31m-            });[m
[32m+[m[32m            loadHistoryFromStorage();[m
 [m
[31m-            // 处理表单提交并显示加载动画[m
             form.addEventListener('submit', (e) => {[m
                 e.preventDefault();[m
[31m-                loader.style.display = 'block';[m
[32m+[m[32m                loader.style.display = 'flex';[m
                 const formData = new FormData(form);[m
[32m+[m[32m                const fabricName = formData.get('fabric_name').trim();[m
[32m+[m[32m                if (!fabricName) {[m
[32m+[m[32m                    alert('请填写布种编号/名称');[m
[32m+[m[32m                    loader.style.display = 'none';[m
[32m+[m[32m                    return;[m
[32m+[m[32m                }[m
                 fetch('/calculate', {[m
                     method: 'POST',[m
                     body: formData[m
[31m-                }).then(response => response.text())[m
[31m-                  .then(html => {[m
[31m-                      document.body.innerHTML = html;[m
[32m+[m[32m                }).then(response => response.json())[m
[32m+[m[32m                  .then(data => {[m
                       loader.style.display = 'none';[m
[32m+[m[32m                      localStorage.setItem('current_result', JSON.stringify(data));[m
[32m+[m[32m                      displayResult(data, fabricName);[m
                   }).catch(error => {[m
[31m-                      alert('计算失败，请重试');[m
                       loader.style.display = 'none';[m
[32m+[m[32m                      showFeedback('计算失败，请重试', 'error');[m
                   });[m
             });[m
[32m+[m
[32m+[m[32m            document.querySelectorAll('.question-mark').forEach(item => {[m
[32m+[m[32m                item.addEventListener('mouseenter', () => {[m
[32m+[m[32m                    const tooltip = item.closest('.input-group').querySelector('.tooltiptext');[m
[32m+[m[32m                    tooltip.style.visibility = 'visible';[m
[32m+[m[32m                    tooltip.style.opacity = '1';[m
[32m+[m[32m                });[m
[32m+[m[32m                item.addEventListener('mouseleave', () => {[m
[32m+[m[32m                    const tooltip = item.closest('.input-group').querySelector('.tooltiptext');[m
[32m+[m[32m                    tooltip.style.visibility = 'hidden';[m
[32m+[m[32m                    tooltip.style.opacity = '0';[m
[32m+[m[32m                });[m
[32m+[m[32m            });[m
[32m+[m[32m        });[m
[32m+[m[32m    </script>[m
[32m+[m[32m</body>[m
[32m+[m[32m</html>[m
[32m+[m[32m"""[m
[32m+[m
[32m+[m[32mHISTORY_HTML = """[m
[32m+[m[32m<!DOCTYPE html>[m
[32m+[m[32m<html lang="zh">[m
[32m+[m[32m<head>[m
[32m+[m[32m    <meta charset="UTF-8">[m
[32m+[m[32m    <meta name="viewport" content="width=device-width, initial-scale=1.0">[m
[32m+[m[32m    <title>历史记录</title>[m
[32m+[m[32m    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">[m
[32m+[m[32m    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">[m
[32m+[m[32m</head>[m
[32m+[m[32m<body>[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <h1>历史记录</h1>[m
[32m+[m[32m        <div class="history-section">[m
[32m+[m[32m            <div class="input-group">[m
[32m+[m[32m                <label>搜索布种</label>[m
[32m+[m[32m                <input type="text" id="history_search" placeholder="输入布种名称..." oninput="filterHistory()">[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="input-group">[m
[32m+[m[32m                <label>日期范围</label>[m
[32m+[m[32m                <input type="date" id="date_start" onchange="filterHistory()">[m
[32m+[m[32m                <span>至</span>[m
[32m+[m[32m                <input type="date" id="date_end" onchange="filterHistory()">[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div id="history_table_container">[m
[32m+[m[32m                <table id="history_table">[m
[32m+[m[32m                    <thead>[m
[32m+[m[32m                        <tr>[m
[32m+[m[32m                            <th>布种名称</th>[m
[32m+[m[32m                            <th>时间</th>[m
[32m+[m[32m                            <th>操作</th>[m
[32m+[m[32m                        </tr>[m
[32m+[m[32m                    </thead>[m
[32m+[m[32m                    <tbody id="history_tbody"></tbody>[m
[32m+[m[32m                </table>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <button onclick="window.location.href='/'" class="back-btn">返回计算器</button>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m    <script>[m
[32m+[m[32m        function loadHistory(fabricName) {[m
[32m+[m[32m            localStorage.setItem('selected_fabric', fabricName);[m
[32m+[m[32m            window.location.href = '/';[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function deleteHistory(fabricName) {[m
[32m+[m[32m            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');[m
[32m+[m[32m            if (history[fabricName]) {[m
[32m+[m[32m                delete history[fabricName];[m
[32m+[m[32m                localStorage.setItem('fabric_history', JSON.stringify(history));[m
[32m+[m[32m                updateHistoryTable();[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function updateHistoryTable() {[m
[32m+[m[32m            const history = JSON.parse(localStorage.getItem('fabric_history') || '{}');[m
[32m+[m[32m            const tbody = document.getElementById('history_tbody');[m
[32m+[m[32m            const search = document.getElementById('history_search').value.toLowerCase();[m
[32m+[m[32m            const dateStart = document.getElementById('date_start').value;[m
[32m+[m[32m            const dateEnd = document.getElementById('date_end').value;[m
[32m+[m[32m            tbody.innerHTML = '';[m
[32m+[m[32m            Object.keys(history)[m
[32m+[m[32m                .filter(name => name.toLowerCase().includes(search))[m
[32m+[m[32m                .filter(name => {[m
[32m+[m[32m                    const timestamp = new Date(history[name].timestamp);[m
[32m+[m[32m                    if (dateStart && timestamp < new Date(dateStart)) return false;[m
[32m+[m[32m                    if (dateEnd && timestamp > new Date(dateEnd)) return false;[m
[32m+[m[32m                    return true;[m
[32m+[m[32m                })[m
[32m+[m[32m                .sort((a, b) => new Date(history[b].timestamp) - new Date(history[a].timestamp))[m
[32m+[m[32m                .forEach(fabricName => {[m
[32m+[m[32m                    const row = document.createElement('tr');[m
[32m+[m[32m                    row.innerHTML = `[m
[32m+[m[32m                        <td onclick="loadHistory('${fabricName}')">${fabricName}</td>[m
[32m+[m[32m                        <td onclick="loadHistory('${fabricName}')">${history[fabricName].timestamp}</td>[m
[32m+[m[32m                        <td><button class="delete-history-btn" onclick="deleteHistory('${fabricName}')">删除</button></td>[m
[32m+[m[32m                    `;[m
[32m+[m[32m                    tbody.appendChild(row);[m
[32m+[m[32m                });[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function filterHistory() {[m
[32m+[m[32m            updateHistoryTable();[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        document.addEventListener('DOMContentLoaded', () => {[m
[32m+[m[32m            updateHistoryTable();[m
         });[m
     </script>[m
 </body>[m
[36m@@ -152,4 +557,4 @@[m [mCALCULATOR_HTML = """[m
 """[m
 [m
 if __name__ == '__main__':[m
[31m-    app.run(host='0.0.0.0', port=8080)[m
\ No newline at end of file[m
[32m+[m[32m    app.run(host='0.0.0.0', port=8080, debug=True)[m
\ No newline at end of file[m
[1mdiff --git a/pyproject.toml b/pyproject.toml[m
[1mindex 6eee0f0..87b7b50 100644[m
[1m--- a/pyproject.toml[m
[1m+++ b/pyproject.toml[m
[36m@@ -8,4 +8,5 @@[m [mdependencies = [[m
     "flask-caching>=2.3.1",[m
     "flask>=3.1.0",[m
     "flask-assets>=2.1.0",[m
[32m+[m[32m    "cssmin>=0.2.0",[m
 ][m
[1mdiff --git a/static/css/style.css b/static/css/style.css[m
[1mindex 33b230e..274faa3 100644[m
[1m--- a/static/css/style.css[m
[1m+++ b/static/css/style.css[m
[36m@@ -1,185 +1,451 @@[m
 body {[m
[31m-    font-family: 'Roboto', sans-serif;[m
[31m-    margin: 0;[m
[31m-    padding: 20px;[m
[31m-    background: linear-gradient(135deg, #ff6b6b, #4ecdc4);[m
[31m-    color: #333;[m
[31m-    min-height: 100vh;[m
[31m-}[m
[31m-.calculator {[m
[31m-    background: #333;[m
[31m-    padding: 20px;[m
[31m-    border-radius: 20px;[m
[31m-    box-shadow: 0 10px 20px rgba(0,0,0,0.3);[m
[31m-    max-width: 900px;[m
[31m-    width: 100%;[m
[31m-    margin: 0 auto;[m
[31m-    display: flex;[m
[31m-    flex-direction: column;[m
[31m-    gap: 20px;[m
[32m+[m[32m  font-family: 'Inter', sans-serif;[m
[32m+[m[32m  margin: 0;[m
[32m+[m[32m  padding: 40px 20px;[m
[32m+[m[32m  background: linear-gradient(to bottom, #F5F5DC, #E6E6C4);[m
[32m+[m[32m  color: #333333;[m
[32m+[m[32m  min-height: 100vh;[m
 }[m
[31m-.input-section, .result-section {[m
[31m-    background: #fff;[m
[31m-    padding: 20px;[m
[31m-    border-radius: 15px;[m
[31m-    box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);[m
[31m-}[m
[31m-@media (min-width: 600px) {[m
[31m-    .calculator {[m
[31m-        flex-direction: row;[m
[31m-    }[m
[31m-    .input-section, .result-section {[m
[31m-        width: 400px;[m
[31m-    }[m
[31m-}[m
[31m-@media (max-width: 600px) {[m
[31m-    .input-section, .result-section {[m
[31m-        width: 100%;[m
[31m-    }[m
[32m+[m
[32m+[m[32m.container {[m
[32m+[m[32m  max-width: 1000px;[m
[32m+[m[32m  margin: 0 auto;[m
[32m+[m[32m  background: rgba(255, 255, 255, 0.9);[m
[32m+[m[32m  padding: 30px;[m
[32m+[m[32m  border-radius: 20px;[m
[32m+[m[32m  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);[m
[32m+[m[32m  position: relative;[m
[32m+[m[32m  overflow: hidden;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.container::before {[m
[32m+[m[32m  content: '';[m
[32m+[m[32m  position: absolute;[m
[32m+[m[32m  top: 0;[m
[32m+[m[32m  left: 0;[m
[32m+[m[32m  width: 100%;[m
[32m+[m[32m  height: 100%;[m
[32m+[m[32m  background: url('data:image/svg+xml,%3Csvg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M0 10h20M10 0v20" stroke="%23D2D6DC" stroke-width="1" opacity="0.2"/%3E%3C/svg%3E') repeat;[m
[32m+[m[32m  opacity: 0.1;[m
[32m+[m[32m  z-index: -1;[m
 }[m
[32m+[m
 h1 {[m
[31m-    color: #fff;[m
[31m-    text-align: center;[m
[31m-    margin-bottom: 20px;[m
[31m-    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);[m
[32m+[m[32m  font-size: 28px;[m
[32m+[m[32m  font-weight: 700;[m
[32m+[m[32m  color: #333333;[m
[32m+[m[32m  text-align: center;[m
[32m+[m[32m  margin-bottom: 40px;[m
 }[m
[31m-.input-group {[m
[31m-    display: flex;[m
[31m-    align-items: center;[m
[31m-    gap: 8px;[m
[32m+[m
[32m+[m[32m.calculator, .history-section {[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  flex-direction: column;[m
[32m+[m[32m  gap: 40px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.input-section, .result-section {[m
[32m+[m[32m  background: none;[m
[32m+[m[32m  padding: 0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m@media (min-width: 768px) {[m
[32m+[m[32m  .calculator {[m
[32m+[m[32m      flex-direction: row;[m
[32m+[m[32m  }[m
[32m+[m[32m  .input-section {[m
[32m+[m[32m      width: 50%;[m
[32m+[m[32m  }[m
[32m+[m[32m  .result-section {[m
[32m+[m[32m      width: 50%;[m
[32m+[m[32m  }[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m@media (max-width: 767px) {[m
[32m+[m[32m  .calculator, .history-section {[m
[32m+[m[32m      padding: 20px;[m
[32m+[m[32m  }[m
[32m+[m[32m  .input-section, .result-section {[m
[32m+[m[32m      width: 100%;[m
[32m+[m[32m  }[m
 }[m
[31m-form {[m
[31m-    display: flex;[m
[31m-    flex-direction: column;[m
[31m-    gap: 12px;[m
[32m+[m
[32m+[m[32m.input-group-set {[m
[32m+[m[32m  border: 1px solid #D2D6DC;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  padding: 15px;[m
[32m+[m[32m  margin-bottom: 20px;[m
[32m+[m[32m  background: rgba(245, 247, 249, 0.5);[m
 }[m
[32m+[m
[32m+[m[32m.input-group-set legend {[m
[32m+[m[32m  font-size: 16px;[m
[32m+[m[32m  font-weight: 600;[m
[32m+[m[32m  color: #1C2526;[m
[32m+[m[32m  padding: 0 10px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.input-group {[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  align-items: center;[m
[32m+[m[32m  gap: 20px;[m
[32m+[m[32m  margin-bottom: 20px;[m
[32m+[m[32m}[m
[32m+[m
 label {[m
[31m-    font-weight: 700;[m
[31m-    color: #2c3e50;[m
[31m-    font-size: 14px;[m
[31m-}[m
[31m-input[type="number"] {[m
[31m-    padding: 8px;[m
[31m-    border: 2px solid #ddd;[m
[31m-    border-radius: 10px;[m
[31m-    font-size: 14px;[m
[31m-    width: 100%;[m
[31m-    box-sizing: border-box;[m
[31m-    background: #f9f9f9;[m
[31m-    transition: border-color 0.3s;[m
[31m-}[m
[31m-input[type="number"]:focus {[m
[31m-    border-color: #3498db;[m
[31m-    outline: none;[m
[32m+[m[32m  width: 140px;[m
[32m+[m[32m  text-align: right;[m
[32m+[m[32m  font-size: 16px;[m
[32m+[m[32m  font-weight: 400;[m
[32m+[m[32m  color: #1C2526;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.input-wrapper {[m
[32m+[m[32m  position: relative;[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  align-items: center;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput[type="number"], input[type="text"], select, input[type="date"] {[m
[32m+[m[32m  padding: 10px 10px 10px 30px;[m
[32m+[m[32m  border: 1px solid #D2D6DC;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  font-size: 16px;[m
[32m+[m[32m  width: 160px;[m
[32m+[m[32m  box-sizing: border-box;[m
[32m+[m[32m  background: #fff;[m
[32m+[m[32m  transition: border-color 0.2s, box-shadow 0.2s;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput[type="number"]:focus, input[type="text"]:focus, select:focus, input[type="date"]:focus {[m
[32m+[m[32m  border-color: #6B8E23;[m
[32m+[m[32m  box-shadow: 0 0 0 3px rgba(107, 142, 35, 0.2);[m
[32m+[m[32m  outline: none;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.icon {[m
[32m+[m[32m  position: absolute;[m
[32m+[m[32m  left: 10px;[m
[32m+[m[32m  width: 16px;[m
[32m+[m[32m  height: 16px;[m
[32m+[m[32m  background-size: contain;[m
[32m+[m[32m  background-repeat: no-repeat;[m
 }[m
[32m+[m
[32m+[m[32m.icon-width { background-image: url('../icons/width.svg'); }[m
[32m+[m[32m.icon-weft { background-image: url('../icons/weft.svg'); }[m
[32m+[m[32m.icon-head { background-image: url('../icons/head.svg'); }[m
[32m+[m[32m.icon-warp { background-image: url('../icons/warp.svg'); }[m
[32m+[m[32m.icon-price { background-image: url('../icons/price.svg'); }[m
[32m+[m[32m.icon-speed { background-image: url('../icons/speed.svg'); }[m
[32m+[m[32m.icon-efficiency { background-image: url('../icons/efficiency.svg'); }[m
[32m+[m[32m.icon-shrinkage { background-image: url('../icons/shrinkage.svg'); }[m
[32m+[m[32m.icon-cost { background-image: url('../icons/cost.svg'); }[m
[32m+[m[32m.icon-invoice { background-image: url('../icons/invoice.svg'); }[m
[32m+[m[32m.icon-output { background-image: url('../icons/output.svg'); }[m
[32m+[m[32m.icon-profit { background-image: url('../icons/profit.svg'); }[m
[32m+[m
 .question-mark {[m
[31m-    cursor: pointer;[m
[31m-    color: #3498db;[m
[31m-    font-size: 16px;[m
[31m-    margin-left: 5px;[m
[31m-}[m
[31m-.tooltip {[m
[31m-    position: relative;[m
[31m-    display: inline-block;[m
[31m-}[m
[31m-.tooltip .tooltiptext {[m
[31m-    visibility: hidden;[m
[31m-    width: 200px;[m
[31m-    background-color: #333;[m
[31m-    color: #fff;[m
[31m-    text-align: center;[m
[31m-    padding: 5px 10px;[m
[31m-    border-radius: 6px;[m
[31m-    position: absolute;[m
[31m-    z-index: 1;[m
[31m-    bottom: 125%;[m
[31m-    left: 50%;[m
[31m-    margin-left: -100px;[m
[31m-    opacity: 0;[m
[31m-    transition: opacity 0.3s;[m
[31m-}[m
[31m-.tooltip:hover .tooltiptext {[m
[31m-    visibility: visible;[m
[31m-    opacity: 1;[m
[32m+[m[32m  cursor: pointer;[m
[32m+[m[32m  color: #6B8E23;[m
[32m+[m[32m  font-size: 14px;[m
[32m+[m[32m  font-weight: 600;[m
[32m+[m[32m  margin-left: 4px;[m
 }[m
[32m+[m
[32m+[m[32m.input-with-tooltip {[m
[32m+[m[32m  position: relative;[m
[32m+[m[32m  display: inline-block;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#weft2-group {[m
[32m+[m[32m  display: none;[m
[32m+[m[32m  padding: 10px;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  margin-top: 10px;[m
[32m+[m[32m  transition: all 0.3s ease;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.toggle-group {[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  align-items: center;[m
[32m+[m[32m  gap: 10px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.switch {[m
[32m+[m[32m  position: relative;[m
[32m+[m[32m  display: inline-block;[m
[32m+[m[32m  width: 40px;[m
[32m+[m[32m  height: 20px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.switch input {[m
[32m+[m[32m  opacity: 0;[m
[32m+[m[32m  width: 0;[m
[32m+[m[32m  height: 0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.slider {[m
[32m+[m[32m  position: absolute;[m
[32m+[m[32m  cursor: pointer;[m
[32m+[m[32m  top: 0;[m
[32m+[m[32m  left: 0;[m
[32m+[m[32m  right: 0;[m
[32m+[m[32m  bottom: 0;[m
[32m+[m[32m  background-color: #ccc;[m
[32m+[m[32m  transition: .4s;[m
[32m+[m[32m  border-radius: 20px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.slider:before {[m
[32m+[m[32m  position: absolute;[m
[32m+[m[32m  content: "";[m
[32m+[m[32m  height: 16px;[m
[32m+[m[32m  width: 16px;[m
[32m+[m[32m  left: 2px;[m
[32m+[m[32m  bottom: 2px;[m
[32m+[m[32m  background-color: white;[m
[32m+[m[32m  transition: .4s;[m
[32m+[m[32m  border-radius: 50%;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput:checked + .slider {[m
[32m+[m[32m  background-color: #6B8E23;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32minput:checked + .slider:before {[m
[32m+[m[32m  transform: translateX(20px);[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.tooltiptext {[m
[32m+[m[32m  visibility: hidden;[m
[32m+[m[32m  width: 180px;[m
[32m+[m[32m  background-color: rgba(0, 0, 0, 0.85);[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m  text-align: center;[m
[32m+[m[32m  padding: 6px 10px;[m
[32m+[m[32m  border-radius: 6px;[m
[32m+[m[32m  position: absolute;[m
[32m+[m[32m  z-index: 1;[m
[32m+[m[32m  top: -40px;[m
[32m+[m[32m  left: 50%;[m
[32m+[m[32m  transform: translateX(-50%);[m
[32m+[m[32m  opacity: 0;[m
[32m+[m[32m  transition: opacity 0.2s;[m
[32m+[m[32m  font-size: 12px;[m
[32m+[m[32m}[m
[32m+[m
 .button-group {[m
[31m-    display: flex;[m
[31m-    justify-content: space-around;[m
[31m-    margin-top: 15px;[m
[31m-}[m
[31m-input[type="submit"], #reset-button {[m
[31m-    padding: 12px;[m
[31m-    border: none;[m
[31m-    border-radius: 50%;[m
[31m-    width: 120px;[m
[31m-    cursor: pointer;[m
[31m-    font-size: 16px;[m
[31m-    font-weight: 700;[m
[31m-    transition: transform 0.2s, background-color 0.3s;[m
[31m-}[m
[31m-input[type="submit"] {[m
[31m-    background-color: #ff6b6b;[m
[31m-    color: white;[m
[31m-}[m
[31m-input[type="submit"]:hover {[m
[31m-    background-color: #e65a5a;[m
[31m-    transform: scale(1.1);[m
[31m-}[m
[31m-input[type="submit"]:active {[m
[31m-    transform: scale(0.95);[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  justify-content: flex-end;[m
[32m+[m[32m  gap: 20px;[m
[32m+[m[32m  margin-top: 30px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.submit-btn, #reset-button, #save-button, #delete-button, .back-btn {[m
[32m+[m[32m  padding: 10px 20px;[m
[32m+[m[32m  border: none;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  font-size: 16px;[m
[32m+[m[32m  font-weight: 600;[m
[32m+[m[32m  cursor: pointer;[m
[32m+[m[32m  transition: background-color 0.2s, transform 0.1s;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.submit-btn {[m
[32m+[m[32m  background: #6B8E23;[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.submit-btn:hover {[m
[32m+[m[32m  background: #556B2F;[m
 }[m
[32m+[m
[32m+[m[32m.submit-btn:active {[m
[32m+[m[32m  transform: scale(0.95);[m
[32m+[m[32m}[m
[32m+[m
 #reset-button {[m
[31m-    background-color: #2ecc71;[m
[31m-    color: white;[m
[32m+[m[32m  background: none;[m
[32m+[m[32m  color: #6B8E23;[m
[32m+[m[32m  border: 1px solid #6B8E23;[m
 }[m
[32m+[m
 #reset-button:hover {[m
[31m-    background-color: #27ae60;[m
[31m-    transform: scale(1.1);[m
[31m-}[m
[31m-#reset-button:active {[m
[31m-    transform: scale(0.95);[m
[31m-}[m
[31m-.result-section h3 {[m
[31m-    color: #2c3e50;[m
[31m-    margin-bottom: 15px;[m
[31m-    text-align: center;[m
[31m-}[m
[31m-.result-table {[m
[31m-    width: 100%;[m
[31m-    border-collapse: collapse;[m
[31m-    opacity: 0;[m
[31m-    animation: fadeIn 0.5s forwards;[m
[31m-}[m
[31m-.result-table th, .result-table td {[m
[31m-    padding: 8px;[m
[31m-    border-bottom: 1px solid #ddd;[m
[31m-    text-align: left;[m
[31m-    font-size: 14px;[m
[31m-}[m
[31m-.result-table th {[m
[31m-    background-color: #3498db;[m
[31m-    color: white;[m
[31m-}[m
[31m-.result-table tr:last-child td {[m
[31m-    border-bottom: none;[m
[31m-    font-weight: 700;[m
[31m-    color: #ff6b6b;[m
[32m+[m[32m  background: #F0F8FF;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#save-button {[m
[32m+[m[32m  background: #6B8E23;[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m  margin-top: 20px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#save-button:hover {[m
[32m+[m[32m  background: #556B2F;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#delete-button {[m
[32m+[m[32m  background: none;[m
[32m+[m[32m  color: #ff3b30;[m
[32m+[m[32m  border: 1px solid #ff3b30;[m
[32m+[m[32m  margin-top: 10px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#delete-button:hover {[m
[32m+[m[32m  background: #fff0f0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.back-btn {[m
[32m+[m[32m  background: #6B8E23;[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m  margin-top: 20px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.back-btn:hover {[m
[32m+[m[32m  background: #556B2F;[m
 }[m
[32m+[m
[32m+[m[32m.result-section h2 {[m
[32m+[m[32m  font-size: 20px;[m
[32m+[m[32m  font-weight: 600;[m
[32m+[m[32m  color: #333333;[m
[32m+[m[32m  margin-bottom: 20px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.result-card {[m
[32m+[m[32m  background: #F5F7F9;[m
[32m+[m[32m  padding: 10px;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  margin-bottom: 10px;[m
[32m+[m[32m  display: flex;[m
[32m+[m[32m  align-items: center;[m
[32m+[m[32m  gap: 10px;[m
[32m+[m[32m  font-size: 16px;[m
[32m+[m[32m  color: #1C2526;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.result-icon {[m
[32m+[m[32m  width: 20px;[m
[32m+[m[32m  height: 20px;[m
[32m+[m[32m  background-size: contain;[m
[32m+[m[32m  background-repeat: no-repeat;[m
[32m+[m[32m}[m
[32m+[m
 .loader {[m
[31m-    border: 8px solid #f3f3f3;[m
[31m-    border-top: 8px solid #3498db;[m
[31m-    border-radius: 50%;[m
[31m-    width: 30px;[m
[31m-    height: 30px;[m
[31m-    animation: spin 1s linear infinite;[m
[31m-    margin: 20px auto;[m
[31m-    display: none;[m
[32m+[m[32m  display: none;[m
[32m+[m[32m  justify-content: center;[m
[32m+[m[32m  align-items: center;[m
[32m+[m[32m  position: fixed;[m
[32m+[m[32m  top: 50%;[m
[32m+[m[32m  left: 50%;[m
[32m+[m[32m  transform: translate(-50%, -50%);[m
[32m+[m[32m  background: rgba(255, 255, 255, 0.9);[m
[32m+[m[32m  padding: 10px 20px;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);[m
[32m+[m[32m  font-size: 14px;[m
[32m+[m[32m  color: #6B8E23;[m
 }[m
[31m-@keyframes spin {[m
[31m-    0% { transform: rotate(0deg); }[m
[31m-    100% { transform: rotate(360deg); }[m
[32m+[m
[32m+[m[32m.loader span {[m
[32m+[m[32m  margin-left: 10px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.loader::before {[m
[32m+[m[32m  content: '';[m
[32m+[m[32m  width: 16px;[m
[32m+[m[32m  height: 16px;[m
[32m+[m[32m  border: 2px solid #F5F7F9;[m
[32m+[m[32m  border-top: 2px solid #6B8E23;[m
[32m+[m[32m  border-radius: 50%;[m
[32m+[m[32m  animation: spin 1s linear infinite;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.feedback-message {[m
[32m+[m[32m  display: none;[m
[32m+[m[32m  position: fixed;[m
[32m+[m[32m  bottom: 20px;[m
[32m+[m[32m  right: 20px;[m
[32m+[m[32m  padding: 10px 20px;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  font-size: 14px;[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);[m
[32m+[m[32m  z-index: 1000;[m
 }[m
[31m-@keyframes fadeIn {[m
[31m-    from { opacity: 0; }[m
[31m-    to { opacity: 1; }[m
[32m+[m
[32m+[m[32m.feedback-message.success {[m
[32m+[m[32m  background: #6B8E23;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.feedback-message.error {[m
[32m+[m[32m  background: #ff3b30;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table_container {[m
[32m+[m[32m  max-height: 400px;[m
[32m+[m[32m  overflow-y: auto;[m
[32m+[m[32m  margin-bottom: 20px;[m
[32m+[m[32m  border: 1px solid #D2D6DC;[m
[32m+[m[32m  border-radius: 8px;[m
[32m+[m[32m  background: #F5F7F9;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table {[m
[32m+[m[32m  width: 100%;[m
[32m+[m[32m  border-collapse: collapse;[m
[32m+[m[32m  font-size: 14px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table th, #history_table td {[m
[32m+[m[32m  padding: 8px;[m
[32m+[m[32m  text-align: left;[m
[32m+[m[32m  border-bottom: 1px solid #D2D6DC;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table th {[m
[32m+[m[32m  background: #6B8E23;[m
[32m+[m[32m  color: #fff;[m
[32m+[m[32m  position: sticky;[m
[32m+[m[32m  top: 0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table td {[m
[32m+[m[32m  cursor: pointer;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table td:hover {[m
[32m+[m[32m  background: #E6E6C4;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_table tr:last-child td {[m
[32m+[m[32m  border-bottom: none;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m#history_search {[m
[32m+[m[32m  padding: 8px;[m
[32m+[m[32m  width: 100%;[m
[32m+[m[32m  box-sizing: border-box;[m
[32m+[m[32m  margin-bottom: 10px;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.delete-history-btn {[m
[32m+[m[32m  padding: 4px 8px;[m
[32m+[m[32m  border: 1px solid #ff3b30;[m
[32m+[m[32m  border-radius: 4px;[m
[32m+[m[32m  background: none;[m
[32m+[m[32m  color: #ff3b30;[m
[32m+[m[32m  font-size: 12px;[m
[32m+[m[32m  cursor: pointer;[m
[32m+[m[32m  transition: background-color 0.2s;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m.delete-history-btn:hover {[m
[32m+[m[32m  background: #fff0f0;[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32m@keyframes spin {[m
[32m+[m[32m  0% { transform: rotate(0deg); }[m
[32m+[m[32m  100% { transform: rotate(360deg); }[m
 }[m
\ No newline at end of file[m
[1mdiff --git a/uv.lock b/uv.lock[m
[1mindex 5efad84..aab5d0b 100644[m
[1m--- a/uv.lock[m
[1m+++ b/uv.lock[m
[36m@@ -40,6 +40,12 @@[m [mwheels = [[m
     { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335 },[m
 ][m
 [m
[32m+[m[32m[[package]][m
[32m+[m[32mname = "cssmin"[m
[32m+[m[32mversion = "0.2.0"[m
[32m+[m[32msource = { registry = "https://pypi.org/simple" }[m
[32m+[m[32msdist = { url = "https://files.pythonhosted.org/packages/8e/d8/dc9da69bb186303f7ab41adef0a5b6d34da2fdba006827620877760241c3/cssmin-0.2.0.tar.gz", hash = "sha256:e012f0cc8401efcf2620332339011564738ae32be8c84b2e43ce8beaec1067b6", size = 3228 }[m
[32m+[m
 [[package]][m
 name = "flask"[m
 version = "3.1.0"[m
[36m@@ -156,6 +162,7 @@[m [mname = "python-template"[m
 version = "0.1.0"[m
 source = { virtual = "." }[m
 dependencies = [[m
[32m+[m[32m    { name = "cssmin" },[m
     { name = "flask" },[m
     { name = "flask-assets" },[m
     { name = "flask-caching" },[m
[36m@@ -163,6 +170,7 @@[m [mdependencies = [[m
 [m
 [package.metadata][m
 requires-dist = [[m
[32m+[m[32m    { name = "cssmin", specifier = ">=0.2.0" },[m
     { name = "flask", specifier = ">=3.1.0" },[m
     { name = "flask-assets", specifier = ">=2.1.0" },[m
     { name = "flask-caching", specifier = ">=2.3.1" },[m
