// tests/workspace-buttons.test.cjs

const assert = require("node:assert/strict");
const fs = require("node:fs");
const { test } = require("node:test");

const source = fs.readFileSync(process.env.WIDGET_QML_PATH, "utf8");
const start = source.indexOf("  function workspaceIds() {");
const end = source.indexOf("\n  function dispatch(", start);
assert.ok(start >= 0 && end > start, "Workspace list function was not found");
const calculate = new Function("root", "Hyprland", source.slice(start, end) + "\nreturn workspaceIds();");

function workspaceIds(block, monitorName, values = []) {
  return calculate(
    { block, slots: 10, monitorName, blockOf: (id) => Math.floor((id - 1) / 10) },
    { workspaces: { values } },
  );
}

test("all ten primary-monitor slots remain visible when empty", () => {
  assert.deepEqual(workspaceIds(0, "eDP-1"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("external monitors show their own block of ten", () => {
  assert.deepEqual(workspaceIds(1, "DP-1"), [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]);
  assert.deepEqual(workspaceIds(2, "HDMI-A-1"), [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]);
});

test("existing workspaces do not duplicate buttons", () => {
  const values = [1, 6, 10].map((id) => ({ id, monitor: { name: "eDP-1" } }));
  assert.deepEqual(workspaceIds(0, "eDP-1", values), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("guest workspaces on this monitor are preserved and sorted", () => {
  const values = [
    { id: 23, monitor: { name: "eDP-1" } },
    { id: 12, monitor: { name: "eDP-1" } },
    { id: 21, monitor: { name: "DP-1" } },
  ];
  assert.deepEqual(workspaceIds(0, "eDP-1", values), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 23]);
});

test("special workspaces are excluded", () => {
  const values = [{ id: -99, monitor: { name: "eDP-1" } }, { id: 0 }];
  assert.deepEqual(workspaceIds(0, "eDP-1", values), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});
