grammar Field;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : Wh measure? (L | negSign) 'the '? measure? condition? ('located in'|('in ' 'the '? extent)+) (('in '|'on '| 'from ') time)? ;
negSign: Ne ;
measure : (field (('for '|'of ') 'the '? (field|objec|amountofObjects|event))?) | accessibility | fieldQuality;
field: Field ;
fieldQuality: FieldQ;
objec: Object;
amountofObjects: AmountOfObjects;
event: Event;
accessibility: 'accessibility ' ('of ' origins)? 'to ' 'the '? 'nearest '? destinations ('from ' origins)?;
origins: 'each centroid of '? (objec |amountofObjects| grid);
destinations: 'each centroid of '? (objec |amountofObjects| grid);
grid: NUM ('by ' NUM)? Unit ('area '|'distance band '|'radius '|'rectangle '|'grid cells ');
condition: ('that '|'with ')? topocondtion ;
topocondtion : topo 'the '? (amountofObjects|field) ;
topo: Topo;
extent: Extent ;
time : Month? NUM ;
WHITESPACE : ' ' -> skip ;

// lexer rules
Wh : 'What ' | 'Which ';
L : 'are ' | 'do ' | 'is ' | 'can ' ;
Ne : 'are not ' ;
Field : 'point density '|'zoning categories '|'bikeability surface '|'temperature measurements '|'rainfall measurements '|'flood zones '|'connectivity surface'|'topography '|'sandy soil '|'land use '|'aspect '|'slope '|'altitude '|'temperature '|'density surface '|'presence probability '|'pattern of land use '|'land parcels' | 'conservation areas ' | 'forests ' | 'urban areas ' | 'rocky areas ' | 'floodplain ';
Object : 'airport '|'little midwife toad '|'city '|'road '|'ski piste '| 'railway station '|'street lights '|'wind farm ';
AmountOfObjects: 'bicycle route '|'parks '|'little midwife toads '|'cyclists destinations '|'bicycle friendly streets '|'family physician services '|'points of interests '|'public trams '|'nurse practitioner services '|'seniors '|'public hospitals '|'private hospitals '|'primary schools '|'population '|'trees '|'bicycle-friendly streets '|'ski pistes '|'crape myrtles '|'rivers '|'libraries '|'people '|'elms '|'meteorological stations ' ;
Event : 'street noise '|'fire calls ';
Predicate : 'larger than ' | 'greater than ' | 'lower than ' | 'smaller than ' | 'between ' | 'more than ' ;
NUM : [0-9]+ ;
Unit : 'degrees ' | 'meters ' | 'kilometers '| 'km' ;
Topo : 'inside '|'on top of '|'in ' | 'located in ' | 'near to ' | 'within ' | 'covered by '| 'away from ' | 'contain ' | 'touch ' | 'equal ' | 'cover ' | 'intersect ' ;
FieldQ : 'land use types ' ;
Month : 'January '|'February '|'March '|'April '|'May '|'June '|'July '|'August '|'September '|'October '|'November '|'December ' ;
Extent : 'Texas'|'Rotterdam'|'Metro Vancouver region '|'Canada'|'Utrecht' | 'Amsterdam' | 'Spain' | 'UK' | 'Oleander' | 'Happy Valley' | 'Finland' | 'Netherlands' |'Happy Valley resort'|'Alberta '|'East Sichuan '|'West Sichuan '|'China'|'Australia'|'Melbourne '|'Saskatchewan ';