export function collectDuplicateIds(ids, label, errors) {
  const seen = new Set();
  for (const id of ids) {
    if (seen.has(id)) errors.push(`duplicate ${label} ID ${String(id)}`);
    seen.add(id);
  }
}
