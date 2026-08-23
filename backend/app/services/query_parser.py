import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Canonical categories in ShopEase catalog
CANONICAL_CATEGORIES = [
    "Smartphones",
    "Laptops",
    "Headphones",
    "Running Shoes",
    "Backpacks",
    "Smart Watches",
    "Keyboards",
    "Mouse",
    "Office Accessories",
    "College Accessories"
]

# Primary category keywords (direct device/product categories)
PRIMARY_CATEGORY_SYNONYMS = {
    # Smartphones
    "phone": "Smartphones",
    "phones": "Smartphones",
    "smartphone": "Smartphones",
    "smartphones": "Smartphones",
    "mobile": "Smartphones",
    "mobiles": "Smartphones",
    "cellphone": "Smartphones",
    "android": "Smartphones",
    "iphone": "Smartphones",
    "iphones": "Smartphones",
    "5g phone": "Smartphones",
    "5g phones": "Smartphones",

    # Laptops
    "laptop": "Laptops",
    "laptops": "Laptops",
    "notebook": "Laptops",
    "notebooks": "Laptops",
    "computer": "Laptops",
    "computers": "Laptops",
    "macbook": "Laptops",
    "pc": "Laptops",
    "gaming laptop": "Laptops",
    "gaming laptops": "Laptops",
    "ultrabook": "Laptops",
    "workstation": "Laptops",

    # Headphones
    "headphone": "Headphones",
    "headphones": "Headphones",
    "earphone": "Headphones",
    "earphones": "Headphones",
    "earbud": "Headphones",
    "earbuds": "Headphones",
    "tws": "Headphones",
    "audio": "Headphones",
    "anc": "Headphones",
    "neckband": "Headphones",
    "headset": "Headphones",
    "headsets": "Headphones",

    # Running Shoes
    "shoe": "Running Shoes",
    "shoes": "Running Shoes",
    "running shoe": "Running Shoes",
    "running shoes": "Running Shoes",
    "sneaker": "Running Shoes",
    "sneakers": "Running Shoes",
    "footwear": "Running Shoes",
    "trainer": "Running Shoes",
    "trainers": "Running Shoes",

    # Backpacks
    "bag": "Backpacks",
    "bags": "Backpacks",
    "backpack": "Backpacks",
    "backpacks": "Backpacks",
    "rucksack": "Backpacks",
    "daypack": "Backpacks",
    "travel bag": "Backpacks",
    "laptop bag": "Backpacks",

    # Smart Watches
    "watch": "Smart Watches",
    "watches": "Smart Watches",
    "smartwatch": "Smart Watches",
    "smartwatches": "Smart Watches",
    "smart watch": "Smart Watches",
    "smart watches": "Smart Watches",
    "fitness band": "Smart Watches",
    "smart band": "Smart Watches",

    # Keyboards
    "keyboard": "Keyboards",
    "keyboards": "Keyboards",
    "mechanical keyboard": "Keyboards",
    "mechanical keyboards": "Keyboards",

    # Mouse
    "mouse": "Mouse",
    "mice": "Mouse",
    "trackball": "Mouse",
    "gaming mouse": "Mouse"
}

# Secondary/accessory/lifestyle category keywords
SECONDARY_CATEGORY_SYNONYMS = {
    # Office Accessories
    "office accessories": "Office Accessories",
    "office accessory": "Office Accessories",
    "desk accessories": "Office Accessories",
    "desk accessory": "Office Accessories",
    "desk mat": "Office Accessories",
    "laptop stand": "Office Accessories",
    "light bar": "Office Accessories",
    "docking station": "Office Accessories",
    "usb hub": "Office Accessories",
    "webcam": "Office Accessories",
    "office": "Office Accessories",
    "desk": "Office Accessories",

    # College Accessories
    "college accessories": "College Accessories",
    "college accessory": "College Accessories",
    "student accessories": "College Accessories",
    "student accessory": "College Accessories",
    "desk accessories for college student": "College Accessories",
    "desk accessories for college": "College Accessories",
    "desk accessories for student": "College Accessories",
    "study lamp": "College Accessories",
    "power bank": "College Accessories",
    "water bottle": "College Accessories",
    "study notebook": "College Accessories",
    "calculator": "College Accessories",
    "college student": "College Accessories",
    "college": "College Accessories",
    "student": "College Accessories",
    "dorm": "College Accessories"
}

CATEGORY_SYNONYMS = {**PRIMARY_CATEGORY_SYNONYMS, **SECONDARY_CATEGORY_SYNONYMS}

KNOWN_COLORS = [
    "black", "white", "blue", "red", "green", "grey", "gray", "silver",
    "gold", "pink", "yellow", "orange", "purple", "brown", "navy",
    "midnight black", "matte black", "space grey", "rose gold"
]

KNOWN_BRANDS = [
    "NovaTech", "AuraMobile", "PixelCraft", "Zenith", "ApexTech", "VoltMax",
    "CyberByte", "ZenBook", "ProBook", "EduBook", "FlexiBook", "CreatorStudio",
    "SwiftStream", "TitanBook", "CloudStride", "TrailBlazer", "FlexRunner",
    "SpeedCarbon", "SprintAir", "AudioZen", "SoundMax", "SoundPulse", "SonicPro",
    "BeatCraft", "UrbanPack", "TerraTrek", "AeroGlide", "ProOffice", "ChronoFit",
    "PulseGear", "VibeActive", "ApexGear", "KeyCraft", "TypeMaster", "ClickPro",
    "DeskEase", "ErgoPlus", "LumiDesk", "StudentPlus", "StudyMate", "VoltCharge"
]


class ParsedQuery(BaseModel):
    raw_query: str
    category: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    semantic_query: str = ""


class QueryParser:
    """Deterministic parser extracting structured constraints from natural language search queries."""

    def parse(self, query: str) -> ParsedQuery:
        clean_raw = query.strip()
        text = clean_raw.lower()
        # Remove commas inside numbers (e.g. 20,000 -> 20000)
        text = re.sub(r'(\d+),(\d+)', r'\1\2', text)

        min_price, max_price = self._extract_prices(text)
        category = self._extract_category(text)
        color = self._extract_color(text)
        brand = self._extract_brand(text)
        features = self._extract_features(text)
        semantic_query = self._build_semantic_query(clean_raw, min_price, max_price, category, color, brand)

        return ParsedQuery(
            raw_query=clean_raw,
            category=category,
            min_price=min_price,
            max_price=max_price,
            color=color,
            brand=brand,
            features=features,
            semantic_query=semantic_query
        )

    def _extract_prices(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extract min and max prices from query text.
        """
        min_price: Optional[int] = None
        max_price: Optional[int] = None

        # 1. Range: "between X and Y" or "X to Y" or "X - Y"
        range_match = re.search(
            r'(?:between|from)?\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k)?\s*(?:and|to|-)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k)?\b',
            text
        )
        if range_match:
            try:
                val1 = float(range_match.group(1)) * (1000 if range_match.group(2) else 1)
                val2 = float(range_match.group(3)) * (1000 if range_match.group(4) else 1)
                if val1 > 0 and val2 > 0:
                    min_price = int(min(val1, val2))
                    max_price = int(max(val1, val2))
                    return min_price, max_price
            except (ValueError, TypeError):
                pass

        # 2. Max Price: "under 30000", "below ₹20000", "less than 15k", "upto 30000", "within 25000", "budget of 20000"
        under_k_match = re.search(
            r'(?:under|below|less than|within|budget(?:\s+of)?|max(?:\s+of)?|upto|up to|around|costing less than)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*k\b',
            text
        )
        if under_k_match:
            try:
                max_price = int(float(under_k_match.group(1)) * 1000)
            except ValueError:
                pass

        if max_price is None:
            under_num_match = re.search(
                r'(?:under|below|less than|within|budget(?:\s+of)?|max(?:\s+of)?|upto|up to|around|costing less than)\s*(?:rs\.?|inr|₹)?\s*(\d{2,7})\b',
                text
            )
            if under_num_match:
                try:
                    max_price = int(under_num_match.group(1))
                except ValueError:
                    pass

        # 3. Min Price: "above 20000", "over 50000", "more than 10000", "starting from 20000", "min 5000"
        above_k_match = re.search(
            r'(?:above|over|more than|greater than|starting from|min(?:\s+of)?|at least)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*k\b',
            text
        )
        if above_k_match:
            try:
                min_price = int(float(above_k_match.group(1)) * 1000)
            except ValueError:
                pass

        if min_price is None:
            above_num_match = re.search(
                r'(?:above|over|more than|greater than|starting from|min(?:\s+of)?|at least)\s*(?:rs\.?|inr|₹)?\s*(\d{2,7})\b',
                text
            )
            if above_num_match:
                try:
                    min_price = int(above_num_match.group(1))
                except ValueError:
                    pass

        return min_price, max_price

    def _extract_category(self, text: str) -> Optional[str]:
        """
        Match category with priority:
        1. Primary hardware / apparel product categories (e.g. 'laptop', 'phone', 'shoes', 'headphones', 'keyboard')
        2. Secondary / accessory categories (e.g. 'desk accessories for college student', 'college', 'student', 'office')
        """
        # 1. Primary hardware categories (e.g. "laptop for college student" -> Laptops)
        for syn, cat in sorted(PRIMARY_CATEGORY_SYNONYMS.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(syn) + r'\b'
            if re.search(pattern, text):
                return cat

        # 2. Secondary accessory/lifestyle categories (e.g. "desk accessories for college student" -> College Accessories)
        for syn, cat in sorted(SECONDARY_CATEGORY_SYNONYMS.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(syn) + r'\b'
            if re.search(pattern, text):
                return cat

        return None

    def _extract_color(self, text: str) -> Optional[str]:
        """Extract recognized color names."""
        for color in sorted(KNOWN_COLORS, key=lambda x: -len(x)):
            pattern = r'\b' + re.escape(color) + r'\b'
            if re.search(pattern, text):
                return color
        return None

    def _extract_brand(self, text: str) -> Optional[str]:
        """Extract recognized brand names."""
        for brand in KNOWN_BRANDS:
            pattern = r'\b' + re.escape(brand.lower()) + r'\b'
            if re.search(pattern, text):
                return brand
        return None

    def _extract_features(self, text: str) -> List[str]:
        """Extract desired key feature keywords."""
        feature_patterns = [
            r'good camera', r'camera', r'photography', r'battery(?:\s+life)?',
            r'5g', r'oled', r'amoled', r'fast charging', r'lightweight',
            r'noise cancellation', r'anc', r'wireless', r'bluetooth',
            r'waterproof', r'water resistant', r'mechanical', r'ergonomic',
            r'gaming', r'coding', r'programming', r'student', r'college',
            r'office', r'daily use', r'travel', r'4k', r'120hz', r'backlight'
        ]
        found = []
        for fp in feature_patterns:
            if re.search(r'\b' + fp + r'\b', text):
                found.append(fp)
        return found

    def _build_semantic_query(
        self,
        raw_query: str,
        min_price: Optional[int],
        max_price: Optional[int],
        category: Optional[str],
        color: Optional[str],
        brand: Optional[str]
    ) -> str:
        """
        Build a rich query string for dense vector embedding search.
        Preserves descriptive tokens while expanding with extracted category.
        """
        parts = [raw_query]
        if category and category.lower() not in raw_query.lower():
            parts.append(category)
        return " ".join(parts).strip()


query_parser = QueryParser()
