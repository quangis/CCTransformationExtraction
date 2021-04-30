grammar GeoAnQu;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : ((WH ((AUX (extremaR|extreDist)? measure) | (measure AUX? false?))) | (measure 'that'? AUX? false?))
        (condition ('and'|false)?)* measure?
        (('with'|'that' AUX?)? false? subcon)?
        (('for each'|'per') support)? condition?
        ('in' (extent 'and'?)+)*
        (('in'|'on')? temEx)? ;
false : Flase ;
measure: location | (conAm coreC) | (coreC 'and'?)+ (('for'|'of'|'to'|'by'|'from') ('new'? 'each'? DIGIT? (extremaR|extreDist)? (coreC+|grid|distBandNei|('placename' DIGIT))))* ;
//measure: location | (coreC (('for'|'of'|'to'|'by'|'from') ('new'? coreC | grid))* (('to'|'from'|'of') extrema? coreC)?) ;
location: (Location1 AUX? false? (allocation|(extremaR? (coreC 'and'?)+ ('of' coreC)?)))|Location2;
conAm: ConAm ;
weight: ('weighted by' coreC ('of' coreC)?) | ('with similar' coreC);
allocation: ('best site'|'best sites') ('for'|'of') 'new'? coreC ;
condition: (topoR (grid|boolField|coreC|denNei))|('with'? boolR extremaR? DIGIT? coreC? (date|time|(predR? quantity)|percent|('of' coreC 'to' coreC*))?)|('with'? predR (boolField|(DIGIT? coreC)))|((extremaR|distanceR) (('each'? coreC ('of' coreC)?)|boolField)?)|(coreC 'of'? coreC?)|weight|topoRIn|boolField|date;  // (('with'|'that' AUX?)? false? subcon)?
grid: quantity? ('grids'|'grid cells'|'grid'|'grid cell'|'hexagonal grids'|'hexagonal grid') ('with' 'diameter of'? quantity)? ;
boolField: ((quantity 'area'?)|(time 'and'?)+) (('from'|'of')? (extremaR|extreDist)? (coreC|grid))*  ('to' extremaR? coreC)?; //('from'|'of')? extrema? coreC ('from' extrema? (coreC|grid))?
subcon: (coreC predR quantity)|(topoR (boolField|coreC))|(predR coreC)|(distanceR coreC ('of' coreC)?);
topoR: TOPO ;
topoRIn: 'in' (coreC ('of' coreC)?|denNei);
boolR: Boolean ;
extremaR: Extrema ;
distanceR: Distance ;
extreDist: ExtreDist ;
predR: Predicate ;
quantity: 'equantity' DIGIT ;
date: 'edate' DIGIT ;
time: 'etime' DIGIT ;
percent: 'epercent' DIGIT ;
denNei: quantity ('circle'|'rectangle') ;
distBandNei: DIGIT 'nearest neighbors' ;
distBand: (quantity 'distance band') | ('distance band' quantity 'by' quantity 'increments') ;
coreC: ('field' DIGIT ML)| ('object' DIGIT) |('objectquality' DIGIT ML)|('event' DIGIT)|('eventquality' DIGIT ML)
|('network' DIGIT)|('objconamount' DIGIT ML)|('eveconamount' DIGIT ML)|('conamount' DIGIT ML)|('covamount' DIGIT ML)
|('amount' DIGIT)|('objconobjconpro' DIGIT ML)|('eveconobjconpro' DIGIT ML)|('objconobjcovpro' DIGIT ML)
|('conconpro' DIGIT ML)|('concovpro' DIGIT ML)|('covpro' DIGIT ML)|('proportion' DIGIT ML);
support : grid | coreC | distBand;
extent: 'placename' DIGIT ;
temEx: 'edate' DIGIT ;


// lexer rules
WH : 'which'|'what'|'from where' ;
Location1 :  'where' ;
Location2 : 'what area'|'what areas' ;
ConAm : 'how many' ;
AUX : 'is'|'are'|'was'|'were' ;
Flase : 'not'|'but not' ;
TOPO : 'inside'|'located in'|'within'|'covered by'|'away from'|'contain'|'contains'|'touch'|'equal'|'cover'|'intersected with'|'intersects with'|'on top of'|'outside'|'affected by';
Boolean : 'have'|'has'|'visible'|'for sale'|'open at'|'aged'|'answered by'|'no';
Extrema : 'longest'|'highest'|'biggest'|'most popular'|'fastest'|'most intense'|'minimum'|'maximum'|'maximize';
Distance : 'closest to' ;
ExtreDist : 'nearest'|'closest';
Predicate : 'lower than'|'larger than'|'at least'|'less than'|'more than';
ML : 'nominal'|'boolean'|'ordinal'|'interval'|'ratio'|'era'|'ira'|'count'|'loc';
DIGIT: [0-9]+;
WS: [ \n\t\r]+ -> skip;
COMMA: ',' -> skip;
