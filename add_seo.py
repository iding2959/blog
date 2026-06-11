#!/usr/bin/env python3
import os
import re
from pathlib import Path

# SEO 映射规则（根据标题关键词生成）
SEO_RULES = {
    'cloudflare': ('Cloudflare', 'Cloudflare Tunnel', '网络优化'),
    'conda': ('Conda', 'Python环境管理', 'Anaconda', 'Miniconda'),
    'gemini': ('Gemini', 'Google AI', 'API', '代理配置'),
    'gpustack': ('GPUStack', 'GPU管理', 'AI推理', 'vLLM', 'Transformers'),
    'juicefs': ('JuiceFS', 'Ubuntu', '分布式文件系统', '对象存储', 'Redis', 'S3'),
    'nix': ('Nix', 'WSL2', 'Linux', '包管理器'),
    'nvm': ('NVM', 'Node.js', '版本管理', 'Linux'),
    'postgresql': ('PostgreSQL', 'SSL', 'Docker', '数据库安全'),
    'pve': ('Proxmox VE', 'PVE', '虚拟化', 'Linux'),
    'pytorch': ('PyTorch', 'CUDA', 'GPU', '深度学习'),
    'tortoisegit': ('TortoiseGit', 'Git', 'Windows'),
    'typora': ('Typora', 'Markdown编辑器'),
    'uv': ('uv', 'Python', '包管理器', 'Docker'),
    'vscode': ('VS Code', 'Todo Tree', '插件'),
    'win11': ('Windows 11', '右键菜单', '系统优化'),
    'clash': ('Clash Verge Rev', '代理', '脚本配置'),
    'cuda': ('CUDA', 'NVIDIA', 'GPU', 'Ubuntu'),
    'yolov8': ('YOLOv8', 'MNIST', '目标检测', '深度学习'),
    'network': ('网络优化', 'Linux', 'TCP', '性能调优'),
    'quanwu': ('科学上网', '网络配置', '代理'),
}

def extract_frontmatter(content):
    """提取 front-matter"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return None, content

def parse_frontmatter(fm_text):
    """解析 front-matter 为字典"""
    fm = {}
    current_key = None
    current_list = []

    for line in fm_text.split('\n'):
        if ':' in line and not line.startswith(' '):
            if current_key and current_list:
                fm[current_key] = current_list
                current_list = []

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value:
                fm[key] = value
            else:
                current_key = key
        elif line.strip().startswith('-') and current_key:
            current_list.append(line.strip()[1:].strip())

    if current_key and current_list:
        fm[current_key] = current_list

    return fm

def generate_seo(title, content):
    """根据标题和内容生成 SEO 信息"""
    title_lower = title.lower()

    # 匹配关键词规则
    keywords = []
    for key, kws in SEO_RULES.items():
        if key in title_lower:
            keywords.extend(kws)
            break

    # 如果没匹配到，从标题提取
    if not keywords:
        keywords = [w.strip() for w in re.findall(r'[\w一-鿿]+', title) if len(w.strip()) > 1][:6]

    # 生成描述：提取第一段或前100字
    desc_match = re.search(r'##[^\n]*\n\n([^\n]+)', content)
    if desc_match:
        description = desc_match.group(1).strip()[:120]
    else:
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        description = (lines[0][:120] if lines else title)[:120]

    return description, ', '.join(keywords[:8])

def rebuild_frontmatter(fm):
    """重建 front-matter"""
    lines = []
    for key, value in fm.items():
        if isinstance(value, list):
            lines.append(f'{key}:')
            for item in value:
                lines.append(f'  - {item}')
        else:
            lines.append(f'{key}: {value}')
    return '\n'.join(lines)

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_text, body = extract_frontmatter(content)
    if not fm_text:
        return False

    fm = parse_frontmatter(fm_text)

    # 检查是否已有 description 和 keywords
    if 'description' in fm and 'keywords' in fm:
        return False

    title = fm.get('title', '')
    description, keywords = generate_seo(title, body)

    # 添加 SEO 字段
    fm_new = {}
    for key in ['title', 'date']:
        if key in fm:
            fm_new[key] = fm[key]

    fm_new['description'] = description
    fm_new['keywords'] = keywords

    for key in fm:
        if key not in fm_new:
            fm_new[key] = fm[key]

    # 重建文件
    new_content = f"---\n{rebuild_frontmatter(fm_new)}\n---\n{body}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

# 主程序
posts_dir = Path('/home/iding/pypi/blog/source/_posts')
updated = 0
skipped = 0

for md_file in posts_dir.rglob('*.md'):
    if 'example' in md_file.name or md_file.name == 'hello-world.md':
        skipped += 1
        continue

    if process_file(md_file):
        print(f'✓ {md_file.relative_to(posts_dir)}')
        updated += 1
    else:
        skipped += 1

print(f'\n完成: {updated} 篇更新, {skipped} 篇跳过')
