from pydantic import BaseModel
from enum import Enum
from .document import Document


class QueryResult(BaseModel):
    """Represents one retrieved document in a list of query results."""
    document: Document
    score: float
    id: str

regions = {
"da-DK": "da-DK",
"de-AT": "de-AT",
"de-CH": "de-CH",
"de-DE": "de-DE",
"en-AU": "en-AU",
"en-CA": "en-CA",
"en-GB": "en-GB",
"en-ID": "en-ID",
"en-IN": "en-IN",
"en-MY": "en-MY",
"en-NZ": "en-NZ",
"en-PH": "en-PH",
"en-US": "en-US",
"en-ZA": "en-ZA",
"es-AR": "es-AR",
"es-CL": "es-CL",
"es-ES": "es-ES",
"es-MX": "es-MX",
"es-US": "es-US",
"fi-FI": "fi-FI",
"fr-BE": "fr-BE",
"fr-CA": "fr-CA",
"fr-CH": "fr-CH",
"fr-FR": "fr-FR",
"it-IT": "it-IT",
"ja-JP": "ja-JP",
"ko-KR": "ko-KR",
"nl-BE": "nl-BE",
"nl-NL": "nl-NL",
"no-NO": "no-NO",
"pl-PL": "pl-PL",
"pt-BR": "pt-BR",
"ru-RU": "ru-RU",
"sv-SE": "sv-SE",
"tr-TR": "tr-TR",
"zh-CN": "zh-CN",
"zh-HK": "zh-HK",
"zh-TW": "zh-TW"
}

Region = Enum('Region', regions)
