# Music Atlas POC 設計

## 目的
Radiooooo型の「年代×地理」探索に、フリージャズ／実験音楽の思想・音響・技法をたどる意味的探索を加える。既存の THE SOUND LIBERATORS を拡張し、海外20人＋日本20人を初期データとして利用する。

## POC方針
- 対象は既存40人と関連作品・概念・場所。
- GEO / TIME / SEMANTIC の3画面を同時に実装。
- UTF-8 JSON / JSONLを正本とし、Gitで差分レビュー。
- 既存の vanilla JS / CSS / HTML を継続。フレームワーク・ビルド工程・外部DBなし。
- 既存のYouTube検索、Spotify、NTS RADIOへのリンクを再利用。

## 画面

### GEO MAP — #/atlas/geo
- 世界地図に国・都市・音楽シーンを表示。
- 年代・概念・人物・場所種別で絞り込み。
- 場所を選ぶと関連人物・作品・シーンを詳細パネルに表示。
- 出身地 birth_place、活動拠点 based_in、演奏地 performed_in、録音地 recorded_in を混同しない。
- POCは軽量SVGの簡略世界地図。緯度経度が未確認ならプロットせず一覧に残す。

### TIME MAP — #/atlas/time
- 1940s〜2020sを10年単位のタイムラインで表示。
- 年代を選ぶと、その時期の人物・作品・音楽シーン・概念を表示。
- 生没年、活動期間、作品発表年、録音年は別フィールド。
- 不明な年は null。推定値で埋めない。

### SEMANTIC MAP — #/atlas/semantic
- 概念ノードと関係線をSVGで可視化。
- 初期概念候補: free-improvisation, collective-improvisation, spiritual-jazz, noise, extended-technique, drone, electronic-improvisation, afro-futurism。
- ノード選択で定義・関連人物・作品・場所・年代を表示。
- 「影響」と「意味的な近さ」を区別。根拠がない因果関係を作らない。

## 共通UI
- 既存ナビゲーションに ATLAS を追加し、3画面をサブナビゲーションで切り替える。
- 共通検索と選択状態を持つ。
- 詳細パネルから既存アーティスト詳細・作品・プレイリスト・NTS RADIOへ遷移。
- モバイルでは地図／タイムラインの下に詳細を縦積み。
- 色だけに依存せず、ノード種別と関係種別をラベル・形状でも識別。

## データ配置: data/atlas/
| ファイル | 形式 | 内容 |
|---|---|---|
| places.json | JSON | 国・都市・シーンの地理情報 |
| eras.json | JSON | 年代区間と歴史的説明 |
| concepts.json | JSON | 概念辞書・定義・別名 |
| works.json | JSON | 作品の年・関連人物・場所・概念 |
| relations.jsonl | JSONL | エンティティ間の型付き関係 |

## ID規約
- 既存アーティストIDをそのまま参照する。
- 新規IDは小文字 kebab-case。
- 関係の参照先は artist:<id> / work:<id> / place:<id> / concept:<id> / era:<id>。
- IDは永続ID。表示名変更で変更しない。

## 最小データ例

places.json:
```json
{"schema_version":"1.0.0","places":[{"id":"new-york","name":"New York","name_ja":"ニューヨーク","kind":"city","country_code":"US","latitude":null,"longitude":null,"precision":"unknown","description":"","sources":[]}]}
```

eras.json:
```json
{"schema_version":"1.0.0","eras":[{"id":"1960s","label":"1960年代","start_year":1960,"end_year":1969,"description":""}]}
```

concepts.json:
```json
{"schema_version":"1.0.0","concepts":[{"id":"free-improvisation","label":"Free Improvisation","label_ja":"フリー・インプロヴィゼーション","category":"practice","definition":"","aliases":[],"sources":[]}]}
```

works.json:
```json
{"schema_version":"1.0.0","works":[{"id":"artist-album-slug","title":"","artist_ids":[],"release_year":null,"recording_year":null,"place_ids":[],"concept_ids":[],"source_urls":[]}]}
```

relations.jsonl:
```json
{"source":"artist:masayuki-takayanagi","relation":"associated_with","target":"concept:free-improvisation","evidence":"editorial","source_urls":[]}
```

## データ品質ルール
1. 事実フィールドには可能な限り出典URLを付ける。
2. null は未確認。推測値で埋めない。
3. 出身地・活動拠点・演奏地・録音地を混同しない。
4. 活動期間は生没年から自動推定しない。
5. 作品の発売年と録音年は別フィールド。
6. influenced_by は明示的な根拠がある場合だけ使う。意味的な近さは associated_with。
7. 根拠は evidence と source_urls に残す。編集者の解釈は editorial と明示。
8. 40人全員に無理にタグを付けず、確認済み情報から段階的に登録。

## 非目標
- 世界の音楽ジャンル網羅
- Spotify API連携や音源の自動再生
- 自動生成された影響関係の無検証公開
- 精密な歴史GIS
- DBサーバーや検索バックエンド

## POC完了条件
- 3画面すべてが既存サイトから到達できる。
- 3画面のフィルターが共通データを使い、人物・作品・場所・概念の詳細へ移動できる。
- JSON/JSONL構文、重複ID、存在しない参照、無効な座標、逆転した年代を検証できる。
- 未確認データを捏造せず、未配置・未設定として扱える。
- PC・モバイルで動作し、外部ライブラリなし。
