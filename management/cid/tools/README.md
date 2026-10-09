# tools

This folder contains all tooling for authoring, validating, and visualizing OAC Connector Interface Definition (CID) documents.

## Structure

```
tools/
└── interactive/        ← Self-contained browser-based tools (open HTML directly)
    ├── oac-cid-editor/             ← Guided JSON CID authoring and editing tool
    ├── oac-cid-insertion-emulator/ ← Animated OAC insertion simulation with compliance checking
    └── oac-cid-compliance-logic/   ← Static reference diagram of the BMC compliance check sequence
```

## Choosing the Right Tool

| Goal | Tool |
|------|------|
| Author a new CID document from scratch | [OAC CID Editor](interactive/oac-cid-editor/) |
| Import and inspect an existing CID file | [OAC CID Editor](interactive/oac-cid-editor/) |
| Test OAC-baseboard compatibility interactively | [OAC CID Insertion Emulator](interactive/oac-cid-insertion-emulator/) |
| Understand the BMC CID compliance check sequence | [OAC CID Compliance Logic](interactive/oac-cid-compliance-logic/) |

All interactive tools are self-contained single-file HTML pages with no server or build step required. Open them directly in any modern browser.

See [interactive/README.md](interactive/README.md) for full tool descriptions and the baseboard JSON format required by the Insertion Emulator.
