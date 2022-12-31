from pydantic import BaseModel
from enum import Enum
from .document import Document


class QueryResult(BaseModel):
    """Represents one retrieved document in a list of query results."""
    document: Document
    score: float
    id: str

regions = {
"es-AR":"es-AR",
"en-AU":"en-AU",
"de-AT":"de-AT",
"nl-BE":"nl-BE",
"fr-BE":"fr-BE",
"pt-BR":"pt-BR",
"en-CA":"en-CA",
"fr-CA":"fr-CA",
"es-CL":"es-CL",
"da-DK":"da-DK",
"fi-FI":"fi-FI",
"fr-FR":"fr-FR",
"de-DE":"de-DE",
"zh-HK":"zh-HK",
"en-IN":"en-IN",
"en-ID":"en-ID",
"it-IT":"it-IT",
"ja-JP":"ja-JP",
"ko-KR":"ko-KR",
"en-MY":"en-MY",
"es-MX":"es-MX",
"nl-NL":"nl-NL",
"en-NZ":"en-NZ",
"no-NO":"no-NO",
"zh-CN":"zh-CN",
"pl-PL":"pl-PL",
"en-PH":"en-PH",
"ru-RU":"ru-RU",
"en-ZA":"en-ZA",
"es-ES":"es-ES",
"sv-SE":"sv-SE",
"fr-CH":"fr-CH",
"de-CH":"de-CH",
"zh-TW":"zh-TW",
"tr-TR":"tr-TR",
"en-GB":"en-GB",
"en-US":"en-US",
"es-US":"es-US",
}

Region = Enum('Region', regions)
