# gantt — 再現性のあるコンパクト・ガントチャート生成

AIが好みの見た目を再現よく生成するための基盤。**YAMLを書く→スクリプトでHTML化**の2段構え。

## 構成

```
gantt/
  gantt_gen.py       # 決定論レンダラ（CSS凍結、日付→%・期間・色は自動）
  SKILL.md           # 参照用（正本は .opencode/skills/gantt/SKILL.md）
  schema.json        # YAMLバリデーション用スキーマ
  README.md          # このファイル
  examples/
    fpga.yaml        # リファレンス（現行FPGAガント20タスク）
    minimal.yaml     # 最小サンプル
  output/            # 生成HTML置き場
```

スキル正本: `.opencode/skills/gantt/SKILL.md`（OpenCodeが自動発見し `skill({name:"gantt"})` で習得）。
このリポジトリをクローンした別のOpenCodeでもそのまま使える。常用マシンでは
`~/.config/opencode/skills/gantt/` にコピーすれば全リポジトリから利用できる。

## 使い方

```bash
# リファレンス再現
python gantt/gantt_gen.py gantt/examples/fpga.yaml -o gantt/output/fpga.html

# 新規（AIにYAMLを書かせてから）
python gantt/gantt_gen.py gantt/examples/xxx.yaml -o gantt/output/xxx.html
```

出力HTMLは単一ファイル・外部依存なし。Obsidianやブラウザでそのまま開ける。

## AIとの連携

1. 人間が雑に指示（「来月から○○を3ヶ月でガント化して」）。
2. AIが `SKILL.md` に従いYAML草案を作成。
3. AIが `gantt_gen.py` でHTML生成。AIはHTML/CSSを直書きしない。
4. 人間がブラウザで確認→修正はYAMLに戻って再生成（再現性維持）。

## 仕様（好みの固定点）

- コンパクト: 9px前後フォント・行高20px・左ラベル135px・1画面収まり
- 詳細: hoverツールチップ（期間+詳細）、下部サブタスク表（期間・工数・担当・成果物）
- マイルストーン: 赤ダイヤ＋ラベル
- 色: フェーズ基色のみ指定、濃淡は自動生成
- 期間: `start/end` 日付から `M/D-M/D` を自動生成し3箇所（バー・ツールチップ・表）に一貫展開

## 変更履歴メモ

- 現行 `FPGAガントチャート.html` との差: タスク幅が週バケット概算→日数精密計算に変更。
  例: 要件定義 9.09%→7.79%。より正確な位置になる意図的改善。見た目の系統は同一。
