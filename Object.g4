grammar Object;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : Wh measure? (L | negSign) 'the '? (objectCondition | measure )? ('in ' | 'of ') 'the '? extent ;
// Wh measure + objectCondition: Which ski piste is longest in the Happy Valley
// measure: What is the population density of Utrecht
negSign: Ne ;

// measures for object questions
measure : object | amountOb | objectQuality ; //objectQuality contains amountOfObjectQuality
object : Object ;
// (start Which  (measure (object ski piste )) is  (objectCondition (ordinalOC longest )) in  the  Happy Valley)
amountOb : AmountOfOb ;
// (start Which  (measure (amountOb buildings )) are  (objectCondition (distV within  1 minute of driving time  from  a  fire station )) in  Fort Worth)
objectQuality : Spec* (objectQ | nearDistanceQ) | countquality ;
// (start What  is  the  (measure (objectQuality (objectQ population density ))) of  Utrecht)
//(start What  is  the  (measure (objectQuality (nearDistanceQ travel time  to  the  nearest  hospital  (support for  each  pc6 area )))) in  Utrecht)
// subject of nearRelation - pc6 area, also support is automatically the subject
nearDistanceQ : ('travel time ' | 'travel distance ') objectOfNearRelation ;
objectOfNearRelation : 'to ' 'the ' Spec* (Object | AmountOfOb) ('for ' ('the '? Spec* (Object | AmountOfOb) Spec*) | support)? ; // To do: Spec = nearest; seperate support
//What is the distance to the nearest primary school for the households with children aged between 4 and 12 year old in Rotterdam
// subject of nearRelation - household
countquality : 'the number of' AmountOfOb 'that are ' objectCondition ;
//(start What  is  (measure (objectQuality (countquality the number of buildings
// that are  (objectCondition (distC within  1 minute of driving time  from  a  fire station ))))) in  Oleander)

// Object Conditions
objectCondition: ordinalOC | booleanOC ;
ordinalOC: 'that has the '? Spec objectQ? ;
//(start Which  (measure (objectLayer ski piste )) is  (objectCondition (ordinalOC longest )) in  the  (extent Happy Valley))
//?? (start Where  is  the  (measure (objectLayer neighborhood )) that has the  highest  crime rate  in  Amsterdam)
objectQ : ('crime rate ' | 'population density ' | ('concentration of ' AmountOfOb) | 'potential accessibility ' ) support? ; //TO do: seperate support

booleanOC : distOC | topoOC | relationOC ;
topoOC :Topo 'the '* (('an ' | 'a ' )? Object | Event | support) ;
//(start Which  (measure (objectLayer fire station )) is
// (objectCondition (booleanOC (topoOC nearest to  the  incident ))) in  (extent Fort Worth))
distOC : Topo NUM Unit 'from ' ( ('an ' | 'a ')? Object) | AmountOfOb ;
//(start Which  (measure (amountOb buildings )) are
// (objectCondition (booleanOC (distOC within  1 minute of driving time  from  a  fire station ))) in  (extent Fort Worth))
relationOC: Verb ('an ' | 'a ')? (Object | Event) ;
//(start Which  (measure (amountOb buildings )) are  (objectCondition (booleanOC (relationOC affected  by  a  hurricane ))) in  (extent Oleander))

support : 'for '? 'each ' Object ;
extent: Extent ;
WHITESPACE : ' ' -> skip ;


// lexer rules
Wh : 'Which ' | 'Where ' | 'What ' ;
L : 'is ' | 'has ' |  'are ';
Ne : 'is not ' | 'does not have ' ;
Object : 'neighborhood ' | 'house ' | 'city ' | 'park ' | 'people ' | 'ski piste ' | 'fire station ' | 'hospital ' | 'primary school ' | 'precinct ' | 'pc6 area ';
AmountOfOb : 'birds ' | 'buildings ' | 'fire stations ' | 'children ' | 'households ';
Event : 'incident ' | 'hurricane ';
Spec : 'highest ' | 'longest ' | 'lowest ' | 'nearest ' | 'average ' | 'minimun ' | 'maximum ' | 'aged between 4 and 12 ';
Topo : 'in ' | 'located in ' | 'near to ' | 'nearest to ' | 'within ' | 'covered by '| 'away from ' | 'contain ' | 'touch ' | 'equal ' | 'cover ' | 'intersect ' ;
Verb :  'lit by ' | 'affected by ' ;
NUM : [0-9]+ ;
Unit : 'degrees ' | 'meters ' | 'kilometers ' | 'minute of driving time ' ;
Extent : 'Utrecht' | 'Amsterdam' | 'Rotterdam' | 'UK' | 'Oleander' | 'Happy Valley' | 'Texas' | 'Netherlands' | 'Fort Worth' | 'Dallas County';







