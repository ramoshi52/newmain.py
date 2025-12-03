import streamlit as st
import json
import random
import os
from datetime import datetime
from google import genai
from google.genai import types
from database import (
    save_test_result, mark_subtopic_seen, get_seen_subtopics,
    get_unseen_subtopics, add_favorite, remove_favorite, get_favorites,
    is_favorite, get_test_history, get_topic_stats, get_weak_topics,
    clear_seen_subtopics
)

st.set_page_config(page_title="AI English Teacher", page_icon="🇬🇧", layout="wide")

TOPIC_SUBTOPICS = {
    "History": [
        "The Fall of the Roman Empire",
        "Ancient Egyptian Pyramids and Pharaohs",
        "The French Revolution of 1789",
        "World War I Causes and Consequences",
        "World War II D-Day Landing",
        "The Renaissance in Italy",
        "The Industrial Revolution in Britain",
        "Ancient Greek Democracy",
        "The Ottoman Empire's Golden Age",
        "The Mongol Conquests of Genghis Khan",
        "The American Civil War",
        "The Cold War and Space Race",
        "The Viking Age and Exploration",
        "The Byzantine Empire",
        "The Crusades",
        "The Black Death Pandemic",
        "The Spanish Inquisition",
        "The Ming Dynasty in China",
        "The Aztec and Mayan Civilizations",
        "The Russian Revolution of 1917",
        "Napoleon Bonaparte's Campaigns",
        "The Silk Road Trade Routes",
        "The Age of Discovery",
        "The Salem Witch Trials",
        "The Berlin Wall",
        "Ancient Mesopotamian Civilizations",
        "The Samurai of Feudal Japan",
        "The British Raj in India",
        "The Irish Potato Famine",
        "The Assassination of Archduke Franz Ferdinand"
    ],
    "Geography": [
        "The Amazon Rainforest Ecosystem",
        "The Sahara Desert Formation",
        "Plate Tectonics and Earthquakes",
        "The Great Barrier Reef",
        "Mount Everest and the Himalayas",
        "The Nile River's Journey",
        "Climate Zones of the World",
        "The Ring of Fire Volcanoes",
        "The Arctic and Antarctic Ice Caps",
        "The Grand Canyon Formation",
        "Tropical Monsoon Seasons",
        "The Dead Sea and Its Properties",
        "The Mississippi River Delta",
        "Fjords of Norway",
        "The Gobi Desert",
        "Coral Reef Ecosystems",
        "The Alps Mountain Range",
        "Tsunami Formation and Impact",
        "The Victoria Falls",
        "Deforestation in Borneo",
        "The Great Lakes of North America",
        "Urban Geography of Tokyo",
        "The Galapagos Islands",
        "Permafrost and Climate Change",
        "The Danube River Basin",
        "Coastal Erosion Processes",
        "The Atacama Desert",
        "Population Distribution in Asia",
        "The Panama Canal",
        "Volcanic Islands of Hawaii"
    ],
    "Medicine": [
        "The Discovery of Penicillin by Alexander Fleming",
        "Hippocrates: The Father of Medicine",
        "Galen's Contributions to Anatomy",
        "The History of Vaccination",
        "Louis Pasteur and Germ Theory",
        "The Nobel Prize in Medicine Winners",
        "The Development of Anesthesia",
        "Ancient Egyptian Medical Practices",
        "The Human Immune System",
        "Marie Curie and Radiology",
        "The Discovery of DNA Structure",
        "Traditional Chinese Medicine",
        "The Black Plague and Medieval Medicine",
        "Surgery in the Renaissance",
        "The Smallpox Eradication",
        "Florence Nightingale and Modern Nursing",
        "Organ Transplantation History",
        "The Polio Vaccine Development",
        "Ayurvedic Medicine Traditions",
        "The Discovery of Blood Types",
        "Antiseptic Surgery by Joseph Lister",
        "The Human Genome Project",
        "Medieval Hospitals and Healers",
        "The Discovery of Insulin",
        "Ancient Greek Medical Schools",
        "The History of Psychiatry",
        "Stem Cell Research",
        "The Spanish Flu Pandemic of 1918",
        "Advances in Cancer Treatment",
        "The History of Heart Surgery"
    ],
    "Travel": [
        "The Seven Wonders of the Ancient World",
        "Backpacking Through Southeast Asia",
        "The Trans-Siberian Railway Journey",
        "Safari Adventures in Kenya",
        "The Camino de Santiago Pilgrimage",
        "Exploring Machu Picchu",
        "Road Trip Along Route 66",
        "The Northern Lights in Iceland",
        "Cruising the Mediterranean",
        "The Great Wall of China",
        "Hiking in the Swiss Alps",
        "The Temples of Angkor Wat",
        "Island Hopping in Greece",
        "The Floating Markets of Thailand",
        "Exploring the Galápagos Islands",
        "The Canals of Venice",
        "Desert Camping in Morocco",
        "The Fjords of New Zealand",
        "Ancient Ruins of Petra",
        "The Cherry Blossoms of Japan",
        "The Palaces of Rajasthan",
        "Diving in the Maldives",
        "The Castles of Scotland",
        "Trekking in Patagonia",
        "The Beaches of Bali",
        "Wine Tours in Tuscany",
        "The Northern Cape of Norway",
        "Exploring Havana's History",
        "The Temples of Kyoto",
        "Safari in the Serengeti"
    ],
    "Technology": [
        "The Invention of the Printing Press",
        "The History of the Internet",
        "Artificial Intelligence and Machine Learning",
        "The Development of Smartphones",
        "Blockchain and Cryptocurrency",
        "The Apollo Space Program",
        "Electric Vehicles Revolution",
        "The History of Video Games",
        "Quantum Computing Basics",
        "Social Media's Impact on Society",
        "The Evolution of Computers",
        "Renewable Energy Technologies",
        "Robotics in Manufacturing",
        "The World Wide Web Creation",
        "3D Printing Technology",
        "Virtual Reality Development",
        "The Telegraph and Morse Code",
        "GPS Navigation Systems",
        "Drone Technology Applications",
        "The History of Television",
        "Cybersecurity Challenges",
        "The Steam Engine Revolution",
        "Biotechnology Advances",
        "The History of Photography",
        "Satellite Communication",
        "The Invention of the Telephone",
        "Self-Driving Cars",
        "The Development of Radio",
        "Nanotechnology Applications",
        "The History of Aviation"
    ],
    "Science": [
        "Newton's Laws of Motion",
        "The Theory of Relativity",
        "Darwin's Evolution Theory",
        "The Periodic Table of Elements",
        "Black Holes and Dark Matter",
        "Climate Change Science",
        "The Big Bang Theory",
        "Photosynthesis in Plants",
        "The Discovery of Electricity",
        "DNA and Genetic Engineering",
        "The Water Cycle",
        "Nuclear Fission and Fusion",
        "The Human Brain Structure",
        "Earthquakes and Seismology",
        "The Speed of Light",
        "Chemical Reactions and Bonds",
        "The Ozone Layer",
        "Magnetism and Electromagnetism",
        "The Solar System Formation",
        "Quantum Mechanics Basics",
        "The Food Chain and Ecosystems",
        "Acid Rain and Its Effects",
        "The Laws of Thermodynamics",
        "Cellular Biology",
        "The Moon's Formation",
        "Renewable Energy Sources",
        "The Human Digestive System",
        "Sound Waves and Acoustics",
        "The Carbon Cycle",
        "Volcanoes and Lava Formation"
    ],
    "Art": [
        "Leonardo da Vinci's Masterpieces",
        "The Impressionist Movement",
        "Ancient Greek Sculpture",
        "Pablo Picasso and Cubism",
        "The Renaissance Art Period",
        "Vincent van Gogh's Life and Work",
        "Egyptian Art and Hieroglyphics",
        "The Baroque Art Movement",
        "Michelangelo's Sistine Chapel",
        "Japanese Ukiyo-e Woodblock Prints",
        "The Surrealist Movement",
        "Ancient Roman Mosaics",
        "Claude Monet's Water Lilies",
        "Pop Art and Andy Warhol",
        "Gothic Architecture",
        "African Tribal Art",
        "The Pre-Raphaelite Brotherhood",
        "Frida Kahlo's Self-Portraits",
        "Chinese Calligraphy Art",
        "The Art Nouveau Movement",
        "Abstract Expressionism",
        "Street Art and Banksy",
        "Islamic Geometric Patterns",
        "The Dutch Golden Age Painting",
        "Contemporary Installation Art",
        "The Bauhaus School",
        "Mexican Muralism",
        "Rococo Art Style",
        "Photography as Fine Art",
        "Digital Art Revolution"
    ],
    "Sports": [
        "The History of the Olympic Games",
        "Football World Cup History",
        "The Rise of Basketball",
        "Tennis Grand Slam Tournaments",
        "The Tour de France",
        "Boxing Legends Through History",
        "The History of Cricket",
        "Formula 1 Racing",
        "The Super Bowl Legacy",
        "Rugby World Cup",
        "Golf's Major Championships",
        "The History of Swimming",
        "Marathon Running Origins",
        "Ice Hockey and the NHL",
        "Gymnastics at the Olympics",
        "The History of Baseball",
        "Extreme Sports Evolution",
        "Table Tennis Origins",
        "The FIFA Women's World Cup",
        "Horse Racing Traditions",
        "The History of Skiing",
        "Volleyball's Olympic Journey",
        "The UFC and Mixed Martial Arts",
        "Surfing Culture and History",
        "The Boston Marathon",
        "Wheelchair Sports History",
        "The History of Fencing",
        "Esports and Gaming",
        "The Ryder Cup in Golf",
        "Athletics World Championships"
    ],
    "Food": [
        "The History of Italian Pasta",
        "Sushi and Japanese Cuisine",
        "French Culinary Traditions",
        "The Spice Trade Routes",
        "Mexican Food Heritage",
        "Indian Curry Varieties",
        "The History of Chocolate",
        "Chinese Dim Sum Culture",
        "Mediterranean Diet Benefits",
        "The Origins of Pizza",
        "Thai Street Food",
        "The History of Coffee",
        "British Tea Culture",
        "Korean Fermented Foods",
        "The History of Wine Making",
        "Middle Eastern Cuisine",
        "American Barbecue Traditions",
        "The History of Bread Making",
        "Vietnamese Pho Origins",
        "Greek Food and Olive Oil",
        "The History of Ice Cream",
        "Spanish Tapas Culture",
        "Turkish Breakfast Traditions",
        "The History of Cheese",
        "Peruvian Ceviche",
        "The History of Sugar",
        "Ethiopian Coffee Ceremony",
        "German Beer Brewing",
        "Caribbean Jerk Seasoning",
        "The History of Salt"
    ],
    "Environment": [
        "Deforestation in the Amazon",
        "Ocean Plastic Pollution",
        "Endangered Species Protection",
        "Renewable Energy Solutions",
        "The Greenhouse Effect",
        "Coral Bleaching Crisis",
        "Air Quality and Health",
        "Sustainable Agriculture",
        "Wildlife Conservation",
        "Water Scarcity Issues",
        "Urban Green Spaces",
        "Recycling and Waste Management",
        "Climate Change Adaptation",
        "Biodiversity Loss",
        "Electric Transportation",
        "Wetland Ecosystems",
        "Carbon Footprint Reduction",
        "Ocean Acidification",
        "Forest Fire Prevention",
        "Organic Farming Practices",
        "The Paris Climate Agreement",
        "Polar Ice Melting",
        "Green Building Design",
        "Invasive Species Impact",
        "Soil Erosion Prevention",
        "Wind Energy Development",
        "Marine Protected Areas",
        "Environmental Justice",
        "Sustainable Fashion",
        "Zero Waste Lifestyle"
    ],
    "Business": [
        "The History of Apple Inc.",
        "Amazon's Business Model",
        "The Rise of E-commerce",
        "Warren Buffett's Investment Strategy",
        "The Startup Ecosystem",
        "Global Supply Chain Management",
        "The History of Banking",
        "Marketing in the Digital Age",
        "Corporate Social Responsibility",
        "The Gig Economy",
        "Tesla's Disruption of Auto Industry",
        "The History of Wall Street",
        "Small Business Success Stories",
        "International Trade Agreements",
        "The Fast Fashion Industry",
        "Sustainable Business Practices",
        "The History of McDonald's",
        "Remote Work Revolution",
        "The Sharing Economy",
        "Luxury Brand Marketing",
        "The History of Advertising",
        "Merger and Acquisition Strategies",
        "Family Business Dynamics",
        "The Rise of Fintech",
        "The History of Retail",
        "Business Ethics Dilemmas",
        "The Oil and Gas Industry",
        "Women in Business Leadership",
        "The Pharmaceutical Industry",
        "The History of Tourism"
    ],
    "Education": [
        "The Montessori Method",
        "Online Learning Revolution",
        "The History of Universities",
        "STEM Education Importance",
        "The Socratic Teaching Method",
        "Literacy Programs Worldwide",
        "Special Education History",
        "The Finnish Education System",
        "Homeschooling Trends",
        "Educational Technology",
        "The History of Libraries",
        "Bilingual Education Benefits",
        "The Role of Teachers",
        "Student Mental Health",
        "Arts Education Value",
        "The History of Exams",
        "Gap Year Experiences",
        "Vocational Training",
        "The Waldorf Education Approach",
        "Education in Developing Countries",
        "The History of Textbooks",
        "Physical Education Importance",
        "Adult Education Programs",
        "The History of Kindergarten",
        "Educational Psychology",
        "School Architecture Design",
        "The History of Scholarships",
        "Peer Learning Strategies",
        "Environmental Education",
        "The Future of Education"
    ],
    "Music": [
        "The History of Jazz",
        "Classical Music Composers",
        "The Beatles' Revolution",
        "Hip Hop Culture Origins",
        "Opera's Golden Age",
        "African Drumming Traditions",
        "The History of Rock Music",
        "Electronic Music Evolution",
        "Country Music Heritage",
        "The History of the Piano",
        "Reggae and Bob Marley",
        "Blues Music Origins",
        "The History of Orchestras",
        "K-Pop's Global Phenomenon",
        "Folk Music Traditions",
        "The Vinyl Record Era",
        "Latin Music Influences",
        "The History of Guitars",
        "Music Festivals History",
        "The MTV Generation",
        "Indian Classical Music",
        "Broadway Musical Theater",
        "The History of Singing",
        "Punk Rock Movement",
        "Gospel Music Heritage",
        "The History of DJs",
        "Soul and R&B Evolution",
        "Celtic Music Traditions",
        "The Streaming Revolution",
        "Music and the Brain"
    ],
    "Animals": [
        "African Elephant Migration",
        "Great White Shark Behavior",
        "The Intelligence of Octopuses",
        "Penguin Colonies in Antarctica",
        "Wolf Pack Dynamics",
        "The Honey Bee Colony",
        "Cheetah Speed and Hunting",
        "Dolphin Communication",
        "The Giant Panda Conservation",
        "Bird Migration Patterns",
        "The Life of Lions",
        "Gorilla Family Structures",
        "Sea Turtle Journey",
        "The Monarch Butterfly Migration",
        "Crocodile Survival Skills",
        "The Bald Eagle",
        "Koala Life in Australia",
        "The Blue Whale",
        "Chimpanzee Tool Use",
        "Arctic Fox Adaptation",
        "The Orangutan Crisis",
        "Salmon Spawning Journey",
        "The African Wild Dog",
        "Polar Bear Hunting",
        "The Hummingbird",
        "Tiger Conservation Efforts",
        "The Komodo Dragon",
        "Owl Night Vision",
        "The Rhinoceros",
        "Flamingo Behavior"
    ],
    "Space": [
        "The Apollo 11 Moon Landing",
        "Mars Exploration Missions",
        "Black Holes Explained",
        "The International Space Station",
        "The Hubble Space Telescope",
        "Saturn's Ring System",
        "The Search for Exoplanets",
        "Asteroid Belt Exploration",
        "The Birth of Stars",
        "SpaceX and Commercial Spaceflight",
        "The Voyager Missions",
        "Jupiter's Great Red Spot",
        "Dark Matter Mystery",
        "The Milky Way Galaxy",
        "Astronaut Training",
        "The James Webb Telescope",
        "Comet Composition",
        "The Possibility of Life on Europa",
        "Space Debris Problem",
        "The History of NASA",
        "Rocket Science Basics",
        "The Moon's Phases",
        "Gravity and Orbits",
        "Solar Flares and Earth",
        "The Andromeda Galaxy",
        "Telescopes Through History",
        "Neutron Stars",
        "The Future of Mars Colonization",
        "Space Tourism",
        "The Big Bang Theory"
    ],
    "Psychology": [
        "Freud's Psychoanalytic Theory",
        "The Stanford Prison Experiment",
        "Memory and Forgetting",
        "Pavlov's Classical Conditioning",
        "The Psychology of Dreams",
        "Emotional Intelligence",
        "The Milgram Obedience Study",
        "Child Development Stages",
        "Cognitive Behavioral Therapy",
        "The Psychology of Color",
        "Maslow's Hierarchy of Needs",
        "Group Dynamics and Conformity",
        "The Placebo Effect",
        "Anxiety and Stress Management",
        "The Psychology of Happiness",
        "Nature vs. Nurture Debate",
        "Body Language Communication",
        "The Psychology of Persuasion",
        "Sleep and Dreams Research",
        "The Bystander Effect",
        "Personality Type Theories",
        "The Psychology of Fear",
        "Motivation and Goal Setting",
        "The Psychology of Addiction",
        "Mindfulness and Meditation",
        "The Psychology of Music",
        "Decision Making Processes",
        "The Psychology of Love",
        "Social Media and Mental Health",
        "The Psychology of Creativity"
    ],
    "Finance": [
        "The History of Money",
        "Stock Market Basics",
        "Cryptocurrency Explained",
        "The 2008 Financial Crisis",
        "Personal Budgeting Strategies",
        "The Federal Reserve System",
        "Investment Portfolio Management",
        "The History of Credit Cards",
        "Real Estate Investment",
        "The Great Depression",
        "Retirement Planning",
        "The Bond Market",
        "Currency Exchange Markets",
        "The History of Insurance",
        "Mutual Funds Explained",
        "The Role of Central Banks",
        "Inflation and Its Effects",
        "The History of Taxes",
        "Venture Capital Funding",
        "The Gold Standard",
        "Student Loan Management",
        "The History of Mortgages",
        "Compound Interest Power",
        "The Stock Market Crash of 1929",
        "ETFs and Index Funds",
        "The History of Coins",
        "Financial Literacy Education",
        "The Dot-Com Bubble",
        "Islamic Banking Principles",
        "The Future of Digital Currency"
    ]
}

TOPIC_LIST = [
    "🎯 Rastgele Konu",
    "🌍 Travel (Seyahat)",
    "📜 History (Tarih)",
    "🌐 Geography (Coğrafya)",
    "💻 Technology (Teknoloji)",
    "🏥 Medicine (Tıp)",
    "🔬 Science (Bilim)",
    "🎨 Art (Sanat)",
    "⚽ Sports (Spor)",
    "🍕 Food (Yemek)",
    "🌿 Environment (Çevre)",
    "💼 Business (İş)",
    "📚 Education (Eğitim)",
    "🎵 Music (Müzik)",
    "🐾 Animals (Hayvanlar)",
    "🚀 Space (Uzay)",
    "🧠 Psychology (Psikoloji)",
    "💰 Finance (Finans)",
    "✍️ Özel Konu Yaz"
]

TEST_TYPES = [
    "📖 Reading Comprehension",
    "📝 Cloze Test",
    "📚 Vocabulary",
    "✏️ Grammar",
    "🔍 Error Correction",
    "🔄 Paraphrasing",
    "📐 Sentence Completion",
    "🔗 Collocations",
    "💬 Idioms",
    "🔠 Word Formation",
    "📍 Prepositions",
    "✅ True/False"
]

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "current_subtopic" not in st.session_state:
    st.session_state.current_subtopic = None
if "current_main_topic" not in st.session_state:
    st.session_state.current_main_topic = None
if "result_saved" not in st.session_state:
    st.session_state.result_saved = False

def get_topic_key_from_selection(selected):
    if selected == "🎯 Rastgele Konu" or selected == "✍️ Özel Konu Yaz":
        return ""
    if "(" in selected:
        return selected.split("(")[0].split(" ", 1)[1].strip()
    return selected

st.title("🇬🇧 AI English Test Generator")

tab1, tab2, tab3 = st.tabs(["📝 Test Oluştur", "📊 Geçmiş & Analiz", "⭐ Favoriler"])

with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = os.environ.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")
    st.divider()
    
    test_type = st.selectbox("Test Türü", TEST_TYPES)
    level = st.select_slider("Seviye", options=["A1", "A2", "B1", "B2", "C1", "C2"], value="B1")
    
    st.divider()
    selected_topic = st.selectbox("Konu", TOPIC_LIST)
    
    topic_key = get_topic_key_from_selection(selected_topic)
    
    custom_topic = ""
    manual_subtopic = None
    
    if selected_topic == "✍️ Özel Konu Yaz":
        custom_topic = st.text_input("Konunuzu yazın")
    elif topic_key and topic_key in TOPIC_SUBTOPICS:
        st.divider()
        subtopic_mode = st.radio(
            "Alt Konu Seçimi",
            ["🎲 Otomatik (Görülmemiş)", "📋 Manuel Seç", "⭐ Favorilerden"],
            horizontal=True
        )
        
        if subtopic_mode == "📋 Manuel Seç":
            all_subtopics = TOPIC_SUBTOPICS[topic_key]
            seen_list = get_seen_subtopics(topic_key)
            seen_set = {s.subtopic for s in seen_list}
            
            subtopic_options = []
            for st_item in all_subtopics:
                if st_item in seen_set:
                    subtopic_options.append(f"✓ {st_item}")
                else:
                    subtopic_options.append(f"○ {st_item}")
            
            selected_subtopic = st.selectbox("Alt Konu Seçin", subtopic_options)
            if selected_subtopic:
                manual_subtopic = selected_subtopic[2:].strip()
        
        elif subtopic_mode == "⭐ Favorilerden":
            favorites = get_favorites(topic_key)
            if favorites:
                fav_options = [f.subtopic for f in favorites]
                manual_subtopic = st.selectbox("Favori Alt Konu", fav_options)
            else:
                st.info("Bu konuda henüz favori eklemediniz.")
        
        seen_count = len(get_seen_subtopics(topic_key))
        total_count = len(TOPIC_SUBTOPICS[topic_key])
        st.caption(f"📈 Görülen: {seen_count}/{total_count}")
        
        if seen_count > 0:
            if st.button("🔄 Görülenleri Sıfırla", key="reset_seen"):
                clear_seen_subtopics(topic_key)
                st.success("Sıfırlandı!")
                st.rerun()
    
    st.divider()
    word_count = st.slider("Kelime Sayısı", 100, 400, 200, 50)
    question_count = st.selectbox("Soru Sayısı", [5, 10, 15], index=1)

def parse_json_safely(text):
    text = text.strip()
    
    for prefix in ["```json", "```JSON", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end+1]
    
    data = json.loads(text)
    return data

def get_random_subtopic(topic_key, avoid_seen=True):
    if topic_key and topic_key in TOPIC_SUBTOPICS:
        all_subtopics = TOPIC_SUBTOPICS[topic_key]
        
        if avoid_seen:
            unseen = get_unseen_subtopics(topic_key, all_subtopics)
            if unseen:
                return random.choice(unseen), topic_key
            clear_seen_subtopics(topic_key)
        
        return random.choice(all_subtopics), topic_key
    elif not topic_key:
        all_topics = list(TOPIC_SUBTOPICS.keys())
        random_topic = random.choice(all_topics)
        all_subtopics = TOPIC_SUBTOPICS[random_topic]
        
        if avoid_seen:
            unseen = get_unseen_subtopics(random_topic, all_subtopics)
            if unseen:
                return random.choice(unseen), random_topic
        
        return random.choice(all_subtopics), random_topic
    return topic_key, topic_key

def create_prompt(test_type, level, topic, word_count, q_count, subtopic=None):
    if subtopic:
        topic_str = subtopic
    elif topic:
        topic_str = topic
    else:
        topic_str = "an interesting and unique topic"
    
    uid = random.randint(10000, 99999)
    
    type_name = test_type.split(" ", 1)[1] if " " in test_type else test_type
    
    prompt = f"""Create a {level} level {type_name} test about: "{topic_str}"

CRITICAL INSTRUCTIONS:
- The passage MUST be specifically and ONLY about "{topic_str}"
- Do NOT write about the general history or development of the broader category
- Focus on specific facts, events, people, dates, and details related to "{topic_str}"
- Include interesting and lesser-known facts about this specific topic
- Write approximately {word_count} words in academic English
- Create exactly {q_count} multiple choice questions
- Each question needs 4 options: A, B, C, D
- correct_answer field must contain ONLY one letter (A, B, C, or D)
- Questions should test comprehension of the specific passage content
- Make this content unique (ID:{uid})

EXAMPLE: If the topic is "Galen's Contributions to Anatomy", write ONLY about Galen - his life, discoveries, medical theories, his books, his influence - NOT about general medicine history.

Return ONLY this JSON format, no other text:

{{"passage": "Your specific passage about {topic_str} here...", "questions": [{{"id": 1, "question": "What is...?", "options": ["A) first", "B) second", "C) third", "D) fourth"], "correct_answer": "B", "explanation": "Because..."}}]}}"""
    
    return prompt

def call_api(api_key, prompt):
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction="You are an expert English test creator. Create unique, specific content about the exact topic given. Never write generic content. Return only valid JSON. No markdown. No explanation.",
                temperature=0.9
            )
        )
        
        if response.text:
            data = parse_json_safely(response.text)
            
            if "questions" in data and len(data["questions"]) > 0:
                for i, q in enumerate(data["questions"]):
                    if "id" not in q:
                        q["id"] = i + 1
                    if "correct_answer" in q:
                        ans = str(q["correct_answer"]).strip().upper()
                        q["correct_answer"] = ans[0] if ans else "A"
                
                if "passage" not in data:
                    data["passage"] = ""
                    
                return {"ok": True, "data": data}
            else:
                return {"ok": False, "error": "Sorular oluşturulamadı"}
        else:
            return {"ok": False, "error": "Boş yanıt"}
            
    except json.JSONDecodeError:
        return {"ok": False, "error": "JSON hatası - Tekrar deneyin"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}

def reset():
    st.session_state.quiz_data = None
    st.session_state.user_answers = {}
    st.session_state.show_results = False
    st.session_state.current_subtopic = None
    st.session_state.current_main_topic = None
    st.session_state.result_saved = False

with tab1:
    c1, c2 = st.columns([3, 1])
    with c1:
        btn_create = st.button("🚀 Testi Oluştur", type="primary", use_container_width=True)
    with c2:
        if st.session_state.quiz_data:
            if st.button("🔄 Sıfırla", use_container_width=True):
                reset()
                st.rerun()

    if btn_create:
        if not api_key:
            st.warning("Lütfen API anahtarınızı girin.")
        else:
            reset()
            
            if selected_topic == "✍️ Özel Konu Yaz":
                subtopic = custom_topic
                main_topic = "Custom"
            elif manual_subtopic:
                subtopic = manual_subtopic
                main_topic = topic_key
            else:
                subtopic, main_topic = get_random_subtopic(topic_key)
            
            st.session_state.current_subtopic = subtopic
            st.session_state.current_main_topic = main_topic
            
            mark_subtopic_seen(main_topic, subtopic)
            
            with st.spinner(f"Test oluşturuluyor: {subtopic}..."):
                prompt = create_prompt(test_type, level, topic_key, word_count, question_count, subtopic)
                result = call_api(api_key, prompt)
                
                if result["ok"]:
                    st.session_state.quiz_data = result["data"]
                    st.success(f"Test hazır! Konu: {subtopic}")
                else:
                    st.error(result["error"])

    if st.session_state.quiz_data:
        data = st.session_state.quiz_data
        
        if st.session_state.current_subtopic:
            col_topic, col_fav = st.columns([4, 1])
            with col_topic:
                st.info(f"📌 Konu: {st.session_state.current_subtopic}")
            with col_fav:
                main_t = st.session_state.current_main_topic or "Custom"
                sub_t = st.session_state.current_subtopic
                if is_favorite(main_t, sub_t):
                    if st.button("⭐", help="Favorilerden çıkar"):
                        remove_favorite(main_t, sub_t)
                        st.rerun()
                else:
                    if st.button("☆", help="Favorilere ekle"):
                        add_favorite(main_t, sub_t)
                        st.toast("Favorilere eklendi!")
                        st.rerun()
        
        passage = data.get("passage", "")
        if passage and len(passage) > 20:
            st.subheader("📖 Metin")
            st.markdown(passage)
            st.divider()
        
        questions = data.get("questions", [])
        
        if questions:
            st.subheader(f"📝 Sorular ({len(questions)} adet)")
            
            for q in questions:
                qid = q.get("id", 1)
                qtext = q.get("question", "")
                opts = q.get("options", [])
                correct = str(q.get("correct_answer", "A")).strip().upper()
                if len(correct) > 1:
                    correct = correct[0]
                expl = q.get("explanation", "")
                
                key = f"q{qid}"
                
                if st.session_state.show_results:
                    user_ans = st.session_state.user_answers.get(key, "")
                    is_ok = (user_ans == correct)
                    
                    icon = "✅" if is_ok else "❌"
                    st.markdown(f"**{icon} Soru {qid}:** {qtext}")
                    
                    for opt in opts:
                        letter = opt[0].upper() if opt else ""
                        if letter == correct:
                            st.success(f"✓ {opt}")
                        elif letter == user_ans and not is_ok:
                            st.error(f"✗ {opt}")
                        else:
                            st.write(f"  {opt}")
                    
                    if expl:
                        with st.expander("Açıklama"):
                            st.write(expl)
                else:
                    st.markdown(f"**Soru {qid}:** {qtext}")
                    
                    user_current = st.session_state.user_answers.get(key)
                    idx = None
                    if user_current and opts:
                        for i, o in enumerate(opts):
                            if o and o[0].upper() == user_current:
                                idx = i
                                break
                    
                    choice = st.radio(
                        "Seçiminiz:",
                        opts,
                        index=idx,
                        key=f"radio_{qid}",
                        label_visibility="collapsed"
                    )
                    
                    if choice:
                        st.session_state.user_answers[key] = choice[0].upper()
                
                st.markdown("---")
            
            if not st.session_state.show_results:
                answered = len(st.session_state.user_answers)
                total = len(questions)
                st.progress(answered / total if total > 0 else 0)
                st.write(f"Cevaplanan: {answered}/{total}")
                
                if st.button("✔️ Testi Bitir", type="primary", use_container_width=True):
                    st.session_state.show_results = True
                    st.rerun()
            else:
                correct_cnt = 0
                total_cnt = len(questions)
                
                for q in questions:
                    qid = q.get("id", 1)
                    correct = str(q.get("correct_answer", "")).strip().upper()
                    if len(correct) > 1:
                        correct = correct[0]
                    user_ans = st.session_state.user_answers.get(f"q{qid}", "")
                    if user_ans == correct:
                        correct_cnt += 1
                
                pct = (correct_cnt / total_cnt * 100) if total_cnt > 0 else 0
                
                if not st.session_state.result_saved:
                    save_test_result(
                        main_topic=st.session_state.current_main_topic or "Custom",
                        subtopic=st.session_state.current_subtopic or "",
                        test_type=test_type,
                        level=level,
                        score=pct,
                        total_questions=total_cnt,
                        correct_answers=correct_cnt
                    )
                    st.session_state.result_saved = True
                
                st.subheader("📊 Sonuç")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Doğru", correct_cnt)
                col2.metric("Yanlış", total_cnt - correct_cnt)
                col3.metric("Başarı", f"%{pct:.0f}")
                
                if pct >= 80:
                    st.success("🎉 Harika!")
                elif pct >= 60:
                    st.info("👍 İyi!")
                elif pct >= 40:
                    st.warning("📚 Daha fazla çalış!")
                else:
                    st.error("📖 Tekrar dene!")
                
                if st.button("🔁 Tekrar Çöz", use_container_width=True):
                    st.session_state.user_answers = {}
                    st.session_state.show_results = False
                    st.session_state.result_saved = False
                    st.rerun()
        else:
            st.warning("Sorular yüklenemedi. Lütfen tekrar deneyin.")

with tab2:
    st.subheader("📊 Test Geçmişi ve Analiz")
    
    stats = get_topic_stats()
    if stats:
        st.markdown("### 📈 Konu Başarı Oranları")
        
        cols = st.columns(3)
        for i, stat in enumerate(stats):
            with cols[i % 3]:
                avg_score = stat.avg_score or 0
                color = "🟢" if avg_score >= 70 else "🟡" if avg_score >= 50 else "🔴"
                st.metric(
                    f"{color} {stat.main_topic}",
                    f"%{avg_score:.0f}",
                    f"{stat.test_count} test"
                )
        
        weak = get_weak_topics(60)
        if weak:
            st.markdown("### ⚠️ Geliştirilmesi Gereken Konular")
            for w in weak:
                st.warning(f"**{w.main_topic}**: Ortalama %{w.avg_score:.0f} ({w.test_count} test)")
    else:
        st.info("Henüz test geçmişi bulunmuyor. İlk testinizi oluşturun!")
    
    st.divider()
    
    st.markdown("### 📜 Son Testler")
    history = get_test_history(20)
    
    if history:
        for h in history:
            score_color = "🟢" if h.score >= 70 else "🟡" if h.score >= 50 else "🔴"
            with st.expander(f"{score_color} {h.subtopic} - %{h.score:.0f} ({h.created_at.strftime('%d/%m/%Y %H:%M')})"):
                st.write(f"**Ana Konu:** {h.main_topic}")
                st.write(f"**Test Türü:** {h.test_type}")
                st.write(f"**Seviye:** {h.level}")
                st.write(f"**Sonuç:** {h.correct_answers}/{h.total_questions} doğru")
    else:
        st.info("Henüz test geçmişi bulunmuyor.")
    
    st.divider()
    
    st.markdown("### 📊 Görülen Alt Konular")
    
    topic_for_seen = st.selectbox(
        "Konu Seçin",
        [k for k in TOPIC_SUBTOPICS.keys()],
        key="seen_topic_select"
    )
    
    if topic_for_seen:
        seen = get_seen_subtopics(topic_for_seen)
        total = len(TOPIC_SUBTOPICS[topic_for_seen])
        seen_count = len(seen)
        
        st.progress(seen_count / total if total > 0 else 0)
        st.write(f"**Görülen:** {seen_count}/{total} alt konu")
        
        if seen:
            seen_names = [s.subtopic for s in seen]
            all_names = TOPIC_SUBTOPICS[topic_for_seen]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Görülenler:**")
                for name in seen_names:
                    st.write(f"• {name}")
            with col2:
                st.markdown("**⬜ Görülmeyenler:**")
                unseen = [n for n in all_names if n not in seen_names]
                for name in unseen[:10]:
                    st.write(f"• {name}")
                if len(unseen) > 10:
                    st.caption(f"... ve {len(unseen) - 10} konu daha")

with tab3:
    st.subheader("⭐ Favori Alt Konularım")
    
    favorites = get_favorites()
    
    if favorites:
        grouped = {}
        for f in favorites:
            if f.main_topic not in grouped:
                grouped[f.main_topic] = []
            grouped[f.main_topic].append(f.subtopic)
        
        for topic, subtopics in grouped.items():
            st.markdown(f"### {topic}")
            for sub in subtopics:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"⭐ {sub}")
                with col2:
                    if st.button("🗑️", key=f"del_{topic}_{sub}", help="Favorilerden çıkar"):
                        remove_favorite(topic, sub)
                        st.rerun()
            st.divider()
    else:
        st.info("Henüz favori eklemediniz. Test oluşturduktan sonra ⭐ simgesine tıklayarak favorilere ekleyebilirsiniz.")

st.markdown("---")
st.caption("AI English Test Generator")
