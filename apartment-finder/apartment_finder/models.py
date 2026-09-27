from dataclasses import dataclass, field


@dataclass
class Listing:
    source: str
    url: str
    price_ils: int
    city: str
    neighborhood: str
    street: str
    rooms: str = ""
    kind: str = ""
    audience: str = ""
    audience_note: str = ""
    date_text: str = ""
    extras: str = ""
    current: bool = True
    travel_text: str = ""
    travel_minutes: float | None = None
    included: bool = False
    exclude_reason: str = ""
    latitude: float | None = None
    longitude: float | None = None

    @property
    def place(self) -> str:
        parts = [p for p in (self.street, self.neighborhood, self.city) if p]
        return ", ".join(parts)

    @property
    def type_label(self) -> str:
        bits = []
        if self.kind:
            bits.append(self.kind)
        if self.rooms:
            bits.append(f"{self.rooms} חד'")
        return ", ".join(bits) if bits else "not stated"


@dataclass
class SourceStatus:
    name: str
    ok: bool
    detail: str


@dataclass
class SearchResult:
    listings: list[Listing] = field(default_factory=list)
    sources: list[SourceStatus] = field(default_factory=list)
    campus_label: str = ""
    campus_lat: float | None = None
    campus_lon: float | None = None
    campus_note: str = ""
    travel_rule: str = ""
