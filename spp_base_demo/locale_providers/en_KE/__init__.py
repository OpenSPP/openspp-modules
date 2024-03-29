from faker.providers.person import Provider as PersonProvider


class Provider(PersonProvider):
    formats = ["{{first_name}} {{last_name}}"]

    first_names_male = [
        "Brian",
        "Kevin",
        "George",
        "Charles",
        "Joseph",
        "Peter",
        "Eric",
        "John",
        "Mark",
        "Stephen",
        "Michael",
        "Daniel",
        "Edward",
        "Robert",
        "Simon",
        "Anthony",
        "Kenneth",
        "Paul",
        "Richard",
        "Derek",
        "Matthew",
        "David",
        "Benjamin",
        "Nathan",
        "Timothy",
        "Samuel",
        "Nicholas",
        "Raymond",
        "Jeffrey",
        "Philip",
        "Patrick",
        "Henry",
        "Adam",
        "Christopher",
        "Andrew",
        "Martin",
        "Luke",
        "Alex",
        "Isaac",
        "Maxwell",
        "Jonathan",
        "Lawrence",
        "Gregory",
        "Oliver",
        "Arnold",
        "Theodore",
        "Victor",
        "Vincent",
        "Jared",
        "Edwin",
        "Ethan",
        "Gerald",
        "Leonard",
        "Bruce",
        "Caleb",
        "Collins",
        "Dennis",
        "Elijah",
        "Franklin",
        "Harold",
        "Ian",
        "Jack",
        "Justin",
        "Keith",
        "Larry",
        "Mason",
        "Noah",
        "Oscar",
        "Preston",
        "Ralph",
        "Scott",
        "Tom",
        "Ulysses",
        "Walter",
        "Xavier",
        "Zachary",
        "Aaron",
        "Abel",
        "Abraham",
        "Adrian",
        "Aidan",
        "Alfred",
        "Allan",
        "Alvin",
        "Amos",
        "Andre",
        "Angelo",
        "Austin",
        "Barry",
        "Bernard",
        "Bill",
        "Blake",
        "Bradley",
        "Brendan",
        "Brett",
        "Calvin",
        "Carl",
        "Cedric",
        "Clarence",
        "Clifford",
        "Clinton",
        "Cody",
        "Corey",
        "Cyrus",
        "Damian",
        "Damon",
        "Darrell",
        "Dean",
        "Dominic",
        "Donovan",
        "Douglas",
        "Duncan",
        "Dylan",
        "Emanuel",
        "Emmanuel",
        "Evan",
        "Everett",
        "Felix",
        "Floyd",
        "Francis",
        "Frank",
        "Fredrick",
        "Gabriel",
        "Garrett",
        "Gilbert",
        "Glen",
        "Gordon",
        "Graham",
        "Grant",
        "Guy",
        "Harrison",
        "Harry",
        "Hayden",
        "Hugh",
        "Hunter",
        "Isaiah",
        "Ivan",
        "Jacob",
        "Jameson",
        "Jamie",
        "Jeremiah",
        "Jesse",
        "Joel",
        "Johan",
        "Jonah",
        "Jordan",
        "Julian",
        "Karl",
        "Kelvin",
        "Kirk",
        "Kyle",
    ]

    first_names_female = [
        "Grace",
        "Faith",
        "Joy",
        "Janet",
        "Mary",
        "Patricia",
        "Linda",
        "Alice",
        "Margaret",
        "Jane",
        "Emily",
        "Dorothy",
        "Elizabeth",
        "Susan",
        "Julia",
        "Jessica",
        "Sarah",
        "Karen",
        "Nancy",
        "Betty",
        "Sharon",
        "Sandra",
        "Barbara",
        "Helen",
        "Kimberly",
        "Deborah",
        "Laura",
        "Joan",
        "Rachel",
        "Martha",
        "Diana",
        "Brenda",
        "Virginia",
        "Catherine",
        "Christine",
        "Samantha",
        "Monica",
        "Paula",
        "Melissa",
        "Ann",
        "Michelle",
        "Rebecca",
        "Rose",
        "Angela",
        "Kathleen",
        "Lisa",
        "Ashley",
        "Amanda",
        "Stephanie",
        "Carolyn",
        "Christina",
        "Marie",
        "Janice",
        "Nicole",
        "Judy",
        "Abigail",
        "Ada",
        "Adelaide",
        "Agnes",
        "Aileen",
        "Aimee",
        "Alana",
        "Alexandra",
        "Alexis",
        "Alice",
        "Alison",
        "Alyssa",
        "Amber",
        "Amelia",
        "Amy",
        "Anastasia",
        "Andrea",
        "Angelica",
        "Anita",
        "Anna",
        "Anne",
        "Annette",
        "Annie",
        "Antonia",
        "April",
        "Ariana",
        "Ariel",
        "Audrey",
        "Ava",
        "Beatrice",
        "Belinda",
        "Bernadette",
        "Bernice",
        "Beryl",
        "Bessie",
        "Beth",
        "Bethany",
        "Betsy",
        "Beverly",
        "Blanche",
        "Bonnie",
        "Brandi",
        "Brianna",
        "Bridget",
        "Brittany",
        "Brooke",
        "Camille",
        "Candace",
        "Carmen",
        "Carol",
        "Caroline",
        "Carrie",
        "Cassandra",
        "Cecilia",
        "Celeste",
        "Celia",
        "Cheryl",
        "Chloe",
        "Chris",
        "Christie",
        "Claire",
        "Clara",
        "Clarice",
        "Connie",
        "Constance",
        "Cora",
        "Courtney",
    ]

    first_names = first_names_female + first_names_male

    last_names = [
        "Kimani",
        "Wanjiru",
        "Kamau",
        "Ochieng",
        "Mwangi",
        "Ngugi",
        "Otieno",
        "Njoroge",
        "Wainaina",
        "Kiplagat",
        "Karanja",
        "Kioko",
        "Kiprono",
        "Momanyi",
        "Chege",
        "Omondi",
        "Gachanja",
        "Kibet",
        "Ndegwa",
        "Githinji",
        "Koech",
        "Maina",
        "Nyaga",
        "Onyango",
        "Mutua",
        "Wambua",
        "Kilonzo",
        "Munene",
        "Limo",
        "Chirchir",
        "Yego",
        "Langat",
        "Kosgei",
        "Bett",
        "Tanui",
        "Ngetich",
        "Barasa",
        "Lagat",
        "Choge",
        "Kigen",
        "Mbogo",
        "Ngao",
        "Mwinyi",
        "Omari",
        "Hamisi",
        "Lugano",
        "Chacha",
        "Makori",
        "Nyongesa",
        "Macharia",
        "Mutuku",
        "Mbugua",
        "Wafula",
        "Ogola",
        "Kirui",
        "Kiptoo",
        "Rotich",
        "Cheruiyot",
        "Sang",
        "Rono",
        "Owino",
        "Mutiso",
        "Kagwe",
        "Kiragu",
        "Muchiri",
        "Gakuo",
        "Kinyua",
        "Gatimu",
        "Gitau",
        "Murigi",
        "Ndungu",
        "Mathenge",
        "Mugo",
        "Waweru",
        "Kuria",
        "Maingi",
        "Thuku",
        "Warui",
        "Gakuru",
        "Kibaki",
        "Wanjala",
        "Machoka",
        "Mwendwa",
        "Mugendi",
        "Muraya",
        "Njenga",
        "Gatere",
        "Kabugi",
        "Karoki",
        "Gichuki",
        "Karuga",
        "Nyambura",
        "Muriuki",
        "Kubai",
        "Irungu",
        "Juma",
        "Abdi",
        "Hassan",
        "Ali",
        "Mohamed",
        "Ibrahim",
        "Ahmed",
        "Mustafa",
        "Isaac",
        "Jacob",
        "Luther",
        "Malcolm",
        "Moses",
        "Noel",
        "Pascal",
        "Quincy",
        "Reagan",
        "Silas",
        "Travis",
        "Upton",
        "Vaughn",
        "Wesley",
        "Xander",
        "Yusuf",
        "Zachariah",
        "Abel",
        "Brock",
        "Cedric",
        "Drake",
        "Ezekiel",
        "Fletcher",
        "Griffin",
        "Horace",
        "Ike",
        "Jarvis",
        "Kent",
        "Lowell",
        "Monty",
        "Nolan",
        "Orville",
        "Prescott",
        "Quinton",
        "Rupert",
        "Stuart",
        "Thaddeus",
        "Vance",
        "Wilfred",
        "Xavier",
        "York",
        "Zane",
    ]
