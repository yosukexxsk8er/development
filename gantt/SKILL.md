# ガントチャート生成 Skill（参照用）

正本は `.opencode/skills/gantt/SKILL.md` にあります。OpenCodeはそちらを自動発見して
`skill({ name: "gantt" })` で習得します。内容は正本と同一に保ってください。

要点のみ抜粋:

- AIは YAML のみ書く。HTML/CSSは直接書かない（見た目は `gantt_gen.py` の凍結CSSが保証）。
- `python gantt/gantt_gen.py <入力.yaml> -o gantt/output/<案件>.html` で生成する。
- 日付・期間・色は自動計算。厳密な形式は `schema.json` を参照。
- リファレンス: `examples/fpga.yaml` → `output/fpga.html`（20タスク / 5マイルストーン）。
