import os
from cssmin import cssmin

# 源文件路径
source_css = 'static/css/style.css'
# 目标文件路径
target_min_css = 'static/gen/style.min.css'

# 确保目标目录存在
os.makedirs('static/gen', exist_ok=True)

# 读取原始 CSS 文件
with open(source_css, 'r') as f:
    css_content = f.read()

# 压缩 CSS
minified_css = cssmin(css_content)

# 写入压缩后的文件
with open(target_min_css, 'w') as f:
    f.write(minified_css)

print(f"CSS 已成功压缩至: {target_min_css}")