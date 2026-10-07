# Base Specification Artifacts

**OAC Base Specification Revision:** 0.9 (Draft)

Source artifacts for the diagrams that appear in the OCP Open Adapter Card Base Specification. Each
one is a text-based model rather than an exported image, so that a diagram can be reviewed in a pull
request, diffed line by line, and regenerated at any resolution when the specification is rebuilt.

The rendered images in the published Base Specification are generated from these files. **These are
the masters.** A diagram corrected in the specification document alone will be overwritten the next
time it is regenerated.

---

## Contents

| Directory | Format | Contents |
|-----------|--------|----------|
| [sequencing_uml/](sequencing_uml/) | PlantUML (`.puml`) | Sequence diagrams of the OAC operational-state transitions, from insertion through power throttling |
| [timing_json/](timing_json/) | WaveDrom (JSON) | Waveform timing diagrams for OAC sideband signals |

---

## Scope

What belongs here: any text-based diagram or model that the Base Specification renders into its own
pages — sequence diagrams, timing waveforms, state models, and pin or mechanical tables expressed as
data.

What does not belong here: the machine-readable artifacts an OAC or a baseboard consumes at runtime.
Those are normative interfaces in their own right, with their own specifications, and they live
under [`../management/`](../management/).

The Base Specification document itself is not carried in this repository. It is published through
the OCP Contribution Portal.

---

## Rendering

Both formats render without installing anything locally.

| Format | Online | Local |
|--------|--------|-------|
| PlantUML | [plantuml.com/plantuml](https://www.plantuml.com/plantuml) | `plantuml file.puml` (requires Java and Graphviz) |
| WaveDrom | [wavedrom.com/editor.html](https://wavedrom.com/editor.html) | `wavedrom-cli -i file.json -s file.svg` (npm) |

For specification builds, render to SVG rather than PNG — the Base Specification is read at a range
of zoom levels and the signal and state labels do not survive rasterization well.

---

## Conventions

- **Filenames encode the Base Specification revision** they were authored against, e.g. `_v0.9`.
  When a diagram changes materially for a new revision, the suffix is updated in the same commit as
  the content change.
- **Operational state names are normative.** Use `O0` through `O7` exactly as the Base Specification
  Section 10.1.1 defines them, and do not invent intermediate states.
- **Signal names are normative.** Use the exact Base Specification signal name including its
  active-low `#` suffix: `OAC_PRSNT[0:6]#`, `OAC_PWR_EN`, `OAC_PWR_GD`, `OAC_PWRBRK#`, `OAC_MC_RDY`.
- **Power levels are named, not numbered.** Write `OPL-MAX`, `OPL-EFF`, `OPL-RED`, `OPL-EMG`,
  `OPL-SET1`.
- **The card is the OAC.** Not "the adapter" — that word survives only inside the proper name *Open
  Adapter Card*. The two controllers in play are distinct: *the OAC's management controller* sits on
  the card, and *the upstream management controller* sits on the baseboard. Name whichever one is
  meant; never abbreviate the latter.
- **Avoid `#` and spaces in filenames.** A `#` is a fragment delimiter in a URL and silently
  truncates any direct link to the file on GitHub.

---

## Changing a Diagram

A diagram here is referenced by the Base Specification, so a change to one is a change to the
specification. When you edit a file in this tree:

1. Confirm the state names, signal names, and timing parameters still match the current Base
   Specification text. The diagram is the thing that gets looked at — if the two disagree, the
   diagram is what readers will believe.
2. Update the `README.md` in the directory you changed. Both subdirectory READMEs describe their
   files individually.
3. Re-render and eyeball the result before committing. PlantUML and WaveDrom both accept input that
   parses but lays out badly.
