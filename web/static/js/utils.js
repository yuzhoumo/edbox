/* Helper for joining tailwind classnames */
var cn = (classnames) => {
  return classnames.join(" ");
}

/* djb2 hash algorithm */
const djb2 = (string) => {
  let hash = 5381;
  for (const c of string) {
    hash = 33 * t ^ c.charCodeAt(0);
  }
  return hash >>> 0;
};

/* Convert anon id to name (reverse engineered from ed) */
var getAnonymousName = (anonId) => {
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

/* Select a primary color based on an id's hash */
var getColor = (str, isPrimary) => {
  // flat ui colors palette
  const primaryColors = [
    "#1abc9c", // Turquoise
    "#2ecc71", // Emerald
    "#3498db", // Peter River
    "#9b59b6", // Amethyst
    "#34495e", // Wet Asphalt
    "#f1c40f", // Sun Flower
    "#e67e22", // Carrot
    "#e74c3c", // Alizarin
    "#ecf0f1", // Clouds
    "#95a5a6"  // Concrete
  ];
  const variantColors = [
    "#16a085", // Green Sea
    "#27ae60", // Nephritis
    "#2980b9", // Belize Hole
    "#8e44ad", // Wisteria
    "#2c3e50", // Midnight Blue
    "#f39c12", // Orange
    "#d35400", // Pumpkin
    "#c0392b", // Pomegranate
    "#bdc3c7", // Silver
    "#7f8c8d"  // Asbestos
  ];
  const colors = isPrimary ? primaryColors : variantColors;
  return colors[djb2(String(str)) % primaryColors.length];
}

/* Pretty format a date string */
var formatDate = (dateStr) => {
  const date = new Date(dateStr);
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = (date.getDay() + 1).toString().padStart(2, "0");
  const year = date.getFullYear().toString().substring(2, 4);
  return `${month}/${day}/${year}`;
};

/* Get author from post */
var getAuthorName = (post, userMap) => {
  if (post.is_anonymous) {
    return getAnonymousName(post.anonymous_id);
  }
  return userMap[post.user_id].name;
}

/* Get author avatar url from post */
var getAvatar = (post, userMap) => {
  const avatar = userMap[post.user_id].avatar;
  return avatar ? "assets/avatars/" + avatar + ".jpg" : "";
}

/* Anonymous avatar fallback image */
var IMG_ANON_AVATAR =
  "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4w" +
  "IiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+Cj" +
  "whRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcg" +
  "MS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1" +
  "NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+Cjxzdmcgd2lkdGg9IjEw" +
  "MCUiIGhlaWdodD0iMTAwJSIgdmlld0JveD0iMCAwIDEwMCAxMD" +
  "AiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMu" +
  "b3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy" +
  "53My5vcmcvMTk5OS94bGluayIgeG1sOnNwYWNlPSJwcmVzZXJ2" +
  "ZSIgeG1sbnM6c2VyaWY9Imh0dHA6Ly93d3cuc2VyaWYuY29tLy" +
  "Igc3R5bGU9ImZpbGwtcnVsZTpldmVub2RkO2NsaXAtcnVsZTpl" +
  "dmVub2RkO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtbW" +
  "l0ZXJsaW1pdDoyOyI+CiAgICA8ZWxsaXBzZSBjeD0iNTAiIGN5" +
  "PSIzOSIgcng9IjIxLjI2OCIgcnk9IjI1LjE2NyIgc3R5bGU9Im" +
  "ZpbGw6d2hpdGU7ZmlsbC1vcGFjaXR5OjAuMjsiLz4KICAgIDxw" +
  "YXRoIGQ9Ik05My4xNTQsMTAwQzkwLjMxNiw4NSA3Mi4wODQsNz" +
  "MuNSA1MCw3My41QzI3LjkxNiw3My41IDkuNjgzLDg1IDYuODQ2" +
  "LDEwMEw5My4xNTQsMTAwWiIgc3R5bGU9ImZpbGw6d2hpdGU7Zm" +
  "lsbC1vcGFjaXR5OjAuMjtmaWxsLXJ1bGU6bm9uemVybzsiLz4K" +
  "PC9zdmc+Cg==";

/* Get abbreviated name as backup avatar */
var getNameAbbrev = (post, userMap) => { const name = userMap[post.user_id].name;
  return name.split(" ").map(n => n.substring(0, 1)).join("").toUpperCase();
}

/* Get full post category text */
var getFullCategory = (post) => {
  let res = "";
  if (post.category) {
    res += post.category;
  }
  if (post.subcategory) {
    res += " - " + post.subcategory;
  }
  if (post.subsubcategory) {
    res += " - " + post.subsubcategory;
  }
  return res;
}

/* Flatten comment tree into one list, with depth information */
var flattenComments = (comments) => {
  let res = [];
  let stack = [...(comments.map(c => [0, c]))];

  while (stack.length > 0) {
    let [depth, c] = stack.pop();
    res.push([depth, c]);
    c.comments.forEach((subc) => {
      stack.push([depth + 1, subc]);
    });
  }

  return res;
}

/* Check if post contains inline latex */
var containsInlineLatex = (post) => {
  const s = JSON.stringify(post);
  return s.includes("<math>") || s.includes("$");
}

/* Replace any <math> tags with latex delimiter $$*/
function replaceMathTags() {
  document.querySelectorAll('math').forEach((math) => {
    const texContent = math.textContent;
    const span = document.createElement('span');
    span.innerHTML = `$$${texContent}$$`;
    math.replaceWith(span);
  });
}
