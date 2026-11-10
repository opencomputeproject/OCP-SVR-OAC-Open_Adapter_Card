# tools

This folder contains all tooling for authoring, validating, and visualizing OAC Connector Interface Definition (CID) documents.

## Structure

```
tools/
└── interactive/        ← Self-contained browser-based tools (open HTML directly)
    ├── oac-cid-editor/             ← Guided JSON CID authoring and editing tool
    ├── oac-cid-insertion-emulator/ ← Animated OAC insertion simulation with compliance checking
    └── oac-cid-compliance-logic/   ← Static reference diagram of the controller compliance check sequence
```

## Choosing the Right Tool

| Goal | Tool |
|------|------|
| Author a new CID document from scratch | [OAC CID Editor](interactive/oac-cid-editor/) |
| Import and inspect an existing CID file | [OAC CID Editor](interactive/oac-cid-editor/) |
| Test OAC-baseboard compatibility interactively | [OAC CID Insertion Emulator](interactive/oac-cid-insertion-emulator/) |
| Understand the upstream management controller's CID compliance check sequence | [OAC CID Compliance Logic](interactive/oac-cid-compliance-logic/) |

All interactive tools are self-contained single-file HTML pages with no server or build step required. Open them directly in any modern browser. All three are aligned to the CID v0.9 schema, including the optional `power.excursion` profile.

These tools operate on a CID document that is already in hand. Locating it is the job of the OAC Metadata file, which the upstream management controller reads first; two of the tools show that step in their sequence, but none of them performs it. See [`../../metadata/`](../../metadata/).

See [interactive/README.md](interactive/README.md) for full tool descriptions and the baseboard JSON format required by the Insertion Emulator.
