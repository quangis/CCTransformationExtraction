grammar EventNetwork;

// parser rules start with lowercase letters, lexer rules with uppercase
//start
start : Wh L 'the '? measure 'in ' 'the '? extent time? ;
// measures for object questions
measure : (Spec* event) | (Spec* eventQ 'of ' 'the '? event) | (Spec* network  'from ' ('a ' | 'an ' | 'the ')? Spec* objec 'to ' ('a ' | 'an ' | 'the ')? Spec* objec ) | (network 'of ' 'the '? (network | objec)) | (network 'to ' 'the ' Spec* objec 'for ' 'the '? objec condition* ) ;
event : Spec* Event ;
//(start What  was  the  (measure (event most intense  hurricane )) in  (extent Oleander) (time in  2019))
//(start What  are  the  (measure (event (track trajectories  of the  birds
// (condition (booleanC (binaryOC that  cross  national parks )))))) in  (extent America) (time from  2010 to  2019))
eventQ : EventQ;
//(start What  is  the  (measure (eventQ average  speed  of the  hurricanes )) in  (extent Oleander) (time in  2019))
objec: Object;
// network
network : Network;
//(start What  is  the  (measure (network quickest  route
// (networkSpec from  the  center of the resort  to  a  new  ski piste ))) in  (extent Happy Valley))

// Object Conditions
condition : ordinalC | booleanC ;
ordinalC : 'that was '? (Predicate NUM ('and ' NUM)* Unit*)+ ;
//(start What  are  the  (measure (event (track trajectories  of the  birds
// (condition (ordinalC that was  less than  1 year old ))))) in  (extent America) (time in  2019))
booleanC : binaryOC ;
binaryOC : ('that ')? Verb Object ;
//(start What  are  the  (measure (event (track trajectories  of the  birds
// (condition (booleanC (binaryOC that  cross  national parks )))))) in  (extent America) (time from  2010 to  2019))

extent: Extent ;
time: ('in ' Year Month?) | ('from ' Year Month? 'to ' Year Month?) ;
WHITESPACE : ' ' -> skip ;


// lexer rules
Wh : 'What ' ;
L : 'is ' | 'was ' |  'are ';
Spec : 'most intense ' | 'new ' | 'average ' | 'quickest ' | 'nearest ' ;
Event : 'hurricane ' | 'incident ' | 'hurricanes ' | 'arsons ' ;
Track : 'trajectories ' ;
EventQ : 'speed ' ;
Object : 'birds ' | 'national parks ' | 'a station ' | 'center of the resort ' | 'ski piste ' | 'A28 motorway ' | 'primary school ' | 'children ';
Network : 'route' | 'traffic flow ' | 'distance ' | 'travel time ' ;
Verb :  'cross ' | 'answered by ' ;
Predicate : 'less than ' | 'between ' ;
NUM : [0-9]+ ;
Unit : 'years old ' | 'year old ' ;
Year : [0-9]+ ;
Month : 'January ' | 'February ' | 'March ' | 'April ' | 'May ' | 'June ' | 'July ' | 'August ' | 'September ' | 'October ' | 'November ' | 'December ' | 'June' ;
Extent : 'Utrecht' | 'Amsterdam' | 'Happy Valley' | 'Rotterdam' | 'Oleander' | 'Netherlands' | 'Fort Worth' | 'Dallas County' | 'America';







