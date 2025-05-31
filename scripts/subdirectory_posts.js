// 使用子目录管理文章且保持原有永久链接格式
const { join } = require('path');
const { readdirSync } = require('fs');

// 处理文章的永久链接，确保子目录不影响最终URL
hexo.extend.filter.register('post_permalink', function (permalink) {
  // Hexo已经生成了包含子目录的permalink
  // 我们需要分析它并删除子目录部分
  
  // 例如：2025/05/31/tech/test-subdirectory/ → 2025/05/31/test-subdirectory/
  
  // 获取_posts目录的路径
  const postDir = join(this.source_dir, '_posts');
  
  try {
    // 获取_posts目录下所有子目录
    const folders = readdirSync(postDir, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    
    // 分解permalink路径组件
    const pathParts = permalink.split('/').filter(Boolean);
    
    // 检查路径中是否包含任何子目录名
    for (const folder of folders) {
      const index = pathParts.indexOf(folder);
      if (index !== -1) {
        // 移除子目录名
        pathParts.splice(index, 1);
        // 重建permalink
        return pathParts.join('/') + '/';
      }
    }
  } catch (err) {
    // 如果出错（例如_posts目录不存在），直接返回原始链接
    console.error('Error processing permalink:', err);
  }
  
  return permalink;
});

// 让 hexo new 生成的文章可以放在指定的子目录中
hexo.extend.filter.register('new_post_path', function(data) {
  if (data.path && data.path.includes('/')) {
    // 如果路径中包含斜杠，说明用户指定了子目录
    return data;
  }
  return data;
}); 