# 히라가나와 가타카나 학습용 문자 데이터를 제공한다.
from __future__ import annotations

KanaEntry = tuple[str, str]


HIRAGANA: tuple[KanaEntry, ...] = (
    ("あ", "a"),
    ("い", "i"),
    ("う", "u"),
    ("え", "e"),
    ("お", "o"),
    ("か", "ka"),
    ("き", "ki"),
    ("く", "ku"),
    ("け", "ke"),
    ("こ", "ko"),
    ("さ", "sa"),
    ("し", "shi"),
    ("す", "su"),
    ("せ", "se"),
    ("そ", "so"),
    ("た", "ta"),
    ("ち", "chi"),
    ("つ", "tsu"),
    ("て", "te"),
    ("と", "to"),
    ("な", "na"),
    ("に", "ni"),
    ("ぬ", "nu"),
    ("ね", "ne"),
    ("の", "no"),
    ("は", "ha"),
    ("ひ", "hi"),
    ("ふ", "fu"),
    ("へ", "he"),
    ("ほ", "ho"),
    ("ま", "ma"),
    ("み", "mi"),
    ("む", "mu"),
    ("め", "me"),
    ("も", "mo"),
    ("や", "ya"),
    ("ゆ", "yu"),
    ("よ", "yo"),
    ("ら", "ra"),
    ("り", "ri"),
    ("る", "ru"),
    ("れ", "re"),
    ("ろ", "ro"),
    ("わ", "wa"),
    ("を", "wo"),
    ("ん", "n"),
)

KATAKANA: tuple[KanaEntry, ...] = (
    ("ア", "a"),
    ("イ", "i"),
    ("ウ", "u"),
    ("エ", "e"),
    ("オ", "o"),
    ("カ", "ka"),
    ("キ", "ki"),
    ("ク", "ku"),
    ("ケ", "ke"),
    ("コ", "ko"),
    ("サ", "sa"),
    ("シ", "shi"),
    ("ス", "su"),
    ("セ", "se"),
    ("ソ", "so"),
    ("タ", "ta"),
    ("チ", "chi"),
    ("ツ", "tsu"),
    ("テ", "te"),
    ("ト", "to"),
    ("ナ", "na"),
    ("ニ", "ni"),
    ("ヌ", "nu"),
    ("ネ", "ne"),
    ("ノ", "no"),
    ("ハ", "ha"),
    ("ヒ", "hi"),
    ("フ", "fu"),
    ("ヘ", "he"),
    ("ホ", "ho"),
    ("マ", "ma"),
    ("ミ", "mi"),
    ("ム", "mu"),
    ("メ", "me"),
    ("モ", "mo"),
    ("ヤ", "ya"),
    ("ユ", "yu"),
    ("ヨ", "yo"),
    ("ラ", "ra"),
    ("リ", "ri"),
    ("ル", "ru"),
    ("レ", "re"),
    ("ロ", "ro"),
    ("ワ", "wa"),
    ("ヲ", "wo"),
    ("ン", "n"),
)

HIRAGANA_MARKS: tuple[KanaEntry, ...] = (
    ("が", "ga"),
    ("ぎ", "gi"),
    ("ぐ", "gu"),
    ("げ", "ge"),
    ("ご", "go"),
    ("ざ", "za"),
    ("じ", "ji"),
    ("ず", "zu"),
    ("ぜ", "ze"),
    ("ぞ", "zo"),
    ("だ", "da"),
    ("ぢ", "ji"),
    ("づ", "zu"),
    ("で", "de"),
    ("ど", "do"),
    ("ば", "ba"),
    ("び", "bi"),
    ("ぶ", "bu"),
    ("べ", "be"),
    ("ぼ", "bo"),
    ("ぱ", "pa"),
    ("ぴ", "pi"),
    ("ぷ", "pu"),
    ("ぺ", "pe"),
    ("ぽ", "po"),
)

KATAKANA_MARKS: tuple[KanaEntry, ...] = (
    ("ガ", "ga"),
    ("ギ", "gi"),
    ("グ", "gu"),
    ("ゲ", "ge"),
    ("ゴ", "go"),
    ("ザ", "za"),
    ("ジ", "ji"),
    ("ズ", "zu"),
    ("ゼ", "ze"),
    ("ゾ", "zo"),
    ("ダ", "da"),
    ("ヂ", "ji"),
    ("ヅ", "zu"),
    ("デ", "de"),
    ("ド", "do"),
    ("バ", "ba"),
    ("ビ", "bi"),
    ("ブ", "bu"),
    ("ベ", "be"),
    ("ボ", "bo"),
    ("パ", "pa"),
    ("ピ", "pi"),
    ("プ", "pu"),
    ("ペ", "pe"),
    ("ポ", "po"),
)

HIRAGANA_YOON: tuple[KanaEntry, ...] = (
    ("きゃ", "kya"),
    ("きゅ", "kyu"),
    ("きょ", "kyo"),
    ("しゃ", "sha"),
    ("しゅ", "shu"),
    ("しょ", "sho"),
    ("ちゃ", "cha"),
    ("ちゅ", "chu"),
    ("ちょ", "cho"),
    ("にゃ", "nya"),
    ("にゅ", "nyu"),
    ("にょ", "nyo"),
    ("ひゃ", "hya"),
    ("ひゅ", "hyu"),
    ("ひょ", "hyo"),
    ("みゃ", "mya"),
    ("みゅ", "myu"),
    ("みょ", "myo"),
    ("りゃ", "rya"),
    ("りゅ", "ryu"),
    ("りょ", "ryo"),
    ("ぎゃ", "gya"),
    ("ぎゅ", "gyu"),
    ("ぎょ", "gyo"),
    ("じゃ", "ja"),
    ("じゅ", "ju"),
    ("じょ", "jo"),
    ("びゃ", "bya"),
    ("びゅ", "byu"),
    ("びょ", "byo"),
    ("ぴゃ", "pya"),
    ("ぴゅ", "pyu"),
    ("ぴょ", "pyo"),
)

KATAKANA_YOON: tuple[KanaEntry, ...] = (
    ("キャ", "kya"),
    ("キュ", "kyu"),
    ("キョ", "kyo"),
    ("シャ", "sha"),
    ("シュ", "shu"),
    ("ショ", "sho"),
    ("チャ", "cha"),
    ("チュ", "chu"),
    ("チョ", "cho"),
    ("ニャ", "nya"),
    ("ニュ", "nyu"),
    ("ニョ", "nyo"),
    ("ヒャ", "hya"),
    ("ヒュ", "hyu"),
    ("ヒョ", "hyo"),
    ("ミャ", "mya"),
    ("ミュ", "myu"),
    ("ミョ", "myo"),
    ("リャ", "rya"),
    ("リュ", "ryu"),
    ("リョ", "ryo"),
    ("ギャ", "gya"),
    ("ギュ", "gyu"),
    ("ギョ", "gyo"),
    ("ジャ", "ja"),
    ("ジュ", "ju"),
    ("ジョ", "jo"),
    ("ビャ", "bya"),
    ("ビュ", "byu"),
    ("ビョ", "byo"),
    ("ピャ", "pya"),
    ("ピュ", "pyu"),
    ("ピョ", "pyo"),
)

CONFUSING_PAIRS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "hiragana": (
        ("し", "つ", "し는 왼쪽 열림 / つ는 오른쪽 열림"),
        ("そ", "ん", "そ는 점이 붙고, ん은 짧게 끝"),
        ("ぬ", "め", "ぬ=고리+꼬리 / め=고리 단단히 닫힘"),
        ("ね", "れ", "ね=막대+배(고리) / れ=고리 없음"),
        ("わ", "れ", "わ 끝에 작은 점 느낌 / れ는 크게 휨"),
    ),
    "katakana": (
        ("シ", "ツ", "シ는 왼쪽 열림 / ツ는 오른쪽 열림"),
        ("ソ", "ン", "ソ는 점이 붙고, ン은 짧게 끝"),
        ("ヌ", "メ", "ヌ=고리+꼬리 / メ=고리 단단히 닫힘"),
        ("ネ", "レ", "ネ=막대+배(고리) / レ=고리 없음"),
        ("ワ", "レ", "ワ 끝에 작은 점 느낌 / レ는 크게 휨"),
    ),
}

READING_EXAMPLES: dict[str, tuple[tuple[str, str, str, str], ...]] = {
    "hiragana": (
        ("きょう", "kyou", "쿄우", "오늘/오늘날; 今日"),
        ("しゃしん", "shashin", "샤신", "사진"),
        ("りょこう", "ryokou", "료코-", "여행"),
        ("にゃん", "nyan", "냥/냥~", "고양이 울음 흉내"),
        ("おちゃ", "ocha", "오챠", "차"),
    ),
    "katakana": (
        ("キョウ", "kyou", "쿄우", "오늘/오늘날; 今日"),
        ("シャシン", "shashin", "샤신", "사진"),
        ("リョコウ", "ryokou", "료코우", "여행"),
        ("ニャン", "nyan", "냥/냥~", "고양이 울음 흉내"),
        ("オチャ", "ocha", "오챠", "차"),
    ),
}

SOKUON_EXAMPLES: dict[str, tuple[tuple[str, str, str, str], ...]] = {
    "hiragana": (
        ("がっこう", "gakkou", "가(ㄲ)꼬-", "학교"),
        ("きって", "kitte", "킷테", "우표"),
        ("ちょっと", "chotto", "춋토/춋또", "조금"),
        ("べっさつ", "bessatsu", "벳사츠", "별책"),
    ),
    "katakana": (
        ("ガッコウ", "gakkou", "가(ㄲ)꼬우", "학교"),
        ("キッテ", "kitte", "킷테", "우표"),
        ("チョット", "chotto", "춋토/춋또", "조금"),
        ("ベッサツ", "bessatsu", "벳사츠", "별책"),
    ),
}

PARTICLES: tuple[dict[str, object], ...] = (
    {
        "particle": "は",
        "reading": "wa",
        "meaning": "은/는",
        "note": "주제를 표시하며 발음은 하가 아니라 와.",
        "examples": ("わたしは学生です。", "これはペンです。"),
    },
    {
        "particle": "が",
        "reading": "ga",
        "meaning": "이/가",
        "note": "주어, 처음 등장하는 정보, 강조에 자주 쓴다.",
        "examples": ("ねこがいます。", "だれが来ますか？"),
    },
    {
        "particle": "を",
        "reading": "o",
        "meaning": "을/를",
        "note": "목적어를 표시하며 발음은 오.",
        "examples": ("パンを食べます。", "映画を見ます。"),
    },
    {
        "particle": "の",
        "reading": "no",
        "meaning": "의 / ~의 것 / 소유·소속",
        "note": "A의 B, 내 것 같은 소유 관계를 나타낸다.",
        "examples": ("わたしの本。", "これはだれのですか？"),
    },
    {
        "particle": "に",
        "reading": "ni",
        "meaning": "에 / 에게",
        "note": "시간, 도착점, 대상을 나타낸다.",
        "examples": ("3時に来ます。", "学校に行きます。", "先生に聞きます。"),
    },
    {
        "particle": "で",
        "reading": "de",
        "meaning": "에서 / 로",
        "note": "행동이 일어나는 장소나 수단을 나타낸다.",
        "examples": ("学校で勉強します。", "バスで行きます。"),
    },
    {
        "particle": "へ",
        "reading": "e",
        "meaning": "~로",
        "note": "방향을 나타내며 보통 에처럼 발음한다.",
        "examples": ("日本へ行きます。",),
    },
    {
        "particle": "と",
        "reading": "to",
        "meaning": "와/과 / ~라고",
        "note": "대상 연결이나 말·생각의 인용에 쓴다.",
        "examples": ("友だちと行きます。", "「行きたい」と言いました。"),
    },
    {
        "particle": "も",
        "reading": "mo",
        "meaning": "도",
        "note": "추가의 의미를 나타낸다.",
        "examples": ("わたしも学生です。", "これもおいしい。"),
    },
    {
        "particle": "から / まで",
        "reading": "kara / made",
        "meaning": "부터 / 까지",
        "note": "시작점과 끝점을 나타낸다.",
        "examples": ("9時から5時まで働きます。",),
    },
    {
        "particle": "ね / よ",
        "reading": "ne / yo",
        "meaning": "공감·확인 / 정보 전달",
        "note": "ね는 그쵸? 맞죠? 느낌, よ는 알려줄게/강하게 말함.",
        "examples": ("いい天気ですね。", "これ、おいしいですよ。"),
    },
)

BEGINNER_PATTERNS: tuple[str, ...] = (
    "わたしは ○○です.",
    "○○が あります/います.",
    "○○を します/食べます/見ます.",
    "○○に 行きます / ○時に.",
    "○○で.",
)


def get_kana(script: str) -> tuple[KanaEntry, ...]:
    normalized = script.strip().lower()
    if normalized == "hiragana":
        return HIRAGANA + HIRAGANA_MARKS + HIRAGANA_YOON
    if normalized == "katakana":
        return KATAKANA + KATAKANA_MARKS + KATAKANA_YOON
    raise ValueError("script must be 'hiragana' or 'katakana'")


def pair_by_romaji() -> dict[str, tuple[str, str]]:
    katakana_by_romaji = {romaji: symbol for symbol, romaji in get_kana("katakana")}
    return {
        romaji: (hiragana, katakana_by_romaji[romaji])
        for hiragana, romaji in get_kana("hiragana")
        if romaji in katakana_by_romaji
    }


def get_confusing_pairs(script: str) -> tuple[tuple[str, str, str], ...]:
    normalized = script.strip().lower()
    if normalized not in CONFUSING_PAIRS:
        raise ValueError("script must be 'hiragana' or 'katakana'")
    return CONFUSING_PAIRS[normalized]


def get_reading_examples(script: str) -> tuple[tuple[str, str, str, str], ...]:
    normalized = script.strip().lower()
    if normalized not in READING_EXAMPLES:
        raise ValueError("script must be 'hiragana' or 'katakana'")
    return READING_EXAMPLES[normalized]


def get_sokuon_examples(script: str) -> tuple[tuple[str, str, str, str], ...]:
    normalized = script.strip().lower()
    if normalized not in SOKUON_EXAMPLES:
        raise ValueError("script must be 'hiragana' or 'katakana'")
    return SOKUON_EXAMPLES[normalized]


def get_particles() -> tuple[dict[str, object], ...]:
    return PARTICLES


def get_beginner_patterns() -> tuple[str, ...]:
    return BEGINNER_PATTERNS
