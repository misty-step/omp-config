import { isDeepStrictEqual } from "node:util";

export function deepEqual(left, right) {
  return isDeepStrictEqual(left, right);
}

export function assertRejected(label, operation, fail) {
  try {
    operation();
  } catch {
    return;
  }
  fail(`${label} unexpectedly accepted`);
}

export function assertAccepted(label, operation, fail) {
  try {
    operation();
  } catch (error) {
    fail(`${label} rejected: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export function assertRejectsWithMessage(label, operation, fragment, fail) {
  let caught;
  try {
    operation();
  } catch (error) {
    caught = error;
  }
  if (!caught) {
    fail(`${label} unexpectedly accepted`);
  } else if (!String(caught.message).includes(fragment)) {
    fail(`${label} rejected for the wrong reason`);
  }
}

export function assertRejectsWithExactMessage(label, operation, expected, fail) {
  let caught;
  try {
    operation();
  } catch (error) {
    caught = error;
  }
  if (!caught) {
    fail(`${label} unexpectedly accepted`);
  } else if (String(caught.message) !== expected) {
    fail(`${label} diagnostic drifted: ${String(caught.message)}`);
  }
}
