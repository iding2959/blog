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
    cat.sort_order = idx >= 0 ? idx : 999;
  });
});
