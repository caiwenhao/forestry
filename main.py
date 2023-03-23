from notion_client import Client
import os
import re
import shutil
from notion2md.exporter.block import MarkdownExporter

# 初始化 Notion 客户端
notion = Client(auth=os.environ["NOTION_TOKEN"])

# 替换为您的数据库 ID
database_id = "eb524516e1814a5495a7774d3545a18b"

# 定义筛选条件
filter_params = {
    "property": "status",
    "select": {
        "equals": "Published"
    }
}

# 获取已发布的文章
results = notion.databases.query(
    **{
        "database_id": database_id,
        "filter": filter_params
    }
)
published_pages = results['results']
print(published_pages)

# 创建 pages/advanced 和 public/images 目录，如果尚不存在
os.makedirs('pages/advanced', exist_ok=True)
os.makedirs('public/images', exist_ok=True)

# 使用 notion2md 将已发布的文章转换为 Markdown 文件并下载图片
for page in published_pages:
    title = page['properties']['title']['title'][0]['plain_text']
    url = page['url']
    page_id = page['id']

    # 将 Notion 页面转换为 Markdown 文件
    markdown_file = f"public/images/{title}.md"
    MarkdownExporter(block_id=page_id, output_filename=title, download=True, unzipped=True, output_path="public/images").export()

    # 读取生成的 Markdown 文件并在开头添加指定标识符
    with open(markdown_file, 'r', encoding='utf-8') as file:
        content = file.read()

    content = "---\n\n---\n" + content

    # 修复图片路径
    content = re.sub(r'!\[([^\]]+)]\(([^\)]+)\)', r'![\1](/images/\2)', content)

    # 将修改后的内容写回文件
    with open(markdown_file, 'w', encoding='utf-8') as file:
        file.write(content)

    # 将生成的 Markdown 文件移动到 pages/advanced 目录下
    destination = f"pages/advanced/{title}.md"
    shutil.move(markdown_file, destination)

    print(f"已成功导出 '{title}' 到 {destination}")