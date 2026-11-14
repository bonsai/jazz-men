# Atlas Data Contract

このディレクトリのJSON/JSONLがMusic Atlasの正本。画面表示用に加工したデータを別途コミットしない。文字コードはUTF-8。

## Files

| File | Top-level shape | Purpose |
|---|---|---|
| places.json | `{schema_version, places[]}` | 国・地域・都市・シーン・会場 |
| eras.json | `{schema_version, eras[]}` | 年代区間 |
| concepts.json | `{schema_version, concepts[]}` | 概念辞書 |
| works.json | `{schema_version, works[]}` | アルバム・作品 |
| relations.jsonl | 1行1オブジェクト | エンティティ間の型付き関係 |

全JSONファイルの `schema_version` は `1.0.0`。空配列は「まだ登録していない」を意味し、未知の事実を推測して補わない。

## Entity references

- `artist:<existing-artist-id>` — `data/artists.json` または `japan/artists.json` のID
- `work:<work-id>`
- `place:<place-id>`
- `concept:<concept-id>`
- `era:<era-id>`

IDは永続ID。表示名の変更でIDを変更しない。形式は小文字kebab-case。

## Field contract

### places.json

必須: `id`, `name`, `kind`, `precision`。
- `kind`: country | region | city | scene | venue
- `country_code`: ISO 3166-1 alpha-2形式、またはnull
- `latitude` / `longitude`: number or null。両方を同時に設定する
- `precision`: exact | approximate | unknown
- `sources`: URL配列

### eras.json

必須: `id`, `label`, `start_year`, `end_year`, `description`。
- 年は整数、両端を含む。start_year <= end_year。

### concepts.json

必須: `id`, `label`, `category`, `definition`。
- `category`: genre | practice | technique | philosophy | scene | sound
- `aliases` / `sources`: 配列。sourcesはURL配列。

### works.json

必須: `id`, `title`, `artist_ids`。
- `release_year` / `recording_year`: integer or null
- `place_ids` / `concept_ids` / `source_urls`: 配列
- recording_yearからrelease_yearを推定しない。

### relations.jsonl

必須: `source`, `relation`, `target`, `evidence`。
- `relation`: associated_with | influenced_by | member_of | performed_in | based_in | born_in | recorded_in | released_in_era | uses_technique | explores_concept
- `evidence`: source | editorial
- `source_urls`: URL配列
- `influenced_by`は影響関係を裏付ける出典URLがある場合のみ使用する。概念的な近さはassociated_with。

## Validation

リポジトリのルートで実行:

```sh
python scripts/validate_atlas.py
```

Python標準ライブラリのみを使用する。JSON/JSONL構文、必須形式、ID重複、参照整合性、座標範囲、年代の逆転、URL形式、関係語彙を検査する。

## Quality rules

- 事実フィールドには可能な限り出典URLを付ける。
- 不明値はnull。推測で埋めない。
- 出生地、居住地／拠点、演奏地、録音地を混同しない。
- 活動期間は生没年から自動推定しない。
- 作品の発売年と録音年は別フィールド。
- 影響関係と編集上の関連づけを区別する。
