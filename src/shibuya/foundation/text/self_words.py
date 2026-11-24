"""foundation.text.self_words — 1 つの「自分」の欄 ``[B5 自分]`` の文と言い方の表(改版 v2.0・A07 → v2.1・記録 2-114)。

正典
- 決定: 壁打ちの記録 ``docs/reference/wallbounce-record-2026-11-22.md`` の 2-96〜2-101(``11-22/2-96``〜``2-101``)・
  〔v2.1〕2-111(言い方の表の直し)・2-112(家は海外)・2-114(1 つの「自分」の欄)。
- 文の形: 返事その 11 ``docs/design/prompt-2026-11-22-reply11.md`` §2-1 の (b)(状況の文の順と文)・(c)(言い方の表)・
  (d)(腕 #7)。〔v2.1〕返事その 12 ``docs/design/prompt-2026-11-24-reply12.md`` §2-1 の (a)・(c)。改版の案 §1-3 の 9 種別の
  型と §1-6 は使わない(決定で外れた)。

1 つの「自分」の欄(人ごとの群=B5 の頭の 1 行・2-114)
- 見出し ``[B5 自分]``・です・ます体。文を 1 行に続けて並べる(間に空白も改行も入れない): ① 年齢・性別の文(1 歳ごと・
  :data:`CHILD_AGE_LIMIT` 歳未満は「男の子」「女の子」・欠けた方は書かない)→ ② 状況の文(0〜3 文)。① も ② も空なら行を出さない。
  例 ``[B5 自分] 34歳の女性です。家はこのあたりの外にあります。このあたりの職場で、事務の仕事をしています。``
- v2.0 の状況の行(B1・共有静的の群)と B5 の頭の 1 文は、この 1 行にまとめた(B1 は空=どの水準でも出さない)。
- 腕: #7(``--self-line``)は ② に効く(facts=状況の文/label=「あなたは{種別}です。」の 1 文/none=② を出さない/
  facts-nojob=仕事の中身を書かない)。#17(``--self-age-sex``)は ① に効く(:func:`self_field_sentences`)。

状況の文(② の中身)
- ① 住まい(全員)→ ② ふだん通う先と仕事(当てはまる人だけ)→ ③ 今日の用事(② の文が無い人だけ)。**種別は文の選び方に
  使わない**(2-96)。文は「事実の欄の組」(:data:`SITUATION_KEY_FIELDS`)だけで決まる=同じ組の体は同じ文。
- 住まいの優先: 路上生活者の役目 → 家のセルがある → 家は海外(訪日来街者か、``is_foreign`` の付いた来街者=2-112)→
  それ以外(方面の口だけ)。
- 「このあたりで働く人」= 勤め先のセルが範囲の中か、持ち場の勤め(役目)がある人(路上生活者を除く)。役目があれば役目を、
  無ければ職業の大分類を使う(2-98)。「していること」の役目は表の文(2-99)。
- 文はこのモジュールの表からだけ組む。**表に無い語が来たら止める**(:class:`ValueError`・黙って落とさない)。

同じ事実が 2 回出ないことの確かめ(2-114): :func:`repeated_self_sentences`(全文と、その体の「自分」の欄の文の列 → 2 回以上
出た文の列)。人物の語りの行(段 10)の重なりの確かめにも使う。

expedient(本モジュール分・未リサーチ)
- **言い方の表 4 つ**(職業の大分類 11・役目 25 語・性別 2 値と子どもの 2 値・持ち場の名 38 語)の語は案(未リサーチ・
  expedient)。返事その 11 §2-1 (c): 「表は案として作って当てる。claude.ai が確かめ、住民の文として自然かはユーザーが見る」。
  〔v2.1〕直した 5 行(管理職・専門職や技術職・品出しのスタッフ・ティッシュ配りのスタッフ・持ち場の名 2 語)は記録 2-111
  (住民の文として自然か=ユーザーの判断)。
- 持ち場の名は表の言い方だけを文に入れる(データの字面を直に入れない)。内部の語「流し(bbox内)」と、場所の名でない
  「巡回ユニット」「巡回ルート」(2-111)は見せない(「このあたりで、」に倒す)。
- 子どもの言い方の区切り 18 歳(:data:`CHILD_AGE_LIMIT`)は記録 2-111 の決め(成年 18 歳・2-109 の役目の下限とそろう)。
  v2.0 の 15 歳は国勢調査の年少人口の区切りに合わせていた。
- 役目も大分類も無い「このあたりで働く人」の文「このあたりで働いています。」は決定の外の埋め合わせ(expedient)。
- 「していること」の役目の文には持ち場の名を入れない(決定の例「このあたりの通りで歌っています。」の形に揃えた)。
- 腕 ``facts-nojob`` でも「していること」の文はそのまま(2-99 で仕事でない役目とした=仕事の中身に当たらない)。
- 見出し ``[B5 自分]`` は案(返事その 11 は見出しを決めていない・2-111 で「今のまま」)。

逐次ループ宣言(P4): なし(文の組み立ては 1 体の事実の組につき 1 回=描画が組ごとに控える)。
"""

from __future__ import annotations

from typing import Final, Iterable, Mapping, Sequence

from shibuya.foundation.arms import self_line as SL

__all__ = [
    "PURPOSE_NAMES",
    "PURPOSE_BUSINESS",
    "PURPOSE_PRIVATE",
    "ROLE_EMPLOYED",
    "ROLE_DOING",
    "ROLE_HOME",
    "ROLE_CLASSES",
    "SELF_HEAD",
    "SITUATION_SENTENCES",
    "OCCUPATION_WORDS",
    "ROLE_WORDS",
    "SEX_WORDS",
    "SEX_WORDS_CHILD",
    "CHILD_AGE_LIMIT",
    "POST_WORDS",
    "post_word",
    "PROFILE_SENTENCES",
    "SITUATION_KEY_FIELDS",
    "LABEL_KIND_WORDS",
    "LABEL_TEMPLATE",
    "check_words",
    "situation_sentences",
    "profile_sentence",
    "profile_line",
    "label_sentence",
    "self_field_sentences",
    "self_field_line",
    "repeated_self_sentences",
    "self_field_lines",
    "table_rows",
]

#: W16 の目的の語(``build.pop.w16_population.PURPOSE_NAMES`` と同値・層契約で import できない=試験で守る)。
PURPOSE_NAMES: Final[tuple[str, ...]] = ("勤務", "通学", "業務", "私事", "居住", "職務")
#: 今日の用事の文を出す目的(業務=2・私事=3)。
PURPOSE_BUSINESS: Final[int] = 2
PURPOSE_PRIVATE: Final[int] = 3

#: 役目の扱いの区分: 雇われた仕事(「〜として働いています」)/していること(事実の 1 文)/住まいで扱う(路上生活者)。
ROLE_EMPLOYED: Final[str] = "employed"
ROLE_DOING: Final[str] = "doing"
ROLE_HOME: Final[str] = "home"
ROLE_CLASSES: Final[tuple[str, ...]] = (ROLE_EMPLOYED, ROLE_DOING, ROLE_HOME)

#: 「自分」の欄の見出し(v2.0 の B5 の頭の 1 文の見出しのまま=2-97・2-111「今のまま」)。〔v2.1・2-114〕v2.0 の B1 の見出し
#: ``[B1 状況]``(と腕 label の ``[B1 種別]``)は住民に見える字面から無くなった。
SELF_HEAD: Final[str] = "[B5 自分] "

#: 状況の文(返事その 11 §2-1 (b) の文のまま。``{post}``・``{role}``・``{occupation}`` は言い方の表の語)。
SITUATION_SENTENCES: Final[Mapping[str, str]] = {
    # ① 住まい
    "home_here": "家はこのあたりにあります。",
    "home_abroad": "家は海外にあります。",
    "home_none": "決まった家はなく、このあたりで寝起きしています。",
    "home_outside": "家はこのあたりの外にあります。",
    # ② ふだん通う先と仕事
    "job_role_post": "{post}で、{role}として働いています。",
    "job_role": "このあたりで、{role}として働いています。",
    "job_occupation": "このあたりの職場で、{occupation}の仕事をしています。",
    "job_plain": "このあたりで働いています。",  # expedient(役目も大分類も無い人)・腕 facts-nojob
    "school": "このあたりの学校に通っています。",
    "outbound": "ふだんはこのあたりの外へ通っています。",
    # ③ 今日の用事
    "errand_business": "仕事の用事で来ています。",
    "errand_private": "自分の用事で来ています。",
}

#: ① 職業の大分類 12(W21 の ``persona_occupation``=日本標準職業分類の大分類の名)→ 「〜の仕事をしています」の〜。
#: 区分の名は文に出さない(2-96)。**案(未リサーチ・expedient)**。〔v2.1・2-111〕管理職・専門職や技術職に直した。
OCCUPATION_WORDS: Final[Mapping[str, str]] = {
    "管理的職業従事者": "管理職",
    "専門的・技術的職業従事者": "専門職や技術職",
    "事務従事者": "事務",
    "販売従事者": "販売",
    "サービス職業従事者": "接客やサービス",
    "保安職業従事者": "警備や保安",
    "農林漁業従事者": "農業や漁業",
    "生産工程従事者": "ものづくり",
    "輸送・機械運転従事者": "運転や輸送",
    "建設・採掘従事者": "建設",
    "運搬・清掃・包装等従事者": "運搬や清掃",
}

#: ② 役目の語(母集団の ``duty_role`` の値・データに在る全部)→ (区分, 言い方)。雇われた仕事=「〜として働いています」の〜・
#: していること=事実の 1 文・住まいで扱う=住まいの文(言い方は空)。区分は 2-99 の対象の並び(路上生活者・配信者・
#: ストリートミュージシャン・募金スタッフ・街頭演説者・路上支援員「など」)に路上占い師とキッチンカー営業者(自営)を足した。
#: **案(未リサーチ・expedient)**。〔v2.1・2-111〕補充 → 品出しのスタッフ・ティッシュ配り → ティッシュ配りのスタッフ。
ROLE_WORDS: Final[Mapping[str, tuple[str, str]]] = {
    # 雇われた仕事
    "駅員": (ROLE_EMPLOYED, "駅員"),
    "電車運転士": (ROLE_EMPLOYED, "電車の運転士"),
    "車掌": (ROLE_EMPLOYED, "車掌"),
    "バス運転士": (ROLE_EMPLOYED, "バスの運転士"),
    "タクシー運転手": (ROLE_EMPLOYED, "タクシーの運転手"),
    "指令": (ROLE_EMPLOYED, "指令員"),
    "警察官": (ROLE_EMPLOYED, "警察官"),
    "消防士": (ROLE_EMPLOYED, "消防士"),
    "救急隊員": (ROLE_EMPLOYED, "救急隊員"),
    "警備員": (ROLE_EMPLOYED, "警備員"),
    "店長": (ROLE_EMPLOYED, "店長"),
    "補充": (ROLE_EMPLOYED, "品出しのスタッフ"),
    "清掃作業員": (ROLE_EMPLOYED, "清掃員"),
    "夜間清掃員": (ROLE_EMPLOYED, "夜間の清掃員"),
    "納品ドライバー": (ROLE_EMPLOYED, "納品のドライバー"),
    "配送作業員": (ROLE_EMPLOYED, "配送の作業員"),
    "ティッシュ配り": (ROLE_EMPLOYED, "ティッシュ配りのスタッフ"),
    # していること(事実の 1 文)
    "ストリートミュージシャン": (ROLE_DOING, "このあたりの通りで歌っています。"),
    "配信者": (ROLE_DOING, "このあたりで配信をしています。"),
    "路上占い師": (ROLE_DOING, "このあたりの路上で占いをしています。"),
    "街頭演説者": (ROLE_DOING, "このあたりの街頭で演説をしています。"),
    "募金スタッフ": (ROLE_DOING, "このあたりで募金を呼びかけています。"),
    "路上支援員": (ROLE_DOING, "このあたりで、路上で暮らす人の相談に乗っています。"),
    "キッチンカー営業者": (ROLE_DOING, "このあたりでキッチンカーの店を出しています。"),
    # 住まいで扱う(役目の語としては出さない=2-99)
    "路上生活者": (ROLE_HOME, ""),
}

#: ③ 性別の値(``AgentState.sex``・W16 の ``sex``: 0=男・1=女)→ 言い方。**案(未リサーチ・expedient)**。
SEX_WORDS: Final[Mapping[int, str]] = {0: "男性", 1: "女性"}
#: 同(:data:`CHILD_AGE_LIMIT` 歳未満の体)。年齢が無く性別だけの体は :data:`SEX_WORDS`。**案(未リサーチ・expedient)**。
SEX_WORDS_CHILD: Final[Mapping[int, str]] = {0: "男の子", 1: "女の子"}
#: 子どもの言い方を使う年齢の区切り(この歳未満)。**案(未リサーチ・expedient)**。〔v2.1・2-111〕15 → 18(成年 18 歳・
#: 2-109 の役目の下限とそろう)。v2.0 は国勢調査の年少人口の区切り(0〜14 歳)に合わせていた。
CHILD_AGE_LIMIT: Final[int] = 18

#: ④ 持ち場の名(W16 の持ち場の表 ``w16_duty_roster.parquet`` の ``post``・データに在る 38 語の全部)→ 見せる言い方。
#: ``None``=見せない(文は持ち場が無いときと同じ「このあたりで、{役目}として働いています。」)。「自分」の欄に入る語は全部この表の
#: 言い方だけ(データの字面を直に入れない=返事その 11 §2-1 (c)「文はこの表からだけ組む」)。表に無い持ち場が来たら止める。
#: 「流し(bbox内)」は内部の語なので見せない。〔v2.1・2-111〕「巡回ユニット」「巡回ルート」は場所の名でないので見せない。
#: ほかの 35 語は今の語のまま見せる(言い方=同じ語)。**案(未リサーチ・expedient)**。
POST_WORDS: Final[Mapping[str, str | None]] = {
    **{w: w for w in (
        "オフィスビル", "オフィス街の広場", "スクランブル交差点", "センター街", "センター街入口", "ハチ公前", "マークシティ",
        "公園そばの空地", "公園のそば", "公園通り", "区の相談窓口", "区役所前", "南口", "商店街入口", "商業ビル", "地下通路",
        "宮下パーク", "宮益坂の路地", "宮益坂乗場", "救急待機所", "東口ターミナル",
        "消防出張所", "西口ターミナル", "運行指令所", "道玄坂の裏通り", "道玄坂乗場", "駅の周辺", "駅ハチ公口",
        "駅前ロータリー", "駅前広場", "駅周辺のビル", "駅東口", "駅東口の路地", "駅西口", "高架下",
    )},
    "巡回ユニット": None,
    "巡回ルート": None,
    "流し(bbox内)": None,
}

#: 年齢・性別の文(「自分」の欄の ① の文・2-97)。見出しは付けない(欄の見出しは :data:`SELF_HEAD`)。数と字の間に空白を
#: 入れない(リポの凍結の文の作法)。
PROFILE_SENTENCES: Final[Mapping[str, str]] = {
    "age_sex": "{age}歳の{sex}です。",
    "age": "{age}歳です。",
    "sex": "{sex}です。",
}

#: 状況の文を決める事実の欄(``foundation.ports.percept.SelfView`` の欄の名と並び)。描画はこの組(と年齢・性別)で欄を控える。
SITUATION_KEY_FIELDS: Final[tuple[str, ...]] = (
    "facts_known", "home_here", "home_abroad", "work_here", "school_here", "outbound", "role", "post", "occupation",
    "purpose",
)

#: 腕 #7 の ``label`` の 1 文と 9 語の表(**腕だけの表**=``templates.TEMPLATES`` と凍結の指紋に入れない)。
#: 索引は ``AgentKind`` の値(0〜8)。〔v2.1〕文は「自分」の欄の ② に入る=見出し ``[B1 種別] `` を外した。
LABEL_KIND_WORDS: Final[tuple[str, ...]] = (
    "通勤者", "来街者", "従業者", "居住者", "指令", "通学者", "定期来街者", "訪日来街者", "乗務員",
)
LABEL_TEMPLATE: Final[str] = "あなたは{kind}です。"


def check_words(roles: Iterable[str] = (), occupations: Iterable[str] = (), sexes: Iterable[int] = (),
                posts: Iterable[str] = ()) -> None:
    """データに在る語が全部言い方の表に在るか(空の語と性別 −1=欠けは除く)。表に無い語があれば止める。

    Raises:
        ValueError: 表に無い役目・大分類・性別の値・持ち場の名(黙って落とさない)。
    """
    bad_r = sorted({str(r) for r in roles if str(r)} - set(ROLE_WORDS))
    bad_o = sorted({str(o) for o in occupations if str(o)} - set(OCCUPATION_WORDS))
    bad_s = sorted({int(s) for s in sexes if int(s) >= 0} - set(SEX_WORDS))
    bad_p = sorted({str(p) for p in posts if str(p)} - set(POST_WORDS))
    if bad_r or bad_o or bad_s or bad_p:
        raise ValueError(
            f"言い方の表に無い語(「自分」の欄の文を組めない): 役目 {bad_r}・大分類 {bad_o}・性別 {bad_s}・持ち場 {bad_p}"
        )


def _role(role: str) -> tuple[str, str]:
    got = ROLE_WORDS.get(str(role))
    if got is None:
        raise ValueError(f"言い方の表に無い役目の語: {role!r}")
    return got


def post_word(post: str) -> str:
    """持ち場の名(データの語・空=無し)→ 見せる言い方(見せない語と無しは空文字)。表に無い名は止める。"""
    p = str(post)
    if not p:
        return ""
    if p not in POST_WORDS:
        raise ValueError(f"言い方の表に無い持ち場の名: {p!r}")
    return POST_WORDS[p] or ""


def situation_sentences(
    facts_known: bool, home_here: bool, home_abroad: bool, work_here: bool, school_here: bool, outbound: bool,
    role: str, post: str, occupation: str, purpose: int, *, job_content: bool = True,
) -> tuple[str, ...]:
    """事実の欄の組 → 状況の文(「自分」の欄の ②・0〜3 文・返事その 11 §2-1 (b) の順)。``facts_known`` が偽(人口の行の
    無い体)は空。

    ``job_content=False``(腕 ``facts-nojob``)は雇われた仕事と大分類の文を「このあたりで働いています。」にする。

    Raises:
        ValueError: 表に無い役目・大分類の語・持ち場の名。
    """
    if not facts_known:
        return ()
    S = SITUATION_SENTENCES
    rcls, rword = _role(role) if role else ("", "")
    shown = post_word(post)  # 持ち場の表の言い方だけ(見せない語・無しは空=「このあたりで、」)・表に無い名は止める
    out: list[str] = []
    # ① 住まい(路上生活者 → 家のセル → 海外 → それ以外)
    if rcls == ROLE_HOME:
        out.append(S["home_none"])
    elif home_here:
        out.append(S["home_here"])
    elif home_abroad:
        out.append(S["home_abroad"])
    else:
        out.append(S["home_outside"])
    # ② ふだん通う先と仕事(路上生活者には仕事の文を出さない)
    second = False
    works = rcls != ROLE_HOME and (bool(work_here) or rcls in (ROLE_EMPLOYED, ROLE_DOING))
    if works:
        if rcls == ROLE_DOING:
            out.append(rword)
        elif not job_content:
            out.append(S["job_plain"])
        elif rcls == ROLE_EMPLOYED:
            out.append(S["job_role_post"].format(post=shown, role=rword) if shown
                       else S["job_role"].format(role=rword))
        elif occupation:
            word = OCCUPATION_WORDS.get(str(occupation))
            if word is None:
                raise ValueError(f"言い方の表に無い職業の大分類: {occupation!r}")
            out.append(S["job_occupation"].format(occupation=word))
        else:
            out.append(S["job_plain"])  # expedient(役目も大分類も無い人)
        second = True
    if school_here:
        out.append(S["school"])
        second = True
    if not second and home_here and outbound and rcls != ROLE_HOME:
        out.append(S["outbound"])
        second = True
    # ③ 今日の用事(② の文が無い人だけ・業務か私事)
    if not second:
        if int(purpose) == PURPOSE_BUSINESS:
            out.append(S["errand_business"])
        elif int(purpose) == PURPOSE_PRIVATE:
            out.append(S["errand_private"])
    return tuple(out)


def profile_sentence(age: int, sex: int) -> str:
    """年齢(1 歳ごと・−1=欠け)と性別の値(−1=欠け)→ 「自分」の欄の ① の文(見出しなし・両方欠ければ空文字)。

    :data:`CHILD_AGE_LIMIT` 歳未満は子どもの言い方(「男の子」「女の子」)。年齢が無く性別だけの体は「男性」「女性」。

    Raises:
        ValueError: 表に無い性別の値。
    """
    a = int(age)
    s = int(sex)
    word = ""
    if s >= 0:
        word = SEX_WORDS.get(s, "")
        if not word:
            raise ValueError(f"言い方の表に無い性別の値: {s}")
        if 0 <= a < CHILD_AGE_LIMIT:
            word = SEX_WORDS_CHILD[s]
    if a >= 0 and word:
        return PROFILE_SENTENCES["age_sex"].format(age=a, sex=word)
    if a >= 0:
        return PROFILE_SENTENCES["age"].format(age=a)
    if word:
        return PROFILE_SENTENCES["sex"].format(sex=word)
    return ""


def profile_line(age: int, sex: int) -> str:
    """年齢・性別の文だけの「自分」の欄 ``[B5 自分] 34歳の女性です。``(状況の文の無い欄と同じ形・両方欠ければ空文字)。"""
    s = profile_sentence(age, sex)
    return SELF_HEAD + s if s else ""


def label_sentence(kind: int) -> str:
    """腕 #7 ``label``: 種別の値 → 「あなたは{種別}です。」(「自分」の欄の ② に入る 1 文・9 語の表に無い値は止める)。"""
    k = int(kind)
    if not 0 <= k < len(LABEL_KIND_WORDS):
        raise ValueError(f"腕 label の種別の表に無い値: {k}")
    return LABEL_TEMPLATE.format(kind=LABEL_KIND_WORDS[k])


def self_field_sentences(
    facts: Sequence[object], age: int, sex: int, kind: int, *, line: str = SL.DEFAULT_LINE, age_sex: bool = True,
) -> tuple[str, ...]:
    """1 体の事実 → 「自分」の欄の文の列(① 年齢・性別の文 → ② 状況の文の順・空の文は入れない)。

    Args:
        facts: 状況の文を決める事実の欄の組(:data:`SITUATION_KEY_FIELDS` の並び)。腕 ``label``・``none`` では読まない。
        age: 1 歳ごとの年齢(−1=欠け)。
        sex: 性別の値(−1=欠け)。
        kind: 種別の値(腕 ``label`` だけが読む)。
        line: 腕 #7 の水準(``foundation.arms.self_line.LINES``)。② に効く。
        age_sex: 腕 #17(真=on)。① に効く。

    Raises:
        ValueError: 腕の水準が表に無い・表に無い語・性別の値・種別の値。
    """
    mode = SL.check_line(line)
    out: list[str] = []
    if age_sex:
        p = profile_sentence(age, sex)
        if p:
            out.append(p)
    if mode == SL.LINE_LABEL:
        out.append(label_sentence(kind))
    elif mode != SL.LINE_NONE:
        out.extend(situation_sentences(*facts, job_content=(mode == SL.LINE_FACTS)))  # type: ignore[arg-type]
    return tuple(out)


def self_field_line(
    facts: Sequence[object], age: int, sex: int, kind: int, *, line: str = SL.DEFAULT_LINE, age_sex: bool = True,
) -> str:
    """1 体の事実 → ``[B5 自分] …`` の 1 行(文を間を空けずに続ける・文が無ければ空文字=行を出さない)。"""
    sents = self_field_sentences(facts, age, sex, kind, line=line, age_sex=age_sex)
    return SELF_HEAD + "".join(sents) if sents else ""


def repeated_self_sentences(text: str, sentences: Iterable[str]) -> tuple[str, ...]:
    """同じ事実が 2 回出ていないかの確かめ(記録 2-114)。全文 ``text`` に 2 回以上出る文を返す(空=重なりなし)。

    ``sentences`` はその体の「自分」の欄の文の列(:func:`self_field_sentences`)。人物の語りの行(段 10)を足した全文にも
    同じ形で使う。並びは ``sentences`` の順・同じ文は 1 回だけ返す。数え方は字面の重ならない出現の数(``str.count``)。
    """
    body = str(text)
    return tuple(s for s in dict.fromkeys(str(x) for x in sentences) if s and body.count(s) > 1)


def self_field_lines(text: str) -> tuple[str, ...]:
    """描画の文(B5 の本文か全文)から「自分」の欄の行(見出し :data:`SELF_HEAD` で始まる行)だけを並びのまま取り出す
    (〔v2.1・記録 2-114〕判断モデル向けの短い版に「自分」の欄を入れる・``foundation.ports.decision.compose``)。

    ほかの見出しの行(``[B5 知識] ``・``[B5 所持] `` など)と見出しの無い行は取らない。欄が無ければ空。
    """
    return tuple(ln for ln in str(text).split("\n") if ln.startswith(SELF_HEAD))


def table_rows() -> list[tuple[str, str, str, str]]:
    """言い方の表の全行 ``(表, データの語, 区分, 言い方)``(報告と README 用・職業 11・役目 25・性別 4・持ち場 38=78 行)。"""
    rows: list[tuple[str, str, str, str]] = []
    for k, v in OCCUPATION_WORDS.items():
        rows.append(("職業の大分類", k, "", v))
    for k, (c, v) in ROLE_WORDS.items():
        rows.append(("役目", k, c, v))
    for s, v in SEX_WORDS.items():
        rows.append(("性別", str(s), f"{CHILD_AGE_LIMIT} 歳以上か年齢なし", v))
    for s, v in SEX_WORDS_CHILD.items():
        rows.append(("性別", str(s), f"{CHILD_AGE_LIMIT} 歳未満", v))
    for k, v in POST_WORDS.items():
        rows.append(("持ち場の名", k, "見せる" if v else "見せない", v or "(このあたりで、)"))
    return rows
