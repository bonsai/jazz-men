# Atlas Data Contract

このディレクトリのJSON/JSONLがMusic Atlasの正本。画面表示用に加工したデータを別途コミットしない。

## Files
- places.json: {schema_version, places[]}
- eras.json: {schema_version, eras[]}
- concepts.json: {schema_version, concepts[]}
- works.json: {schema_version, works[]}
- relations.jsonl: 1行につき1 relation object

## Entity references
artist:<existing-artist-id>, work:<work-id>, place:<place-id>, concept:<concept-id>, era:<era-id>

## places.json
必須: id, name, kind。
- kind: country | region | city | scene | venue
- country_code: ISO 3166-1 alpha-2。該当しない場合null。
- latitude / longitude: number or null
- precision: exact | approximate | unknown
- sources: URL配列

## eras.json
必須: id, label, start_year, end_year。年は整数かつ両端を含む。start_year <= end_year。

## concepts.json
必須: id, label, category, definition。
- category: genre | practice | technique | philosophy | scene | sound
- aliases / sources: 配列

## works.json
必須: id, title, artist_ids。
- release_year / recording_year: integer or null
- place_ids / concept_ids / source_urls: 配列
- recording_yearからrelease_yearを推定しない。

## relations.jsonl
必須: source, relation, target, evidence。
- relation: associated_with | influenced_by | member_of | performed_in | based_in | born_in | recorded_in | released_in_era | uses_technique | explores_concept
- evidence: source | editorial
- source_urls: URL配列
- influenced_byは影響関係を裏付ける出典がある場合のみ。概念的な近さはassociated_with。

## Quality
- IDは安定したkebab-case。表示名は変更可能。
- 不明値はnull。推測で埋めない。
- 出生地、居住地／拠点、演奏地、録音地を混同しない。
- すべての参照先IDと重複IDを検証する。
