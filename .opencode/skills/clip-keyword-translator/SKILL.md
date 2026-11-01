# CLIP Keyword Translator Skill

日本語キーワードを、CLIPモデル向けの英語検索フレーズに変換するエージェントスキル。

## 使用方法

OpenCode内で以下のように呼び出す：

```
/skill clip-keyword-translator <日本語キーワード>
```

または複数キーワード：

```
/skill clip-keyword-translator 尻 ビーチ 料理
```

## 出力形式

JSON形式で標準出力。各日本語キーワードに対し、CLIP検索に適した英語フレーズ3〜5個を配列で返す。

```json
{
  "尻": [
    "a photo of buttocks",
    "a photo of a butt",
    "a person's bottom",
    "buttocks visible",
    "rear view of a person"
  ],
  "ビーチ": [
    "a photo of a beach",
    "a sandy beach",
    "ocean shore",
    "seaside landscape",
    "beach with waves"
  ]
}
```

## 翻訳方針

1. **CLIP向けテンプレート**: "a photo of X", "a picture of X", "X visible" 等の定型句を使用
2. **多様な表現**: 同義語・関連表現を複数生成し、リコール向上を狙う
3. **具体性**: 抽象的すぎず、視覚的に認識可能な表現を優先
4. **NSFW考慮**: 成人向けキーワードも適切な英語表現に変換（CLIPは一般画像で学習済み）

## 実装例（プロンプト）

```
以下の日本語キーワードを、画像検索モデル(CLIP)に最適な英語の説明文に翻訳してください。
各キーワードに対して3〜5個の英語表現を出力し、JSON形式で返してください。
CLIPは「a photo of X」「a picture of X」「X visible」等のテンプレートで高精度になります。
視覚的に具体的で、画像内で認識可能な表現を優先してください。

入力: 尻 ビーチ
出力形式: {"尻": [...], "ビーチ": [...]}
```