#!/usr/bin/env python3
"""
CLIPキーワード翻訳スキル
日本語キーワードをCLIPモデル向けの英語検索フレーズに変換する。
OpenCodeのエージェントスキルとして呼び出されることを想定。
"""
import sys
import json
import argparse


# よく使うキーワードの翻訳辞書（フォールバック用）
BUILTIN_TRANSLATIONS = {
    "尻": [
        "a photo of buttocks",
        "a photo of a butt",
        "a person's bottom",
        "buttocks visible",
        "rear view of a person",
    ],
    "お尻": [
        "a photo of buttocks",
        "a photo of a butt",
        "a person's bottom",
    ],
    "ヒップ": [
        "a photo of hips",
        "a photo of buttocks",
        "hip line visible",
    ],
    "ビーチ": [
        "a photo of a beach",
        "a sandy beach",
        "ocean shore",
        "seaside landscape",
        "beach with waves",
    ],
    "海": [
        "a photo of the ocean",
        "a photo of the sea",
        "seascape",
        "blue ocean",
    ],
    "料理": [
        "a photo of food",
        "a photo of a meal",
        "delicious food on a plate",
        "cooked dish",
    ],
    "食べ物": [
        "a photo of food",
        "delicious meal",
        "food photography",
    ],
    "犬": [
        "a photo of a dog",
        "a cute dog",
        "dog sitting",
        "dog portrait",
    ],
    "猫": [
        "a photo of a cat",
        "a cute cat",
        "cat sitting",
        "cat portrait",
    ],
    "花": [
        "a photo of flowers",
        "beautiful flowers",
        "flower bouquet",
        "blooming flowers",
    ],
    "山": [
        "a photo of a mountain",
        "mountain landscape",
        "snowy mountain peak",
    ],
    "空": [
        "a photo of the sky",
        "blue sky with clouds",
        "sunset sky",
    ],
    "夜景": [
        "a photo of night view",
        "city nightscape",
        "night city lights",
    ],
    "車": [
        "a photo of a car",
        "car on road",
        "sports car",
    ],
    "建物": [
        "a photo of a building",
        "architecture photography",
        "modern building",
    ],
    "人物": [
        "a photo of a person",
        "portrait of a person",
        "person standing",
    ],
    "顔": [
        "a photo of a face",
        "portrait close up",
        "facial expression",
    ],
    "手": [
        "a photo of hands",
        "hand close up",
        "hands holding",
    ],
    "足": [
        "a photo of feet",
        "legs visible",
        "foot close up",
    ],
}


def translate_keywords(keywords: list[str]) -> dict:
    """日本語キーワードリストを英語フレーズ辞書に変換"""
    result = {}
    for kw in keywords:
        if kw in BUILTIN_TRANSLATIONS:
            result[kw] = BUILTIN_TRANSLATIONS[kw]
        else:
            # 辞書になければシンプルなテンプレートで生成
            result[kw] = [
                f"a photo of {kw}",
                f"a picture of {kw}",
                f"{kw} visible",
            ]
    return result


def main():
    parser = argparse.ArgumentParser(
        description="日本語キーワードをCLIP向け英語フレーズに変換"
    )
    parser.add_argument("keywords", nargs="+", help="日本語キーワード（複数可）")
    parser.add_argument("--json", action="store_true", help="JSON形式で出力")
    args = parser.parse_args()

    result = translate_keywords(args.keywords)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for jp, en_list in result.items():
            print(f"{jp}:")
            for en in en_list:
                print(f"  - {en}")


if __name__ == "__main__":
    main()