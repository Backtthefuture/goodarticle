from flask import Flask, render_template
from feishu import FeishuAPI
import json

app = Flask(__name__)
feishu_api = FeishuAPI()

def extract_text_from_json(json_data):
    """从飞书多维表格返回的JSON数据中提取纯文本内容"""
    if not json_data:
        return ''
    
    # 如果是字符串形式的JSON，尝试解析
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except:
            return json_data
    
    # 如果是列表，遍历列表并提取文本
    if isinstance(json_data, list):
        result = []
        for item in json_data:
            if isinstance(item, dict) and 'text' in item:
                result.append(item['text'])
            else:
                result.append(str(item))
        return ' '.join(result)
    
    # 如果是字典，直接提取text字段
    if isinstance(json_data, dict) and 'text' in json_data:
        return json_data['text']
    
    # 其他情况直接返回字符串形式
    return str(json_data)

@app.route('/')
def index():
    # 获取飞书多维表格数据
    records = feishu_api.get_table_records()
    articles = []
    
    for record in records:
        fields = record.get('fields', {})
        # 提取文章ID用于生成唯一标识符
        article_id = record.get('record_id', '')
        
        # 处理概要内容输出字段，提取纯文本
        content_raw = fields.get('概要内容输出', '')
        content_text = extract_text_from_json(content_raw)
        
        # 同样处理金句和点评字段
        quote_raw = fields.get('金句输出', '')
        quote_text = extract_text_from_json(quote_raw)
        
        comment_raw = fields.get('黄叔点评', '')
        comment_text = extract_text_from_json(comment_raw)
        
        # 获取创建时间信息（如果有）
        created_time = record.get('created_time', '')
        
        # 获取原文链接（可能存在不同的字段名）
        original_url = ''
        for field_name in ['原链接', '原文链接', '链接', 'URL', 'url']:
            if fields.get(field_name):
                url_raw = fields.get(field_name)
                original_url = extract_text_from_json(url_raw)
                break
        
        article = {
            'id': article_id,
            'title': fields.get('标题', ''),
            'quote': quote_text,
            'comment': comment_text,
            'content': content_text,
            'created_time': created_time,
            'original_url': original_url
        }
        articles.append(article)
    
    # 将文章列表倒序排列，最新的内容显示在最前面
    articles.reverse()
    
    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)