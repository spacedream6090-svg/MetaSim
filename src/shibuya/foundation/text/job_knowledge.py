"""foundation.text.job_knowledge — 仕事で知る人の知識の行(B5・改版 v2.1・役割知識の A4)。

正典
- 決定: 壁打ちの記録 ``docs/reference/wallbounce-record-2026-11-22.md`` の 2-108(A61)と 2-115(A4)
  (``11-22/2-108``・``11-22/2-115``)。
- 指示: 返事その 12 ``docs/design/prompt-2026-11-24-reply12.md`` §2-1 (b)。重なりの調べ
  ``docs/reference/duplication-audit-2026-11-23.md`` の A4。

中身
- 知識の項目 4 つ(:data:`ITEM_IDS` の順=路上飲酒・客引き・落とし物・深夜営業)。項目ごとに、文の型(v2.0 の B0 の役割知識の
  文から見出し ``[役割知識] `` を外し、値の所を穴にした)・世界の決まりの表の行の id(:data:`RULE_IDS`)・穴を埋める
  ``params`` の欄と穴の形(:data:`HOLES`)・表に行が無いときの値(:data:`HAND_PARAMS`=v2.0 の文と同じ値)を持つ。
- 由来の印: 表の行から値を読めたら :data:`BASIS_RULES`(``rules-table``)・読めなければ :data:`BASIS_HAND`(``hand``)。
  値が今のままなら、どちらでも文のバイトは v2.0 の B0 の文(見出しを外したもの)と同じ。
- 誰がどれを知るか(:data:`ROLE_ITEMS`): 役目の語(``self_words.ROLE_WORDS`` の鍵と同じ集合=試験が守る)→ 項目の id の並び。
  職業の大分類だけの人には出さない(表は役目の語だけ)。**表に無い役目の語が来たら止める**(:class:`ValueError`)。
- 行: 見出し :data:`HEAD`・1 項目 1 行・項目の順は :data:`ITEM_IDS` の順。型は凍結・値は表から。値は数字と型の固定の語だけ
  (穴の形で止める)なので、``salience`` の置き換えは通さない。
- 表の読み口: 規則の表(``get(id, asof)`` を持つ読み口・``asof`` は世界の日)か、id → 行の辞書(``params`` の欄を持つ辞書か
  ``params`` 属性を持つ行)。foundation は world を読まない(層契約)ので、読み口は呼び手が渡す。
- 数える: 役目ごとの知識の行の推定トークン(描画と同じ式 ``channels.estimate_tokens``・行ごとに改行を足した塊)と、最も長い
  役目の計(取り置きの値の候補)。

つなぎ(第351 の第 2 段): 組み立て(``runtime.systems.assemble``=規則の表を読む今の読み手の 1 つ)が、ランの始まりの日に効いて
いる行を :func:`rows_from` で id → 行の辞書に引き、描画(``mind.percept.draw.Renderer`` の ``knowledge_rows``)に渡す。描画は
役目ごとの行を作るときに 1 回だけ組み(:func:`role_blocks`)、B5 の「自分」の欄 ``[B5 自分]`` のすぐ後に置く(腕 #7 が
``facts`` のときだけ)。行の分は人ごとの群とは別に取り置く(``templates.PERSON_RESERVES`` の ``knowledge``)。今の表にあるのは
深夜営業の 1 行だけ(親の一次確認)=ほかの 3 つは手で決めた値(``hand``)。

expedient(本モジュール分・未リサーチ)
- 誰がどれを知るかの表(警察官 4・警備員 3・駅員 1・店長 2・補充 1・ほかの 20 語は 0)は手で決めた(記録 2-108)。
- 時刻の穴の形: ``params`` は ``"HH:MM"``。文の「午後」「翌朝」「翌午前」は型に固定し、時の数だけを穴にする。分が 0 でない値と、
  固定の語に合わない時(「午後」に 12〜23 時でない値・「翌朝」「翌午前」に 0〜11 時でない値)は止める。
- 金額の穴の言い方: 1 万円の倍数は「N万円」・ほかは「N円」(桁の区切りは付けない)。
- 表に行が無い・施行の前(``asof`` の日に効いている版が無い)ときは、手で決めた値(v2.0 の文と同じ値)で文を出す。
- 表に無い 3 つ(路上飲酒・客引き・落とし物)の行の id と ``params`` の欄の名は案(下書き
  ``docs/bench/analysis/revision-351/rules-rows-draft.json``)。
- 見出し ``[B5 知識] `` は発注の案(返事その 12 は見出しを決めていない)。
- 推定トークンは行ごとに改行を足した塊で数える。取り置きは最も長い役目(警察官)の塊の字数の半分の切り上げ=描画の増分の上限
  (「自分」の欄の取り置きと同じ数え方・``templates.KNOWLEDGE_LINE_TOKENS``)。
- 知識の行を出すのは腕 #7 が ``facts`` のときだけ(``label``・``none``・``facts-nojob`` では出さない=仕事の中身を見せない水準で
  仕事の知識だけが見えるのを避ける・親の当て方)。「自分」の欄が空の体(人口の行の無い体)にも出さない。
- 知識の行は凍結の散文(v2.0 の B0 の役割知識の文)なので、描画の ⑥ 省略記法の検査(「など」「等」=列挙の省略を狙う規則)の
  外に置く(B0 の散文に掛けないのと同じ扱い)。

逐次ループ宣言(P4): なし(役目 1 つにつき項目は 4 つまで・役目の表は 25 語)。
"""

from __future__ import annotations

import re
from typing import Any, Final, Iterable, Mapping

from shibuya.foundation.text.channels import estimate_tokens
from shibuya.foundation.text.normalize import LINE_SEPARATOR

__all__ = [
    "HEAD",
    "ITEM_STREET_DRINKING",
    "ITEM_TOUTING",
    "ITEM_LOST_PROPERTY",
    "ITEM_LATE_NIGHT_BUSINESS",
    "ITEM_IDS",
    "BASIS_RULES",
    "BASIS_HAND",
    "HOLE_PM_HOUR",
    "HOLE_AM_HOUR",
    "HOLE_INT",
    "HOLE_YEN",
    "HOLE_KINDS",
    "ITEM_TEMPLATES",
    "RULE_IDS",
    "HOLES",
    "HAND_PARAMS",
    "ROLE_ITEMS",
    "check_roles",
    "knowledge_items",
    "item_body",
    "knowledge",
    "knowledge_lines",
    "rows_from",
    "role_blocks",
    "block_text",
    "lines_tokens",
    "role_tokens",
    "longest_role",
]

#: 知識の行の見出し(発注の案)。
HEAD: Final[str] = "[B5 知識] "

ITEM_STREET_DRINKING: Final[str] = "street_drinking"
ITEM_TOUTING: Final[str] = "touting"
ITEM_LOST_PROPERTY: Final[str] = "lost_property"
ITEM_LATE_NIGHT_BUSINESS: Final[str] = "late_night_business"
#: 項目の id(行の順もこの順=v2.0 の B0 の並び)。
ITEM_IDS: Final[tuple[str, ...]] = (ITEM_STREET_DRINKING, ITEM_TOUTING, ITEM_LOST_PROPERTY, ITEM_LATE_NIGHT_BUSINESS)

#: 由来の印(表の行から値を読めた/手で決めた値)。
BASIS_RULES: Final[str] = "rules-table"
BASIS_HAND: Final[str] = "hand"

#: 穴の形。``pm_hour``=``"HH:MM"``(12〜23 時・分は 0)→ 時 − 12 / ``am_hour``=``"HH:MM"``(0〜11 時・分は 0)→ 時 /
#: ``int``=1 以上の整数 → そのまま / ``yen``=1 以上の整数[円] → 「N万円」(1 万円の倍数)か「N円」。
HOLE_PM_HOUR: Final[str] = "pm_hour"
HOLE_AM_HOUR: Final[str] = "am_hour"
HOLE_INT: Final[str] = "int"
HOLE_YEN: Final[str] = "yen"
HOLE_KINDS: Final[tuple[str, ...]] = (HOLE_PM_HOUR, HOLE_AM_HOUR, HOLE_INT, HOLE_YEN)

#: 文の型(v2.0 の B0 の役割知識の文から見出しを外し、値の所を穴 ``{params の欄の名}`` にした)。
ITEM_TEMPLATES: Final[Mapping[str, str]] = {
    ITEM_STREET_DRINKING: "渋谷駅周辺地域では、午後{banned_from}時から翌朝{banned_until}時までの間、路上や公園などの公共の場所での"
    "飲酒が条例で禁止されています(罰則規定はありません)。",
    ITEM_TOUTING: "渋谷駅を中心とするおおむね半径{radius_m}メートルは客引き行為等防止啓発地区です。"
    "勧告後の違反には{fine_yen}の過料があります。",
    ITEM_LOST_PROPERTY: "落とし物を拾ったときは、施設の中で拾った場合は{facility_hours}時間以内、路上で拾った場合は"
    "拾った日から{street_days}日以内に警察署等へ提出しないと、報労金請求権などの権利がなくなります。",
    ITEM_LATE_NIGHT_BUSINESS: "深夜営業等の制限は午後{restricted_from}時から翌午前{restricted_until}時までで、"
    "飲食店営業など{business_types}業種が対象です。",
}

#: 世界の決まりの表の行の id(案・足したら使う id。下書き ``docs/bench/analysis/revision-351/rules-rows-draft.json``)。
RULE_IDS: Final[Mapping[str, str]] = {
    ITEM_STREET_DRINKING: "street_drinking.shibuya_station_area",
    ITEM_TOUTING: "touting.shibuya_station_district",
    ITEM_LOST_PROPERTY: "lost_property.submission_deadline",
    ITEM_LATE_NIGHT_BUSINESS: "late_night_business.tokyo_environment_ordinance",
}

#: 穴(=表の行の ``params`` の欄の名)と穴の形。並びは文の中の順。
HOLES: Final[Mapping[str, tuple[tuple[str, str], ...]]] = {
    ITEM_STREET_DRINKING: (("banned_from", HOLE_PM_HOUR), ("banned_until", HOLE_AM_HOUR)),
    ITEM_TOUTING: (("radius_m", HOLE_INT), ("fine_yen", HOLE_YEN)),
    ITEM_LOST_PROPERTY: (("facility_hours", HOLE_INT), ("street_days", HOLE_INT)),
    ITEM_LATE_NIGHT_BUSINESS: (("restricted_from", HOLE_PM_HOUR), ("restricted_until", HOLE_AM_HOUR),
                               ("business_types", HOLE_INT)),
}

#: 表に行が無いときに使う値(v2.0 の B0 の文と同じ値=手で決めた)。
HAND_PARAMS: Final[Mapping[str, Mapping[str, Any]]] = {
    ITEM_STREET_DRINKING: {"banned_from": "18:00", "banned_until": "05:00"},
    ITEM_TOUTING: {"radius_m": 700, "fine_yen": 50000},
    ITEM_LOST_PROPERTY: {"facility_hours": 24, "street_days": 7},
    ITEM_LATE_NIGHT_BUSINESS: {"restricted_from": "23:00", "restricted_until": "06:00", "business_types": 8},
}

_ALL: Final[tuple[str, ...]] = ITEM_IDS
_NONE: Final[tuple[str, ...]] = ()

#: 誰がどれを知るか(役目の語 → 項目の id の並び)。鍵は ``self_words.ROLE_WORDS`` の鍵と同じ 25 語(試験が守る)。
#: **手で決めた(expedient・未リサーチ)**。
ROLE_ITEMS: Final[Mapping[str, tuple[str, ...]]] = {
    # 雇われた仕事
    "駅員": (ITEM_LOST_PROPERTY,),
    "電車運転士": _NONE,
    "車掌": _NONE,
    "バス運転士": _NONE,
    "タクシー運転手": _NONE,
    "指令": _NONE,
    "警察官": _ALL,
    "消防士": _NONE,
    "救急隊員": _NONE,
    "警備員": (ITEM_STREET_DRINKING, ITEM_TOUTING, ITEM_LOST_PROPERTY),
    "店長": (ITEM_LOST_PROPERTY, ITEM_LATE_NIGHT_BUSINESS),
    "補充": (ITEM_LOST_PROPERTY,),
    "清掃作業員": _NONE,
    "夜間清掃員": _NONE,
    "納品ドライバー": _NONE,
    "配送作業員": _NONE,
    "ティッシュ配り": _NONE,
    # していること
    "ストリートミュージシャン": _NONE,
    "配信者": _NONE,
    "路上占い師": _NONE,
    "街頭演説者": _NONE,
    "募金スタッフ": _NONE,
    "路上支援員": _NONE,
    "キッチンカー営業者": _NONE,
    # 住まいで扱う
    "路上生活者": _NONE,
}

_HHMM: Final[re.Pattern[str]] = re.compile(r"(\d{2}):(\d{2})", re.ASCII)


def check_roles(roles: Iterable[str]) -> None:
    """データに在る役目の語(空は除く)が全部 :data:`ROLE_ITEMS` に在るか。表に無い語があれば止める。

    Raises:
        ValueError: 知識の表に無い役目の語(黙って落とさない)。
    """
    bad = sorted({str(r) for r in roles if str(r)} - set(ROLE_ITEMS))
    if bad:
        raise ValueError(f"知識の表に無い役目の語(知識の行を組めない): {bad}")


def knowledge_items(role: str) -> tuple[str, ...]:
    """役目の語(空=役目なし)→ 知る項目の id(:data:`ITEM_IDS` の順)。表に無い語は止める。"""
    r = str(role)
    if not r:
        return ()
    got = ROLE_ITEMS.get(r)
    if got is None:
        raise ValueError(f"知識の表に無い役目の語: {r!r}")
    return tuple(i for i in ITEM_IDS if i in got)


def _hour(value: Any, lo: int, hi: int, where: str) -> int:
    m = _HHMM.fullmatch(value) if isinstance(value, str) else None
    if m is None:
        raise ValueError(f"{where} は \"HH:MM\" の文字列(いま {value!r})")
    h, mi = int(m.group(1)), int(m.group(2))
    if mi != 0 or not lo <= h <= hi:
        raise ValueError(f"{where} は {lo:02d}:00〜{hi:02d}:00 のちょうどの時(文の型の固定の語に合わない・いま {value!r})")
    return h


def _fill(kind: str, value: Any, where: str) -> str:
    """穴の形 ``kind`` の値 → 文に入れる字(数字と固定の語だけ)。形に合わない値は止める。"""
    if kind == HOLE_PM_HOUR:
        return str(_hour(value, 12, 23, where) - 12)
    if kind == HOLE_AM_HOUR:
        return str(_hour(value, 0, 11, where))
    if kind not in (HOLE_INT, HOLE_YEN):
        raise ValueError(f"{where}: 知らない穴の形 {kind!r}")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{where} は 1 以上の整数(いま {value!r})")
    if kind == HOLE_YEN:
        return f"{value // 10000}万円" if value % 10000 == 0 else f"{value}円"
    return str(value)


def _row_params(rules: Any, rule_id: str, asof: Any) -> Mapping[str, Any] | None:
    """表の読み口から行の ``params``(行が無い・施行の前は ``None``)。"""
    if rules is None:
        return None
    if isinstance(rules, Mapping):
        row = rules.get(rule_id)
    else:
        getter = getattr(rules, "get", None)
        if not callable(getter):
            raise TypeError("規則の表の読み口は get(id, asof) を持つ読み口か、id → 行の辞書")
        if asof is None:
            raise ValueError("規則の表の読み口から読むには asof(世界の日)が要る")
        try:
            row = getter(rule_id, asof)
        except LookupError:  # 表に id が無い(KeyError)・施行の前(RuleNotInForce)
            return None
    if row is None:
        return None
    params = row.get("params") if isinstance(row, Mapping) else getattr(row, "params", None)
    if not isinstance(params, Mapping):
        raise ValueError(f"規則の表の行 {rule_id!r} に params の辞書が無い")
    return params


def item_body(item_id: str, rules: Any = None, *, asof: Any = None) -> tuple[str, str]:
    """項目 1 つの文(見出しなし)と由来の印。表の行が読めれば ``rules-table``・読めなければ ``hand``(手で決めた値)。

    Raises:
        ValueError: 知らない項目・表の行の ``params`` に穴の欄が無い・穴の形に合わない値(表の誤りを黙って直さない)。
    """
    if item_id not in ITEM_TEMPLATES:
        raise ValueError(f"知らない知識の項目: {item_id!r}")
    rid = RULE_IDS[item_id]
    params = _row_params(rules, rid, asof)
    basis = BASIS_HAND if params is None else BASIS_RULES
    src = HAND_PARAMS[item_id] if params is None else params
    vals: dict[str, str] = {}
    for name, kind in HOLES[item_id]:
        if name not in src:
            raise ValueError(f"規則の表の行 {rid!r} の params に {name!r} が無い")
        vals[name] = _fill(kind, src[name], f"{rid}.params.{name}")
    return ITEM_TEMPLATES[item_id].format(**vals), basis


def knowledge(role: str, rules: Any = None, *, asof: Any = None) -> tuple[tuple[str, str, str], ...]:
    """役目の語 → ``(項目の id, 行, 由来の印)`` の並び(役目なし・知る項目なしは空)。行は見出し :data:`HEAD` つき。"""
    out: list[tuple[str, str, str]] = []
    for item in knowledge_items(role):
        body, basis = item_body(item, rules, asof=asof)
        out.append((item, HEAD + body, basis))
    return tuple(out)


def knowledge_lines(role: str, rules: Any = None, *, asof: Any = None) -> tuple[str, ...]:
    """役目の語 → 知識の行の並び(見出し ``[B5 知識] ``・1 項目 1 行・:data:`ITEM_IDS` の順)。"""
    return tuple(line for _item, line, _basis in knowledge(role, rules, asof=asof))


def rows_from(rules: Any, asof: Any) -> dict[str, dict[str, Any]]:
    """規則の表の読み口から、``asof`` の日に効いている知識の行(:data:`RULE_IDS` のうち表にある行)を id → 行の辞書
    (``{"params": {...}}``・params は写し)に引く。組み立てがランの始まりの日に 1 回だけ呼ぶ(CP10=ランは始まりの版で最後まで)。

    ``rules`` が ``None``(表の無い写し)は空の辞書。行の ``params`` の穴の欄と形は、ここでは見ない(描画が行を作るときに
    :func:`item_body` が確かめて止める)。
    """
    out: dict[str, dict[str, Any]] = {}
    for item in ITEM_IDS:
        rid = RULE_IDS[item]
        params = _row_params(rules, rid, asof)
        if params is not None:
            out[rid] = {"params": dict(params)}
    return out


def role_blocks(rules: Any = None, *, asof: Any = None) -> dict[str, str]:
    """役目の語 → 知識の行を改行でつないだ塊(末尾の改行なし・知る項目の無い役目は入れない)。描画が作るときに 1 回だけ組む。"""
    out: dict[str, str] = {}
    for role in ROLE_ITEMS:
        lines = knowledge_lines(role, rules, asof=asof)
        if lines:
            out[role] = LINE_SEPARATOR.join(lines)
    return out


def block_text(lines: Iterable[str]) -> str:
    """行の並び → 行ごとに改行を足した塊(描画が B5 に差し込む形の案・行が無ければ空文字)。"""
    return "".join(line + LINE_SEPARATOR for line in lines)


def lines_tokens(lines: Iterable[str]) -> int:
    """知識の行の推定トークン(描画と同じ式 ``estimate_tokens`` を塊に当てる・行が無ければ 0)。"""
    text = block_text(lines)
    return estimate_tokens(text) if text else 0


def role_tokens(rules: Any = None, *, asof: Any = None) -> dict[str, int]:
    """役目ごとの知識の行の推定トークン(:data:`ROLE_ITEMS` の順)。"""
    return {role: lines_tokens(knowledge_lines(role, rules, asof=asof)) for role in ROLE_ITEMS}


def longest_role(rules: Any = None, *, asof: Any = None) -> tuple[str, int]:
    """知識の行が最も長い役目と、その推定トークン(取り置きの値の候補)。同じ長さは :data:`ROLE_ITEMS` の先の語。"""
    toks = role_tokens(rules, asof=asof)
    best = max(toks.values())
    return next(r for r, t in toks.items() if t == best), best
