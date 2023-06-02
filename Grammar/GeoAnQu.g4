grammar GeoAnQu;

// parser rules start with lowercase letters, lexer rules with uppercase
start: ((measure (AUX|(false AUX))?) | (WH1 AUX false? measure) | (WH2 measure AUX false?) | (Location1 AUX false? measure))
       (condition ('and'|false)? measure1?)*
       (support condition?)?
       extent temporalex? ;
//start : ((WH ((AUX (extremaR|extreDist)? measure) | (measure AUX? false?))) | (measure 'that'? AUX? false?))
//        (condition ('and'|false)?)* measure1?
//        support? condition?
//        extent temporalex?;
//(('with'|'that' AUX?)? false? subcon)?
//(('in'|'on'|'from')? temEx 'to'? temEx?)?
false : Flase ;
measure : mergeO | location | (conAm coreC) | allocation | (aggre? coreC) | (aggre? coreC ('of'|'to'|'for') coreC weight?) |
          (coreC 'of' coreC 'to' aggre? coreC ('of' coreC)?) |
          ((aggre|(coreC 'of'))? (networkC|networkQ|objectQ) ('along' networkC)? (('to'|'through')? destination)? (('from'|'for'|'of')? 'each'? origin)? (('to'|'through')? destination)? ('along' networkC)?) |
          (objectQ 'by' networkC) | (networkQ 'of' networkC) | (aggre? coreC 'to' DIGIT 'nearest neighbors' ('for'|'of') coreC);
measure1: 'to' aggre? coreC;
location: (Location1 AUX? false? extremaR? coreC) | Location2;
conAm: ConAm ;
allocation: 'allocation' DIGIT ('for'|'of') 'new'? coreC ;
mergeO: coreC ('and'? coreC)+ ;
weight: ('weighted by' aggre? coreC ('of' coreC)?) | ('with similar' aggre? coreC);
condition: boolField | (topoR coreC ('from' coreC)? subcon?) |
           (aggre? coreC? (compareR quantityV 'and'?)+) | ('along' networkC 'from' origin 'to' destination) |
           ('that'? extremaR 'each'? aggre? coreC? ('of' coreC 'to' aggre? coreC)? subcon?) |
           (booleanR coreC subcon?) | (coreC subcon?) | ('with'? compareR? conAmount) | visible ;
//boolField | (topoR (grid|(coreC ('of' ((coreC 'from' origin 'to' destination)|coreC))?)|densityNei))|
//           ('with'? boolR 'from'? DIGIT? (extremaR|aggre)? coreC? (('of' coreC 'to' coreC+)|('of'? compareR? (quantityV|coreC))|date|time|percent)?)|
//           (('with'|'of')? compareR (quantityV|distField|(DIGIT? coreC)))|
//           ((extremaR|distanceR) ('each'? coreC ('of' coreC)?)?)|
//           topoRIn | coreC | date ;  //(coreC time? 'of'? coreC?) // (('with'|'that' AUX?)? false? subcon)?
//grid: quantity? ('grids'|'grid cells'|'grid'|'grid cell'|'hexagonal grids'|'hexagonal grid'|'hexagon grid') ('with' 'diameter of'? quantity)? ;
//boolField: (topoR|compareR|extremaR)? (distField|serviceObj|(coreC 'from' coreC));
boolField: (topoR|compareR) (distField|serviceObj) ;
distField: quantityV ('distfield' DIGIT ML)? ('from'|'of'|'to') extremaR? (coreC|(networkC (('from'|'for'|'of') origin)? ('to' destination)?)) ;
serviceObj: (time|quantityV)+ 'of'? networkQ (('from'|'for'|'of') origin)? ('to' destination)? ;
//origin: ('from'|'for'|'of')? (extremaR|extreDist)? (objectC|(quantity? grid)) ('of' (objectC|quantity? grid))? ;
//destination: 'to'? DIGIT? (extremaR|extreDist)? objectC;
origin: DIGIT? (extremaR|'each')? objectC? 'of'? (objectC|eventC|grid)+ ;
destination: DIGIT? (extremaR|'each'|'every')? ((objectC|eventC) 'and'? 'every'?)+;
conAmount: DIGIT coreC ;
subcon: (('that' AUX false?)|'with')? ((topoR 'each'? coreC) | (coreC compareR quantityV) | (extremaR coreC) | boolField);
//((topoR|extremaR) (distField|serviceObj))
//subcon: (coreC compareR quantityV)|
//        boolField |
//        (topoR coreC)|
//        (compareR coreC)|
//        (distanceR coreC ('of' coreC)?);
aggre: 'aggregate' DIGIT;
topoR: 'toporel' DIGIT;
//topoRIn: 'in' (coreC ('of' coreC)?|densityNei);
//boolR: Boolean ;
extremaR: 'extrema' DIGIT;
//distanceR: Distance ;
//extreDist: ExtreDist ;
booleanR: 'boolean' DIGIT;
compareR: 'comparison' DIGIT;
quantityV: 'quantity' DIGIT ;
time: 'time' DIGIT ;
//date: 'edate' DIGIT ;
//percent: 'epercent' DIGIT ;
//densityNei: DensityNei ;
//densityNei: quantity ('circle'|'rectangle') ;
distBandNei: 'nearest neighbors' ;
//distBand: (quantityV 'distance band') | ('distance band' quantityV 'by' quantityV 'increments') ;
grid: 'grid' DIGIT;
networkC: 'network' DIGIT ;
networkQ: 'networkquality' DIGIT ML ;
objectC: 'object' DIGIT ;
objectQ: 'objectquality' DIGIT ML;
eventC: 'event' DIGIT ;
coreC: ('field' DIGIT ML)|('object' DIGIT)|('objectquality' DIGIT ML)|('event' DIGIT)|('eventquality' DIGIT ML)
|('objconamount' DIGIT ML)|('eveconamount' DIGIT ML)|('conamount' DIGIT ML)|('covamount' DIGIT ML)
|('amount' DIGIT)|('objconobjconpro' DIGIT ML)|('eveconobjconpro' DIGIT ML)|('objconobjcovpro' DIGIT ML)|('eveconobjcovpro' DIGIT ML)
|('conconpro' DIGIT ML)|('concovpro' DIGIT ML)|('covpro' DIGIT ML)|('genpro' DIGIT ML)|('concept' DIGIT)|('region' DIGIT);
visible: 'visible' ;
support : 'support' ;
extent: 'extent' ;
temporalex: 'temporalex' ;


// lexer rules
WH1 : 'what'|'from where' ;
WH2 : 'which' ;
Location1 : 'where' ;
Location2 : 'what area'|'what areas' ;
ConAm : 'how many' ;
AUX : 'is'|'are'|'was'|'were'|'has'|'have' ;
Flase : 'not'|'but not' ;
//Aggregate : 'aggregate';
//TOPO : 'toporel';
//Quantity : 'quantity';
//Boolean : 'have'|'has'|'had'|'visible'|'visible from'|'aged'|'answered by'|'no';
//Extrema : 'extrema' ;
//Distance : 'closest to'|'nearest to' ;
//ExtreDist : 'nearest'|'closest';
//Compare : 'comparison';
//Grid: 'grid';
//DensityNei: 'densityNei';
ML : 'int_'|'nom_'|'rat_'|'cou_'|'loc_'|'ord_'|'era_'|'ira_'|'bool_';
DIGIT: [0-9]+;
WS: [ \n\t\r]+ -> skip;
COMMA: ',' -> skip;