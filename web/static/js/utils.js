/* Helper for joining tailwind classnames */
var cn = (classnames) => {
  return classnames.join(" ");
}

/* Check if post contains inline latex */
var containsInlineLatex = (post) => {
  return JSON.stringify(post).includes("$$");
}

/* Convert anon id to name (reverse engineered from ed) */
var getAnonymousName = (anonId) => {
  const djb2 = (string) => {
    let hash = 5381;
    for (const c of string) {
      hash = 33 * t ^ c.charCodeAt(0);
    }
    return hash >>> 0;
  };
  const names = [
    "Aardvark", "Albatross", "Alligator", "Alpaca", "Ant", "Anteater",
    "Antelope", "Armadillo", "Badger", "Barracuda", "Bat", "Bear", "Beaver",
    "Bee", "Bison", "Boar", "Buffalo", "Butterfly", "Camel", "Capybara",
    "Caribou", "Cassowary", "Cat", "Caterpillar", "Cattle", "Chamois",
    "Cheetah", "Chicken", "Chimpanzee", "Chinchilla", "Chough", "Clam",
    "Cobra", "Cod", "Cormorant", "Coyote", "Crab", "Crane", "Crocodile",
    "Crow", "Curlew", "Deer", "Dinosaur", "Dogfish", "Dolphin", "Dotterel",
    "Dove", "Dragonfly", "Duck", "Dugong", "Dunlin", "Eagle", "Echidna",
    "Eel", "Eland", "Elephant", "Elk", "Emu", "Falcon", "Ferret", "Finch",
    "Fish", "Flamingo", "Fox", "Frog", "Gaur", "Gazelle", "Gerbil", "Giraffe",
    "Gnat", "Gnu", "Goat", "Goldfinch", "Goldfish", "Goose", "Gorilla",
    "Goshawk", "Grasshopper", "Grouse", "Guanaco", "Gull", "Hamster", "Hare",
    "Hawk", "Hedgehog", "Heron", "Herring", "Hippopotamus", "Hornet", "Horse",
    "Human", "Hummingbird", "Hyena", "Ibex", "Ibis", "Jackal", "Jaguar",
    "Jay", "Jellyfish", "Kangaroo", "Kingfisher", "Koala", "Kookabura",
    "Kouprey", "Kudu", "Lapwing", "Lark", "Lemur", "Leopard", "Lion", "Llama",
    "Lobster", "Loris", "Louse", "Lyrebird", "Magpie", "Mallard", "Manatee",
    "Mandrill", "Mantis", "Marten", "Meerkat", "Mink", "Mole", "Mongoose",
    "Monkey", "Moose", "Mouse", "Mule", "Narwhal", "Newt", "Nightingale",
    "Octopus", "Okapi", "Opossum", "Oryx", "Ostrich", "Otter", "Owl",
    "Oyster", "Panther", "Parrot", "Partridge", "Peafowl", "Pelican",
    "Penguin", "Pheasant", "Pig", "Pigeon", "Pony", "Porcupine", "Porpoise",
    "Quail", "Quelea", "Quetzal", "Rabbit", "Raccoon", "Rail", "Ram",
    "Red deer", "Red panda", "Reindeer", "Rhinoceros", "Rook", "Salamander",
    "Salmon", "Sand Dollar", "Sandpiper", "Sardine", "Scorpion", "Seahorse",
    "Seal", "Shark", "Sheep", "Shrew", "Skunk", "Snail", "Snake", "Sparrow",
    "Spider", "Spoonbill", "Squid", "Squirrel", "Starling", "Stingray",
    "Stork", "Swallow", "Swan", "Tapir", "Tarsier", "Tiger", "Toad", "Trout",
    "Turkey", "Turtle", "Viper", "Vulture", "Wallaby", "Walrus", "Weasel",
    "Whale", "Wildcat", "Wolf", "Wolverine", "Wombat", "Woodpecker", "Wren",
    "Yak", "Zebra"
  ];
  return `Anonymous ${names[djb2(String(anonId)) % names.length]}`;
}

/* Pretty format a date string */
var formatDate = (dateStr) => {
  const date = new Date(dateStr);
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = (date.getDay() + 1).toString().padStart(2, "0");
  const year = date.getFullYear().toString().substring(2, 4);
  return `${month}/${day}/${year}`;
};
