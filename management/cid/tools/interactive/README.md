# OAC CID Interactive Tools

Interactive HTML tools for authoring, validating, and visualizing OAC Connector Interface Definitions (CIDs). All tools are self-contained single-file HTML pages — open directly in any modern browser, no server or installation required.

All tools use JSON format per the CID v0.9 schema and reflect the current OCP OAC Base Specification v0.9.

---

## Tools

| Tool | File | Purpose |
|------|------|---------|
| [CID Editor](#cid-editor) | `oac-cid-editor/OAC-CID-Editor.html` | Guided form editor for authoring and exporting JSON CID documents |
| [Insertion Emulator](#insertion-emulator) | `oac-cid-insertion-emulator/OAC-CID-Insertion-Emulator.html` | Animated simulation of adapter insertion with live compliance checking |
| [Compliance Logic](#compliance-logic) | `oac-cid-compliance-logic/OAC-CID-Compliance-Logic.html` | Static reference diagram of the BMC CID compliance check sequence |

---

## CID Editor

A multi-panel editor for authoring OAC CID documents and OCP-ratified Connector Profiles. Operates in two top-level modes — **CID** (full adapter document) and **Connector Profile** (reusable pinout definition) — each with **Guided** (form-based) and **Manual** (raw JSON with syntax highlighting) editing sub-modes. All modes stay in two-way sync.

**Sections covered:** metadata, power (input voltage, connector type, all OPL fields), connectors (impedance, connector_profile reference, M-PESTI, high-speed lanes with protocol groups and link subdivision, clocking, discrete signals).

**Visual Pin Map:** Expandable pin grid for each connector. Click any available cell to assign HS lane, clock, or discrete signal pins. Assigned pins are color-coded by type and labeled with protocol group and lane index. Pin A1 is permanently blocked (reserved for OAC_PRSNT#/M-PESTI).

**Live Validation:** Continuous schema validation in both Guided and Manual modes. Errors and warnings appear in a pane below the JSON preview with a badge count in the header.

**Import/Export:** Load any existing CID or Connector Profile JSON (auto-detected). Export as formatted or minified JSON.

**Help:** `?` button opens a modal with Getting Started guide, searchable Field Reference, Keyboard Shortcuts, and About/version info. Field-level `?` tooltip icons provide inline descriptions.

No external dependencies. See [oac-cid-editor/README.md](oac-cid-editor/README.md) for full documentation.

---

## Insertion Emulator

Load a baseboard capability JSON and an adapter CID JSON, then click Insert to run a sequenced simulation. An animated card-insertion visualization plays while the compliance engine evaluates the two schemas against each other. The event log on the right panel records every check in real time.

**Compliance checks:** input voltage, connector type (100A/125A), OPL-MAX power budget, OPL-EMG declaration, connector impedance, high-speed lane parameters, lane pin assignments, reference clocking, required discrete signals, spec revision.

**Verdicts:** BLOCKED (any failure — OAC_PWR_EN remains de-asserted), DEGRADED (warnings only — power enabled with reduced capability), NORMAL (all pass — full capability).

No external dependencies.

---

## Compliance Logic

A static reference diagram showing the full sequence of CID validation checks performed by the upstream management controller, their evaluated fields, and their possible outcomes (FAIL / WARN / PASS / SKIP). Covers schema validation, power fields (input_voltage, connector_type, opl_max_w, opl_emg_w), connector profile resolution, high-speed lanes, clocking, discrete signals, and spec revision.

No external dependencies.

---

## Baseboard Schema Format

The Insertion Emulator requires a **baseboard capability JSON** in addition to the adapter CID. The baseboard file uses the same `oac_cid` structure as an adapter CID but describes the slot's capabilities rather than an adapter's requirements. Any field the baseboard does not populate is treated as undeclared (generating a WARN rather than a FAIL where applicable).

Example minimal baseboard file:

```json
{
  "oac_cid": {
    "metadata": {
      "schema_version": "0.9",
      "oac_spec_revision": "0.9",
      "description": "Example baseboard slot — 50V, 125A, 5000W"
    },
    "power": {
      "primary": {
        "input_voltage": "+50V",
        "connector_type": "125A",
        "opl_max_w": 5000.0,
        "opl_emg_w": 500.0
      }
    },
    "connectors": [
      {
        "id": "CONN0",
        "populated": true,
        "impedance_ohm": 85,
        "high_speed_lanes": [
          {
            "name": "pcie_primary",
            "protocol": "PCIe Gen6",
            "link_direction": "INBOUND",
            "total_lanes": 16,
            "minimum_lanes": 4
          }
        ]
      }
    ]
  }
}
```

Note that `high_speed_lanes` is an **array** of named protocol groups. `link_role` is not part of the
v0.9 schema — it was removed because link topology has no bearing on the power decision.

---

## Version Alignment

These tools were authored against the v0.9 schema, but some embedded version strings and defaults
inside the HTML still read `0.7` or `0.8` — the Editor's About panel and its generated export
filenames, and the Insertion Emulator's header and log banner among them. This is cosmetic: the
field sets, validation rules, and compliance checks are v0.9. Set `schema_version` explicitly to
`"0.9"` when authoring, and rename exported files accordingly.
