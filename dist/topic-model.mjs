export const LABELS = ['RAG', 'Agents', 'Fine-tuning', 'Other'];

export function predictTopic(text, model) {
  if (typeof text !== 'string' || !text.trim()) throw Error('Enter a title and short description.');
  if (text.length > 4000) throw Error('Use a short description under 4,000 characters.');
  if (model?.schema_version !== 2 || !Array.isArray(model.classes)) throw Error('The starter router is unavailable.');
  const tokens = text.toLowerCase().match(/[\p{L}\p{N}_]{2,}/gu) || [];
  const terms = [...tokens, ...tokens.slice(0, -1).map((t, i) => `${t} ${tokens[i + 1]}`)];
  const counts = new Map();
  for (const term of terms) {
    if (!Object.hasOwn(model.vocabulary, term)) continue;
    const index = model.vocabulary[term]; counts.set(index, (counts.get(index) || 0) + 1);
  }
  if (!counts.size) return {label: 'Other', engine: model.engine, note: 'No recognized topic features.'};
  const values = [...counts].map(([i, count]) => [i, count * model.idf[i]]);
  const norm = Math.sqrt(values.reduce((sum, [, value]) => sum + value * value, 0));
  const scores = model.classes.map((_, c) => model.intercepts[c] + values.reduce((sum, [i, v]) => sum + model.coefficients[c][i] * v / norm, 0));
  const best = scores.indexOf(Math.max(...scores));
  return {label: model.classes[best], engine: model.engine};
}

function validateMetricsValue(value) {
  if (!value || !Number.isInteger(value.n) || value.n < 1 || value.n > 100000) throw Error('Invalid sample count.');
  for (const key of ['accuracy', 'macro_f1']) {
    if (typeof value[key] !== 'number' || !Number.isFinite(value[key]) || value[key] < 0 || value[key] > 1) throw Error('Invalid metrics.');
  }
  if (JSON.stringify(value.label_order) !== JSON.stringify(LABELS)) throw Error('The category order does not match this project.');
  const matrix = value.confusion_matrix;
  if (!Array.isArray(matrix) || matrix.length !== 4 || matrix.some(row => !Array.isArray(row) || row.length !== 4 || row.some(n => !Number.isInteger(n) || n < 0))) throw Error('Invalid confusion matrix.');
  if (matrix.flat().reduce((a, b) => a + b, 0) !== value.n) throw Error('Confusion matrix and sample count differ.');
  if (Math.abs(matrix.reduce((sum, row, i) => sum + row[i], 0) / value.n - value.accuracy) > 1e-8) throw Error('Accuracy and confusion matrix differ.');
}

export function validateComparison(report) {
  if (report?.schema_version !== 2 || report.task !== 'topic_router' || report.status !== 'measured' || report.same_evaluation_set !== true) throw Error('Import comparison.json from the completed topic-router notebook.');
  if (JSON.stringify(report.labels) !== JSON.stringify(LABELS) || !/^[a-f0-9]{64}$/.test(report.dataset_hash)) throw Error('Missing dataset identity or topic labels.');
  for (const results of [report, report.source_cases].filter(Boolean)) {
    const keys = ['baseline', 'finetuned', ...(results.lexical ? ['lexical'] : [])];
    for (const key of keys) validateMetricsValue(results[key]);
    for (const key of keys) {
      if (results[key].n !== results.baseline.n) throw Error('Evaluation counts do not match.');
      const support = results[key].confusion_matrix.map(row => row.reduce((a, b) => a + b, 0));
      const baseSupport = results.baseline.confusion_matrix.map(row => row.reduce((a, b) => a + b, 0));
      if (JSON.stringify(support) !== JSON.stringify(baseSupport)) throw Error('Evaluation class counts do not match.');
    }
  }
  return report;
}

export function validateArticles(packet) {
  if (packet?.schema_version !== 2 || packet.task !== 'topic_router' || typeof packet.engine !== 'string' || packet.engine.length > 150) throw Error('Import routed_articles.json from the topic-router notebook.');
  if (!['recent_editorial_feed', 'historical_paper_examples'].includes(packet.source_mode)) throw Error('Missing source type.');
  if (!Array.isArray(packet.articles) || !packet.articles.length || packet.articles.length > 100) throw Error('Include 1–100 articles.');
  const ids = new Set();
  for (const article of packet.articles) {
    for (const key of ['id', 'title', 'text', 'source_url']) if (typeof article[key] !== 'string' || !article[key].trim() || article[key].length > 5000) throw Error(`Invalid article ${key}.`);
    if (ids.has(article.id)) throw Error('Duplicate article ID.'); ids.add(article.id);
    if (!LABELS.includes(article.label)) throw Error('Invalid topic label.');
    let url; try { url = new URL(article.source_url); } catch { throw Error('Invalid source URL.'); }
    if (url.protocol !== 'https:' || url.username || url.password) throw Error('Sources must use HTTPS without embedded credentials.');
    if (article.published_at !== undefined && (typeof article.published_at !== 'string' || !Number.isFinite(Date.parse(article.published_at)))) throw Error('Invalid publication date.');
  }
  return packet;
}
