# Timing JSON

**OAC Base Specification Revision:** 0.9 (Draft)
**Format:** WaveDrom (JSON)
**Related Base Specification section:** 10.1.3 Power Brake Response and Timing (Table 28)

WaveDrom waveform diagrams for OAC sideband signal timing. WaveDrom renders a JSON description of
signals and annotated edges into an SVG timing diagram, which keeps the timing parameters reviewable
as text rather than locked inside an exported image.

---

## Contents

| File | Signal | Description |
|------|--------|-------------|
| [OAC_PWRBRK_Timing_v0.9.json](OAC_PWRBRK_Timing_v0.9.json) | `OAC_PWRBRK#` | Power brake assertion and release, with the OAC's power-level response and the three timing parameters of Table 28 |

---

## OAC_PWRBRK# Timing

`OAC_PWRBRK#` is the platform's emergency power-reduction signal. It is asserted when the platform
must shed OAC load faster than any management-path mechanism can achieve, and it takes precedence
over every software- and firmware-configured limit in effect at the time.

The diagram shows two tracks. The upper track is the `OAC_PWRBRK#` signal, idle high, asserted low,
then released. The lower track is the OAC's power level moving through four states in response:
Normal → Reducing → the emergency level → Recovering → Normal.

Three parameters are annotated as edges between the tracks:

| Parameter | Value | Meaning | Compliance |
|-----------|-------|---------|-----------|
| `Tdet` | ≤ 10 µs | From `OAC_PWRBRK#` assertion to the OAC recognizing it and beginning power reduction | **Required** |
| `Tred` | ≤ 10 ms | To complete the transition to the reduced power level | **Required** |
| `Trec` | 10 ms | To return to the prior power level after release | **Recommended** — guidance only, not a compliance requirement |

The asymmetry is deliberate. Entering the reduced state protects the platform and is therefore
bounded; leaving it does not, so recovery is advisory and a platform must not depend on the OAC
having recovered by any particular moment.

The diagram is explicitly annotated *"Timing not drawn to scale."* `Tdet` and `Tred` differ by three
orders of magnitude and cannot be drawn proportionally on one page.

---

## Rendering

Paste the file contents into [wavedrom.com/editor.html](https://wavedrom.com/editor.html), or
render locally:

```
npm install -g wavedrom-cli
wavedrom-cli -i OAC_PWRBRK_Timing_v0.9.json -s OAC_PWRBRK_Timing_v0.9.svg
```

Render to SVG for specification builds. The edge annotations carry the normative timing values and
do not survive rasterization at specification page width.

---

## A Note on the JSON

WaveDrom input is **JSON5**, not strict ECMA-404 JSON. The shipped file uses trailing commas and
empty objects as spacer rows, both of which WaveDrom accepts and a strict JSON parser rejects.

This matters only if you point tooling at this directory: do not add these files to a strict-JSON
validation sweep. It has no bearing on the management artifacts under
[`../../management/`](../../management/), which are strict ECMA-404 and are validated as such.

---

## Editing Conventions

- Use exact Base Specification signal names, including the active-low `#` suffix.
- Power levels are named, not numbered: `OPL-MAX`, `OPL-EFF`, `OPL-RED`, `OPL-EMG`, `OPL-SET1`.
- Timing parameter names match the Base Specification table that defines them — `Tdet`, `Tred`,
  `Trec` — and carry their bound inline in the edge label (`Tdet <= 10 us`), so that the rendered
  figure is readable without the accompanying table.
- Keep `"Timing not drawn to scale"` in the footer on any diagram spanning more than one order of
  magnitude.
- Avoid `#` and spaces in filenames. A `#` is a URL fragment delimiter and silently truncates direct
  links on GitHub — this file was renamed from `OAC_PWRBRK#_20260805.json` for exactly that reason.

---

## Known Issues

| Issue | Detail |
|-------|--------|
| The reduced power level is labelled `PCAP0` | The Base Specification calls this level **OPL-EMG**. `PCAP0` is terminology from an earlier draft and should be updated when the diagram is next revised |
| `Trec` is drawn with a `<=` bound | Base Specification Table 28 states `Trec` as a recommendation, not a maximum. The `<=` in the edge label overstates it |
