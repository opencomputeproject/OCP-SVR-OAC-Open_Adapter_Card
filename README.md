# OCP Open Adapter Card (OAC)

**Workstream:** Open Compute Project Foundation — Server Project, Open Adapter Card
**Base Specification Revision:** 0.9 (Draft)
**Document Status:** Draft

This repository is the authoritative home for the machine-readable artifacts, companion
specifications, and supporting documentation of the **OCP Open Adapter Card Base Specification**.
The Base Specification names this repository normatively as the location of the CID artifacts, the
SCD artifacts, and the required management objects and PLDM PDRs.

The Base Specification document itself is published through the OCP Contribution Portal and is not
carried here. This repository carries everything the Base Specification points *at*.

---

## What an OAC is

An Open Adapter Card is a modular add-in card form factor for OCP servers. It is installed into a
baseboard slot carrying up to seven high-speed connectors (CONN0–CONN6) plus an optional cabled
position, and it is managed over MCTP on the OAC Management USB 2.0 interface present on CONN0.

OAC slots are not hot-pluggable, and primary busbar power is substantial — up to 5 kW through the
BK125 connector variant. A baseboard therefore cannot discover an OAC by energizing it and seeing
what happens. It has to find out what the card is, and decide whether it can host it, while the card
is still running on auxiliary power alone.

That constraint is what the two companion specifications in this repository exist to satisfy.

---

## Repository Structure

```
.
├── README.md                        ← This file
├── base_specification_artifacts/    ← Diagrams and models referenced by the Base Specification
│   ├── sequencing_uml/              ← PlantUML operational-state sequence diagrams
│   └── timing_json/                 ← WaveDrom timing diagrams
└── management/                      ← The two companion management specifications
    ├── cid/                         ← Connector Interface Definition
    └── scd/                         ← Slot Configuration Data
```

Every directory carries its own `README.md` describing its contents.

---

## The Two Management Artifacts

Both are JSON documents exchanged over MCTP/PLDM in Operational State **O3 (Management
Initialized)** — after auxiliary power is good, but before `OAC_PWR_EN` is asserted.

| | [CID](management/cid/) | [SCD](management/scd/) |
|---|---|---|
| Question answered | May this OAC be powered at all? | Now that it may be, how shall it be configured? |
| Direction | OAC → upstream management controller | Definition: OAC → controller · Assignment: controller → OAC |
| Nature | **Compatibility** declaration | **Configuration** exchange |
| Replaces | Guesswork about an unenumerated card | Hardware strapping |
| Carries | Connector population, pin maps, protocol groups, clocking, power envelopes and OPLs | Slot identity, link subdivision selection, platform power budget, vendor fields |

The division between them is a single question:

> **Does the platform need this to decide whether to power the OAC at all?**
> **Yes → CID. No → SCD.**

Power envelopes live in the CID, because the platform weighs them before `OAC_PWR_EN`. The link
subdivision *menu* lives in the SCD Definition, because the platform does not need it to make the
power decision.

### Sequence

```
  1.  OAC seated, OAC_PRSNT# asserted                              O0 → O1
  2.  +12V_AUX good                                                O1 → O2
  3.  MCTP session established over CONN0 USB 2.0                  O2 → O3
  4.  Controller reads the CID            (PLDM for FRU Data)        │
  5.  Controller decides: may this card be powered?                  │ O3
  6.  Controller reads the SCD Definition (PLDM for FRU Data)        │
  7.  Controller writes the SCD Assignment (PLDM for File Transfer)  │
  8.  OAC validates and accepts                                      ▼
  9.  OAC_PWR_EN asserted, primary power up, configuration latches  O3 → O4
 10.  Reset released                                                O4 → O5
```

Steps 4 through 8 all happen on auxiliary power. If step 5 fails, the sequence stops there and the
busbar is never energized.

---

## Operational States

| State | Name | Notes |
|-------|------|-------|
| O0 | Unpowered | No power of any kind |
| O1 | Presence Detected | `OAC_PRSNT[0:6]#` asserted by seating |
| O2 | Auxiliary Power Good | +12V_AUX present |
| O3 | Management Initialized | MCTP/PLDM available; CID and SCD exchanged here |
| O4 | Primary Power Good (Held in Reset) | Busbar energized; configuration latched |
| O5 | Operational | Normal operation |
| O6 | Power Constrained | Operating at a reduced Operational Power Level |
| O7 | Emergency Power Constrained | OPL-EMG, typically entered via `OAC_PWRBRK#` |

Normal progression is O0 → O1 → O2 → O3 → O4 → O5. O5, O6, and O7 interchange under power policy.

---

## Operational Power Levels

| OPL | Required | Excursions | Description |
|-----|----------|-----------|-------------|
| OPL-MAX | Yes | Permitted | Maximum sustained power the OAC is rated for |
| OPL-EFF | No | Permitted | Efficiency-optimized operating point |
| OPL-RED | No | Not permitted | Reduced operating point |
| OPL-EMG | Yes | Not permitted | Emergency level; the `OAC_PWRBRK#` target |
| OPL-SET1 | Yes | Permitted | Platform- or user-configured operating point |

`OPL-MAX ≥ OPL-EFF ≥ OPL-RED ≥ OPL-EMG`, and any assigned OPL-SET must satisfy
`OPL-EMG ≤ OPL-SET ≤ OPL-MAX`. The OAC declares its supported OPLs and their sustained wattages in
the **CID**; the platform states the budget it is willing to supply in the **SCD**. The SCD can only
ever narrow the envelope the CID declared — a configuration document never raises a hardware limit.

---

## Where to Start

| If you are… | Start at |
|---|---|
| An OAC vendor authoring a card's management data | [management/cid/](management/cid/) then [management/scd/templates/](management/scd/templates/) |
| A baseboard or BMC implementer | [management/cid/specification/](management/cid/specification/) and [management/scd/specification/](management/scd/specification/) |
| Looking for a worked end-to-end example | [management/scd/examples/](management/scd/examples/) — matched CID + Definition + Assignment triples |
| Authoring a CID interactively | [management/cid/tools/interactive/](management/cid/tools/interactive/) — self-contained browser tools |
| Validating documents you have written | [management/scd/tools/](management/scd/tools/) — `validate-scd.py` |
| Looking for the state and timing diagrams | [base_specification_artifacts/](base_specification_artifacts/) |

---

## Normative References

The OAC management stack is built on DMTF specifications. Implementers should obtain these from
[dmtf.org](https://www.dmtf.org/standards/published_documents); they are not redistributed here.

| Reference | Document |
|-----------|----------|
| DSP0236 | Management Component Transport Protocol (MCTP) Base Specification |
| DSP0240 | PLDM Base Specification |
| DSP0241 | PLDM over MCTP Binding Specification |
| DSP0242 | PLDM for File Transfer Specification |
| DSP0248 | PLDM for Platform Monitoring and Control Specification |
| DSP0249 | PLDM State Set Specification |
| DSP0257 | PLDM for FRU Data Specification |
| ECMA-404 | JSON Data Interchange Syntax, 2nd Edition |

Each companion specification states the exact revisions it depends on in its own Section 2.

---

## Contributing

This repository is maintained by the OCP Open Adapter Card workstream. Errata, change proposals, and
new connector profile submissions should be raised as issues or pull requests against this
repository. Profiles are ratified by the workstream before merge.

All documents here are **Draft** status and subject to revision prior to final publication.

---

## License

See [LICENSE](LICENSE) at the repository root.
