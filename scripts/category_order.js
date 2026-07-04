// 自定义分类排序（非侵入式，替换主题不影响）
// 配合 themes/fluid/_config.yml 中 category.order_by: "sort_order" 使用
// 在生成前为每个 Category 模型注入 sort_order 字段
const CATEGORY_ORDER = [
  'AI 应用',
  '基础设施',
  '开发实践',
  '网络与代理',
  '工具与效率',
  '杂谈',
];

hexo.extend.filter.register('before_generate', function () {
  const Category = hexo.database.model('Category');
  if (!Category) return;

  Category.forEach(function (cat) {
    const idx = CATEGORY_ORDER.indexOf(cat.name);
    const sortOrder = idx >= 0 ? idx : 999;
    // 关键：必须写入 model.data[id] 原始数据存储，
    // 因为后续 find() 会从 data[id] 重新创建 Document，
    // 只设置 Document 对象的属性会在 find() 时丢失
    if (Category.data[cat._id]) {
      Category.data[cat._id].sort_order = sortOrder;
    }
  });
});
