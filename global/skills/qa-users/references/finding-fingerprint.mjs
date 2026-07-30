import { createHash } from "node:crypto";

const FINGERPRINT_VERSION = "qa-users.finding-fingerprint.v1";

export function createFindingFingerprint({ affected_entrypoint, reproduction, expected, observed, category }) {
  const fields = [
    ["affected_entrypoint", normalizeValue(affected_entrypoint)],
    ["reproduction", normalizeReproduction(reproduction)],
    ["expected", normalizeValue(expected)],
    ["observed", normalizeValue(observed)],
    ["category", normalizeValue(category)],
  ];
  const payload = [frame(FINGERPRINT_VERSION), ...fields.flatMap(([name, value]) => [frame(name), frame(value)])].join("\u0000");
  return createHash("sha256").update(payload, "utf8").digest("hex");
}

export function normalizeValue(value) {
  if (typeof value !== "string") throw new TypeError("finding fingerprint fields must be strings");
  return value.normalize("NFC").replace(/\r\n?/gu, "\n").replace(/\s+/gu, " ").trim().toLocaleLowerCase("en-US");
}

function normalizeReproduction(reproduction) {
  if (!Array.isArray(reproduction) || reproduction.length === 0) throw new TypeError("finding reproduction must be a non-empty array");
  return reproduction.map(normalizeValue).join("\u001f");
}

function frame(value) {
  const byteLength = Buffer.byteLength(value, "utf8");
  return `${byteLength}:${value}`;
}
