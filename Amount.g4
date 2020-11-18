grammar Amount;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : Wh measure condition? ('for each '|'answered by each ' support)? (('in '| 'located in ')? 'the '? extent )+ (('in '|'on '| 'from ') time)? ('to ' time)? ;
measure : objectCountAmount | eventCountAmount | objectRatioAmount | fieldRatioAmount | eventRatioAmount | objectLocationamount | eventLocationamount ;
objectCountAmount : countAmount 'of ' 'the '? (objec|amountofObjects);
countAmount : CountAmount ;
eventCountAmount : countAmount 'of ' 'the '? event;
objectRatioAmount : ratioAmount 'of ' 'the '? (objec|amountofObjects);
eventRatioAmount : ratioAmount 'to ' event;
fieldRatioAmount : ratioAmount 'of ' ('the'|'each ')? field;
ratioAmount : RatioAmount ;
objectLocationamount : locationamount ('of '|'in ') 'the '? (objec|amountofObjects) (('weighted by '|'with ') ('the '|'their ')? weightedfield)? ;
eventLocationamount : locationamount ('of '|'in ') 'the '? event (('weighted by '|'with ') ('the '|'their ')? weightedfield)? ;
locationamount : LocationAmount ;
weightedfield : Quality ;
condition : ('that '|'with ')? (topocondtion|predicondition) ;
//condition : ('that '|'with ')? (topocondtion|predicondition|extrema) ;
topocondtion : topo ('a '| 'the ')? ((networkvalue ('from ' origins)? ('to ' destinations)?)|(value* 'of ' 'the'? (objec|amountofObjects))|(value* ('and ' value)?)|grid|event|field) ;
origins: objec|amountofObjects ;
destinations: objec|amountofObjects ;
topo : Topo ;
value : NUM (Unit|objec)? ;
networkvalue : value ('and ' value)? (('of '? 'driving time')|'network distance ');
predicondition : predicate value ('and ' value)? ;
predicate : Predicate ;
//extrema : Extrema value? ;
field : Field ;
objec : Object ;
amountofObjects : AmountOfObjects ;
event : Event ;
support : Object | grid ;
grid : NUM ('by ' NUM)? Unit ('area '|'distance band '|'radius '|'rectangle '|'grid cells ');
extent : Extent ;
time : Month? NUM ;
COMMA : ',' -> skip ;
WHITESPACE : ' ' -> skip ;

// lexer rules
Wh : 'What is the ' |'What are the '| 'How much do people ' | 'Where are the ' | 'Where is the ';
CountAmount : 'number ' ;
RatioAmount : 'percentage ' | 'average percentage '|'exposure '|'total area' ;
LocationAmount : 'mean center '|'central feature '|'standard distance circles '|'directional trend '|'directional trends '|'mean direction '|'clusters '|'degree of clustering '|'degree of dispersion ';

Field : 'water areas '|'street noise '|'noise polluted areas '|'soil type '|'residential areas '|'commercial areas '|'flat areas '|'slope '|'altitude '|'annual minimum temperature '|'temperature '|'precipitation '|'density surface '|'land parcels'|'conservation areas '|'forestry lands '|'urban areas '|'rocky areas '|'floodplain '|'flood zones '|'groundwater '|'natural resources ' ;
Object : 'alarm territory '|'PC4 area' |'district '|'school district '|'central station '|'state '|'park '|'census block '|'census tract '|'precinct '|'neighborhood '|'disposal of radioactive waste '|'landscape conservation zone '|'retail store '|'fire station '|'major highway '|'city '|'road '|'library '|'ski piste '|'railway station '|'windsurfing beach '|'wind farm ' ;
AmountOfObjects: 'neighborhoods '|'census blocks '|'customers '|'freeways '|'library patrons '|'bank branches '|'water wells '|'seriously lonely people '|'sport facilities '|'elderly people '|'high school students '|'households '|'dwelling units '|'tractors '|'people '|'buildings '|'bus stops '|'roads '|'health care facilities '|'senior high schools '|'population '|'Hispanic population '
|'hospitals '|'arcades '|'playgrounds '|'schools '|'Hispanic food stores '|'cameras '|'bedrooms '|'luxury hotels '|'holiday accommodations '|'fire stations '|'population density '|'runways '|'owner occupied houses '|'bald eagles '|'PC4 areas '
|'major transport routes '|'shops '|'five star hotels '|'centroids of 2 by 2 km grid cells '|'meteorological stations '|'street lights '|'rivers '|'flower stores '|'industrial areas '|'ski pistes '|'primary schools '|'vacant houses ';
Event : 'accidents '|'crimes '|'flu cases '|'West Nile Virus '|'animal grazing '|'false fire alarms '|'fire alarms '|'animal migration '|'tornadoes '|'crime '|'individual crimes '|'touchdowns of the tornado '|'hurricane '|'tsunami '|'auto incidents '|'election votes '|'arsons ' |'fire calls ' |'incidents ';
Quality : 'similar priority '|'priority '|'transactions '|'employee number '|'similar income '|'similar crime rate '|'severity ';
Topo : 'inside '|'affected by '|'in '|'located in '|'near to '|'within '|'covered by '|'contain '|'touch '|'equal '|'cover '|'intersect ' ;
Predicate : 'larger than '|'greater than '|'lower than '|'less than '| 'smaller than '|'between '|'more than '|'at least '|'open at ';
//Extrema : 'most popular '|'most intense '|'fastest '|'minimum '|'maximum '|'maximize ' ;
NUM : [0-9]+ ;
Unit : 'degrees '|'meters '|'kilometers '|'minutes '|'mm '|'m '|'per square kilometer '|'years '|'square km';
Month : 'January '|'February '|'March '|'April '|'May '|'June '|'July '|'August '|'September '|'October '|'November '|'December ' ;
Extent : 'Tarrant '|'Oost district '|'Baltimore '|'Indonesia '|'Rotterdam'|'Utrecht'|'Amsterdam'|'Spain'|'UK'|'United Kingdom'|'Oleander '|'Oleander'|'Happy Valley'|'Happy Valley ski resort'|'Finland'|'Netherlands'|'Riverside San Bernardino '|'Fort Worth'
|'CA'|'Schiphol airport'|'Texas'|'Italy'|'Salford'|'Zdarske Vrchy'|'Toronto'|'Portland'|'Dallas'|'United States ';