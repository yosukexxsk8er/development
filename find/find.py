import argparse
import os
import re


def find_files(start_dir: str, pattern: str, output_file: str | None) -> list[str]:
    """
    指定されたディレクトリツリー内にあるファイルを検索し、結果を出力します。

    Args:
        start_dir: 検索対象となるディレクトリのパス
        pattern: 正規表現パターン
        output_file: 出力先ファイルパス (省略可能)
    """
    matches = []

    for root, _, files in os.walk(start_dir):
        for filename in files:
            if re.search(pattern, filename):
                filepath = os.path.join(root, filename)
                matches.append(filepath)
                print(filepath)

                if output_file:
                    with open(output_file, "a") as f:
                        f.write(f"{filepath}\n")

    return matches


def main():
    # 引数解析
    parser = argparse.ArgumentParser(description="ファイル検索プログラム")
    parser.add_argument("start_dir", help="検索対象となるディレクトリ")
    parser.add_argument("pattern", help="正規表現パターン")
    parser.add_argument("-o", "--output", help="出力先ファイルパス", metavar="OUTPUT_FILE")
    args = parser.parse_args()

    # 検索実行
    matched_files = find_files(args.start_dir, args.pattern, args.output)
    output_message = (
        f"検索結果を {'ファイル {args.output}' if args.output else '標準出力'} に保存しました。"
    )
    print(output_message)


if __name__ == "__main__":
    main()
