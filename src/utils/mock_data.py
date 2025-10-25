"""
Mock data for Phase 2-3 UI development

This module provides hardcoded mock data for building and testing the UI
before implementing the backend logic.
"""

# Mock Bible Books (subset for testing)
MOCK_BOOKS = [
    "Genesis创世记",
    "Exodus出埃及记",
    "Leviticus利未记",
    "Numbers民数记",
    "Deuteronomy申命记",
    "Matthew马太福音",
    "Mark马可福音",
    "Luke路加福音",
    "John约翰福音",
    "Acts使徒行传",
    "Romans罗马书",
    "1 Corinthians哥林多前书",
    "2 Corinthians哥林多后书",
    "Galatians加拉太书",
    "Ephesians以弗所书",
    "Revelation启示录",
]

# Mock Book Metadata
MOCK_BOOK_INFO = {
    "Genesis创世记": {"id": 1, "chapters": 50},
    "Exodus出埃及记": {"id": 2, "chapters": 40},
    "Matthew马太福音": {"id": 40, "chapters": 28},
    "John约翰福音": {"id": 43, "chapters": 21},
    "Romans罗马书": {"id": 45, "chapters": 16},
}

# Mock Hymns
MOCK_HYMNS = {
    "A01": {"name": "Amazing Grace", "slides_id": "1saIavtk49GG2zSinkdAgWltEba0xiRv7Cf5KbksYKwk"},
    "A02": {"name": "How Great Thou Art", "slides_id": "1ABC123XYZ456"},
    "C001": {"name": "Come Thou Fount", "slides_id": "1O6uLRuKGDsgkgtHSYw2HVfmYvEHDqziz_MiGaDKRsVg"},
    "C002": {"name": "Crown Him with Many Crowns", "slides_id": "1DEF789GHI012"},
    "123": {"name": "Blessed Assurance", "slides_id": "1JKL345MNO678"},
}

# Mock Bible Verses (John 3:16-17)
MOCK_VERSES = {
    "John约翰福音": {
        3: {
            16: {
                "cuv": "神爱世人，甚至将他的独生子赐给他们，叫一切信他的，不至灭亡，反得永生。",
                "kjv": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "niv": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
                "nas": "For God so loved the world, that He gave His only Son, so that everyone who believes in Him will not perish, but have eternal life.",
                "dby": "For God so loved the world, that he gave his only-begotten Son, that whosoever believes on him may not perish, but have life eternal."
            },
            17: {
                "cuv": "因为神差他的儿子降世，不是要定世人的罪，乃是要叫世人因他得救。",
                "kjv": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
                "niv": "For God did not send his Son into the world to condemn the world, but to save the world through him.",
                "nas": "For God did not send the Son into the world to judge the world, but so that the world might be saved through Him.",
                "dby": "For God has not sent his Son into the world that he may judge the world, but that the world may be saved through him."
            },
            18: {
                "cuv": "信他的人，不被定罪；不信的人，罪已经定了，因为他不信神独生子的名。",
                "kjv": "He that believeth on him is not condemned: but he that believeth not is condemned already, because he hath not believed in the name of the only begotten Son of God.",
                "niv": "Whoever believes in him is not condemned, but whoever does not believe stands condemned already because they have not believed in the name of God's one and only Son.",
                "nas": "The one who believes in Him is not judged; the one who does not believe has been judged already, because he has not believed in the name of the only Son of God.",
                "dby": "He that believes on him is not judged: but he that believes not has been already judged, because he has not believed on the name of the only-begotten Son of God."
            }
        }
    }
}

# Mock Chapter Preview (John 3, verses 1-21)
MOCK_CHAPTER_VERSES = [
    "1. There was a man of the Pharisees, named Nicodemus, a ruler of the Jews:",
    "2. The same came to Jesus by night, and said unto him, Rabbi, we know that thou art a teacher come from God...",
    "3. Jesus answered and said unto him, Verily, verily, I say unto thee, Except a man be born again, he cannot see the kingdom of God.",
    "4. Nicodemus saith unto him, How can a man be born when he is old? can he enter the second time into his mother's womb, and be born?",
    "5. Jesus answered, Verily, verily, I say unto thee, Except a man be born of water and of the Spirit, he cannot enter into the kingdom of God.",
    "6. That which is born of the flesh is flesh; and that which is born of the Spirit is spirit.",
    "7. Marvel not that I said unto thee, Ye must be born again.",
    "8. The wind bloweth where it listeth, and thou hearest the sound thereof, but canst not tell whence it cometh, and whither it goeth...",
    "9. Nicodemus answered and said unto him, How can these things be?",
    "10. Jesus answered and said unto him, Art thou a master of Israel, and knowest not these things?",
    "11. Verily, verily, I say unto thee, We speak that we do know, and testify that we have seen; and ye receive not our witness.",
    "12. If I have told you earthly things, and ye believe not, how shall ye believe, if I tell you of heavenly things?",
    "13. And no man hath ascended up to heaven, but he that came down from heaven, even the Son of man which is in heaven.",
    "14. And as Moses lifted up the serpent in the wilderness, even so must the Son of man be lifted up:",
    "15. That whosoever believeth in him should not perish, but have eternal life.",
    "16. For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
    "17. For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
    "18. He that believeth on him is not condemned: but he that believeth not is condemned already...",
    "19. And this is the condemnation, that light is come into the world, and men loved darkness rather than light...",
    "20. For every one that doeth evil hateth the light, neither cometh to the light, lest his deeds should be reproved.",
    "21. But he that doeth truth cometh to the light, that his deeds may be made manifest, that they are wrought in God.",
]

# Mock History
MOCK_HISTORY = [
    {"ref": "John 3:16", "versions": ["cuv", "kjv"], "timestamp": "14:30"},
    {"ref": "Genesis 1:1", "versions": ["cuv"], "timestamp": "14:25"},
    {"ref": "Romans 8:28", "versions": ["cuv", "kjv", "niv"], "timestamp": "14:20"},
    {"ref": "John 1:1", "versions": ["kjv"], "timestamp": "14:15"},
]

# Mock Display Info
MOCK_DISPLAYS = [
    {"name": "Built-in Display", "resolution": "1920×1080", "position": "(0, 0)", "primary": True},
    {"name": "External Display", "resolution": "1920×1080", "position": "(1920, 0)", "primary": False},
]

# Bible Version Names
BIBLE_VERSIONS = {
    "cuv": "和合本 (CUV)",
    "kjv": "King James (KJV)",
    "niv": "New International (NIV)",
    "nas": "New American Standard (NAS)",
    "dby": "Darby Translation (DBY)",
}

# Bible Version Codes (for checkboxes)
BIBLE_VERSION_CODES = ["cuv", "kjv", "niv", "nas", "dby"]