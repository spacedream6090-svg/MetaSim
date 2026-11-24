"""foundation.arms.self_line — 「自分」の欄の状況の文の腕 #7 と年齢・性別の文の腕 #17(改版 v2.0・A07 → v2.1・記録 2-114)。

〔v2.1〕2 つの腕は、人ごとの群の頭の 1 つの「自分」の欄 ``[B5 自分]``(``foundation.text.self_words.self_field_line``)に
効く: #7 は欄の ② 状況の文に・#17 は欄の ① 年齢・性別の文に。B1 はどの水準でも空(v2.0 の B1 の行は無くなった)。
腕 #7 ``prompt-self-line``(旧名 ``prompt-kind-words``): ``--self-line {facts,label,none,facts-nojob}``(環境変数
``SHIBUYA_SELF_LINE``・:func:`set_line`)。既定 ``facts``=状況の文(状況の事実・``foundation.text.self_words``)。
``label``=ラベルの 1 文「あなたは{種別}です。」(9 語の表=腕だけの表)/``none``=状況の文を出さない/
``facts-nojob``=仕事の中身を書かず「このあたりで働いています。」(登録だけ=回すのは #7 で行の効きが分かってから・2-101)。
腕 #17 ``prompt-age-sex``(新): ``--self-age-sex {on,off}``(環境変数 ``SHIBUYA_SELF_AGE_SEX``・:func:`set_age_sex`)。既定 on
(登録だけ)。2 つとも「出さない」(none・off)なら「自分」の欄は出ない。

腕は組み立てと描画(``mind.percept.draw.Renderer`` の既定)が読む。既定と違う値は LLM の入力を変えるので、**既定と違う腕
だけ**を設定の指紋に足し(:func:`config`・鍵は manifest と同じ名=腕 #3・#15・#14 の ``salience.arms_fingerprint`` と同じ
作法・``runtime.systems.assemble``)、``cli.run`` のランの種類は腕(``arm``)に数える(環境変数だけで切り替えたときも)。
manifest の ``self_line``・``self_age_sex``。腕の文は ``templates.TEMPLATES``(凍結の指紋)に入れない。

逐次ループ宣言: なし。
"""

from __future__ import annotations

import os
from typing import Any, Final

__all__ = [
    "ENV_LINE", "ENV_AGE_SEX", "LINE_FACTS", "LINE_LABEL", "LINE_NONE", "LINE_FACTS_NOJOB", "LINES", "DEFAULT_LINE",
    "AGE_SEX_ON", "AGE_SEX_OFF", "AGE_SEX_ARMS", "DEFAULT_AGE_SEX", "ARM_NAME_LINE", "ARM_NAME_AGE_SEX", "FP_KEYS",
    "line", "set_line", "age_sex", "age_sex_on", "set_age_sex", "check_line", "check_age_sex", "is_default", "config",
]

ENV_LINE: Final[str] = "SHIBUYA_SELF_LINE"
ENV_AGE_SEX: Final[str] = "SHIBUYA_SELF_AGE_SEX"
LINE_FACTS: Final[str] = "facts"
LINE_LABEL: Final[str] = "label"
LINE_NONE: Final[str] = "none"
LINE_FACTS_NOJOB: Final[str] = "facts-nojob"
LINES: Final[tuple[str, ...]] = (LINE_FACTS, LINE_LABEL, LINE_NONE, LINE_FACTS_NOJOB)
DEFAULT_LINE: Final[str] = LINE_FACTS
AGE_SEX_ON: Final[str] = "on"
AGE_SEX_OFF: Final[str] = "off"
AGE_SEX_ARMS: Final[tuple[str, ...]] = (AGE_SEX_ON, AGE_SEX_OFF)
DEFAULT_AGE_SEX: Final[str] = AGE_SEX_ON
#: 腕の表の名(改版の案 §6・返事その 11 §2-1 (d))。
ARM_NAME_LINE: Final[str] = "prompt-self-line"
ARM_NAME_AGE_SEX: Final[str] = "prompt-age-sex"
#: 設定の指紋に足す鍵(manifest と同じ名・既定と違う腕だけ=既定のランの指紋は今のまま)。
FP_KEYS: Final[tuple[str, str]] = ("self_line", "self_age_sex")


def check_line(name: str) -> str:
    """腕 #7 の値を検査する(不正値は ``ValueError``)。"""
    v = str(name).strip().lower()
    if v not in LINES:
        raise ValueError(f"--self-line は {LINES} のどれか(いま {name!r})")
    return v


def check_age_sex(name: bool | str) -> str:
    """腕 #17 の値を検査して ``on``/``off`` にする(bool も受ける)。"""
    if isinstance(name, bool):
        return AGE_SEX_ON if name else AGE_SEX_OFF
    v = str(name).strip().lower()
    if v not in AGE_SEX_ARMS:
        raise ValueError(f"--self-age-sex は {AGE_SEX_ARMS} のどれか(いま {name!r})")
    return v


def _env(name: str, default: str, check: Any) -> str:
    raw = os.environ.get(name, "").strip()
    return check(raw) if raw else default


_LINE: str = _env(ENV_LINE, DEFAULT_LINE, check_line)
_AGE_SEX: str = _env(ENV_AGE_SEX, DEFAULT_AGE_SEX, check_age_sex)


def line() -> str:
    """いまの腕 #7(既定 ``facts``)。"""
    return _LINE


def set_line(name: str) -> None:
    """腕 #7 を選ぶ(CLI ``--self-line``・試験の切替口)。"""
    global _LINE
    _LINE = check_line(name)


def age_sex() -> str:
    """いまの腕 #17(既定 ``on``)。"""
    return _AGE_SEX


def age_sex_on() -> bool:
    return _AGE_SEX == AGE_SEX_ON


def set_age_sex(name: bool | str) -> None:
    """腕 #17 を選ぶ(CLI ``--self-age-sex``・試験の切替口)。"""
    global _AGE_SEX
    _AGE_SEX = check_age_sex(name)


def is_default() -> bool:
    """2 つとも既定か(違えばランの種類は腕)。"""
    return _LINE == DEFAULT_LINE and _AGE_SEX == DEFAULT_AGE_SEX


def config() -> dict[str, str] | None:
    """設定の指紋に出す腕(**既定と違う腕だけ**・鍵は manifest と同じ名)。2 つとも既定なら ``None``=指紋に何も足さない。"""
    out: dict[str, str] = {}
    if _LINE != DEFAULT_LINE:
        out["self_line"] = _LINE
    if _AGE_SEX != DEFAULT_AGE_SEX:
        out["self_age_sex"] = _AGE_SEX
    return out or None
