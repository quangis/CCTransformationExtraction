grammar Location;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : Wh  (L|negSign) 'the '? measure  ('in '| 'located in ') 'the '? extent (('in '|'on '| 'from ') time)? ('to ' time)? ;
negSign: Ne ;
measure :  location | locAllocation ;
location : condition? ('of '|'from '|'away from ')? ('the '|'a '|'an ')? 'nearest'? (objec|amountofObjects|field|event) condition? ;
locAllocation : 'best site for a ' ('new '|'potential')? (objec|amountofObjects) condition*;
condition : ('that '|'with ')? (topocondtion|predicondition|extrema) ;
topocondtion : topo (value* ('and ' value)?)|networkvalue ;
topo : NUM (Unit|objec)? ;
networkvalue : value ('and ' value)? 'of '? ('driving time'|'travel time') ;
predicondition : predicate value ('and ' value)? ;
predicate : Predicate ;
extrema : Extrema value? ;
objec : Object ;
amountofObjects : AmountOfObjects ;
field : Field ;
event : Event ;
extent : Extent+ ;
time : Month? NUM ;
WHITESPACE : ' ' -> skip ;
COMMA : ',' -> skip ;

// lexer rules
Wh : 'What areas '|'Where ' ;
L : 'are '|'do '|'is '|'can '|'have '|'do have '|'was ' ;
Ne : 'are not '|'do not have' ;
Field : 'commercial areas '|'flat areas '|'slope '|'altitude '|'annual minimum temperature '|'temperature '|'precipitation '|'density surface '|'land parcels'|'conservation areas '|'forestry lands '|'urban areas '|'rocky areas '|'floodplain '|'groundwater '|'natural resources ' ;
Object : 'disposal of radioactive waste '|'landscape conservation zone '|'retail store '|'fire station '|'major highway '|'city '|'road '|'library '|'ski piste '|'railway station '|'windsurfing beach '|'wind farm ' ;
AmountOfObjects: 'bus stops '|'roads '|'health care facilities '|'hospitals '|'arcades '|'playgrounds '|'schools '|'Hispanic food stores '|'cameras '|'bedrooms '|'luxury hotels '|'holiday accommodations '|'fire stations '|'population density '|'runways '|'major transport routes '|'shops '|'five star hotels '|'centroids of 2 by 2 km grid cells '|'meteorological stations '|'street lights '|'rivers '|'flower stores '|'industrial areas '|'ski pistes ';
Event : 'street noise '|'individual crimes '|'touchdowns of the tornado '|'hurricane '|'tsunami '|'auto incidents ' ;
Topo : 'affected by '|'in '|'located in '|'near to '|'within '|'covered by '|'contain '|'touch '|'equal '|'cover '|'intersect ' ;
Predicate : 'larger than '|'greater than '|'lower than '|'less than '| 'smaller than '|'between '|'more than '|'at least '|'open at ';
Extrema : 'most popular '|'most intense '|'fastest '|'minimum '|'maximum '|'maximize ' ;
NUM : [0-9]+ ;
Unit : 'degrees '|'meters '|'kilometers '|'minutes '|'percentage '|'mm '|'m '|'per square kilometer ';
Month : 'January '|'February '|'March '|'April '|'May '|'June '|'July '|'August '|'September '|'October '|'November '|'December ' ;
Extent : 'Indonesia '|'Utrecht'|'Amsterdam'|'Spain'|'UK'|'United Kingdom'|'Oleander '|'Oleander'|'Happy Valley'|'Happy Valley ski resort'|'Finland'|'Netherlands'|'Riverside San Bernardino '|'CA'|'Schiphol airport'|'Tarrant County '|'Texas'|'Italy'|'Salford'|'Zdarske Vrchy'|'Toronto'|'Portland';