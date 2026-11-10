# OAC CID Interactive Tools

Interactive HTML tools for authoring, validating, and visualizing OAC Connector Interface Definitions (CIDs). All tools are self-contained single-file HTML pages — open directly in any modern browser, no server or installation required.

All tools use JSON format per the CID v0.9 schema and reflect the current OCP OAC Base Specification v0.9.

All three tools operate on a CID document that is already in hand. Locating it is the job of the
**OAC Metadata file** — the first file the upstream management controller reads and the only one it
finds by name. The Insertion Emulator and the Compliance Logic diagram both show that step in their
sequence, but neither performs it: these are offline tools and there is no OAC to query. See
[`../../../metadata/`](../../../metadata/) for what happens before the CID is opened.

---

## Tools

| Tool | File | Purpose |
|------|------|---------|
| [CID Editor](#cid-editor) | `oac-cid-editor/OAC-CID-Editor.html` | Guided form editor for authoring and exporting JSON CID documents |
| [Insertion Emulator](#insertion-emulator) | `oac-cid-insertion-emulator/OAC-CID-Insertion-Emulator.html` | Animated simulation of OAC insertion with live compliance checking |
| [Compliance Logic](#compliance-logic) | `oac-cid-compliance-logic/OAC-CID-Compliance-Logic.html` | Static reference diagram of the upstream management controller's CID compliance check sequence |

---

## CID Editor

A multi-panel editor for authoring OAC CID documents and OCP-ratified Connector Profiles. Operates in two top-level modes — **CID** (full OAC document) and **Connector Profile** (reusable pinout definition) — each with **Guided** (form-based) and **Manual** (raw JSON with syntax highlighting) editing sub-modes. All modes stay in two-way sync.

**Sections covered:** metadata, power (input voltage, connector type, all OPL fields, declared power excursion profile), connectors (impedance, connector_profile reference, M-PESTI, high-speed lanes with protocol groups and link subdivision, clocking, discrete signals).

**Power Excursion:** An optional card, off by default. Enabling it offers the recommended interval grid of specification Table 7.3.2-2 in one click, or intervals can be entered by hand. Each row shows the Base Specification Section 10.1.4 ceiling at that interval alongside the declared ratio, and a plot draws the declared profile against the envelope. The profile is drawn as a **step**, because the nearest-shorter-interval rule of Section 7.3.2 is literally a step function — the plot and the normative rule agree by construction. Out-of-envelope points are marked in red.

**Visual Pin Map:** Expandable pin grid for each connector. Click any available cell to assign HS lane, clock, or discrete signal pins. Assigned pins are color-coded by type and labeled with protocol group and lane index. Pin A1 is permanently blocked (reserved for OAC_PRSNT#/M-PESTI).

**Live Validation:** Continuous schema validation in both Guided and Manual modes. Errors and warnings appear in a pane below the JSON preview with a badge count in the header.

**Import/Export:** Load any existing CID or Connector Profile JSON (auto-detected). Export as formatted or minified JSON.

**Help:** `?` button opens a modal with Getting Started guide, searchable Field Reference, Keyboard Shortcuts, and About/version info. Field-level `?` tooltip icons provide inline descriptions.

No external dependencies. See [oac-cid-editor/README.md](oac-cid-editor/README.md) for full documentation.

---

## Insertion Emulator

Load a baseboard capability JSON and an OAC CID JSON, then click Insert to run a sequenced simulation. An animated card-insertion visualization plays while the compliance engine evaluates the two schemas against each other. The event log on the right panel records every check in real time.

**Compliance checks:** input voltage, connector type (100A/125A), OPL-MAX power budget, OPL-EMG declaration, declared power excursion profile, connector impedance, high-speed lane parameters, lane pin assignments, reference clocking, required discrete signals, spec revision.

The excursion check compares the OAC's declared transient demand against the slot's transient capability in **absolute watts**, not ratio against ratio, because each document's ratios are normalized to its own `opl_max_w`. A baseboard that declares no excursion profile is assumed to support the full Base Specification Section 10.1.4 envelope, since the specification requires it to tolerate any conformant OAC. A malformed OAC profile is rejected rather than budgeted against — the log says the transient budget was not evaluated rather than reporting a PASS it did not earn.

**Verdicts:** BLOCKED (any failure — OAC_PWR_EN remains de-asserted), DEGRADED (warnings only — power enabled with reduced capability), NORMAL (all pass — full capability).

No external dependencies.

---

## Compliance Logic

A static reference diagram showing the full sequence of CID validation checks performed by the upstream management controller, their evaluated fields, and their possible outcomes (FAIL / WARN / PASS / SKIP). Thirteen checks, covering schema validation, power fields (`input_voltage`, `connector_type`, `opl_max_w`, `opl_emg_w`, `excursion`), connector profile resolution, high-speed lanes, clocking, discrete signals, and spec revision.

No external dependencies.

---

## Baseboard Schema Format

The Insertion Emulator requires a **baseboard capability JSON** in addition to the OAC CID. The baseboard file uses the same `oac_cid` structure as an OAC CID but describes the slot's capabilities rather than the OAC's requirements. Any field the baseboard does not populate is treated as undeclared (generating a WARN rather than a FAIL where applicable).

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

All three tools are v0.9 throughout, in their field sets and validation rules as well as in their
displayed version strings. The stale `0.7` and `0.8` strings that previously survived in the
Editor's About panel and export filenames and in the Insertion Emulator's header and log banner
were corrected on 2026-11-09, in the same pass that added the power excursion support.

When these tools are revised for a future schema version, the version strings to check are: the
Editor's header subtitle, its About panel rows, and the two export-filename fallbacks; the Insertion
Emulator's subtitle and its `COMPLIANCE EVALUATION` log banner; and the Compliance Logic diagram's
footer.
