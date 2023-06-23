grammar GeoAnQu;

// parser rules start with lowercase letters, lexer rules with uppercase
start: ((measure (AUX|(false AUX))?) | (WH1 AUX false? measure) | (WH2 measure AUX false?) | (Location1 AUX false? measure))
       (condition ('and'|false)? measure1?)*
       (support condition?)?
       extent temporalex? ;
false : Flase ;
measure : mergeO | location | (conAm coreC) | allocation | (aggre? coreC) | (aggre? coreC ('of'|'to'|'for') 'each'? coreC weight?) |
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
           ('with'? aggre? (coreC ('of' coreC)?)? (compareR quantityV 'and'?)+) | ('along' networkC 'from' origin 'to' destination) |
           ('that'? extremaR 'each'? aggre? coreC? ('of' coreC 'to' aggre? coreC)? subcon?) |
           (booleanR coreC subcon?) | visible | (coreC subcon?) | ('with'? compareR? conAmount) ;
boolField: (topoR|compareR) (distField|serviceObj) ;
distField: quantityV ('distfield' DIGIT)? ('from'|'of'|'to') extremaR? (coreC|(networkC (('from'|'for'|'of') origin)? ('to' destination)?)) ;
serviceObj: (time|quantityV)+ 'of'? networkQ (('from'|'for'|'of') origin)? ('to' destination)? ;
origin: DIGIT? (extremaR|'each')? objectC? 'of'? (objectC|eventC|grid)+ ;
destination: DIGIT? (extremaR|'each'|'every')? ((objectC|eventC) 'and'? 'every'?)+;
conAmount: DIGIT coreC ;
subcon: (('that' AUX false?)|'with')? ((topoR 'each'? coreC) | (coreC compareR quantityV) | (extremaR coreC) | boolField);
aggre: 'aggregate' DIGIT;
topoR: 'toporel' DIGIT;
extremaR: 'extrema' DIGIT;
booleanR: 'boolean' DIGIT;
compareR: 'comparison' DIGIT;
quantityV: 'quantity' DIGIT ;
time: 'time' DIGIT ;
distBandNei: 'nearest neighbors' ;
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
ML : 'int_'|'nom_'|'rat_'|'cou_'|'loc_'|'ord_'|'era_'|'ira_'|'bool_';
DIGIT: [0-9]+;
WS: [ \n\t\r]+ -> skip;
COMMA: ',' -> skip;