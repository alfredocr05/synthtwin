"""A built-in list of common given names, the persons' names reader's one list (release 37, lane PRIVACY).

WHY IT EXISTS. The persons' names reader (`taxonomy.persons_names_hold`,
plans P4-D478 and P4-D494) reads a column of names from the SHAPE of its
values alone: every name word opens with a capital, or the whole cell is
in capitals. A column of names written in small letters (`garcia,
maria`), one given name alone (`Maria`), or a given name beside an
initial (`maria g.`) has no shape that tells it from a column of
ordinary labels, so it was read as labels: on the shipped route at the
owner's floor, 1,000 names written in small letters, each on 20 rows,
put no question, and the twin wrote all 20,000 of its cells as real
names. A given name is the signal such a value still carries, and the
owner ruled that a built-in list of common given names may read it.

WHAT IT IS. GENERIC PUBLIC KNOWLEDGE: common given names across the
languages a health table in the United States meets -- English,
Spanish, Portuguese, Italian, French, German, Polish, Russian, Irish,
Nordic, Arabic, Persian, Turkish, Hebrew, the languages of India, West
and East Africa, Vietnamese, Chinese and Japanese written in Latin
letters, and Korean -- written from general knowledge for this
repository. Nothing in it comes from any person's table, any
institution's records or any download; it is a fixed part of the code,
the same on every computer, and nothing is learnt from the table read.

WHAT IT LEAVES OUT. Each name is three letters or more, in small letters
with its marks set aside (`Jose` for `José`). A given name that is also
an ordinary word, a month or a weekday, a unit's or a test's
abbreviation, a colour, a gem, a plant, a virtue, a season or the
weather, a place (a state, a city, a country), a role, or a word a
clinical label holds is left out (`STOP`, which the gate file holds
apart from the list): the list is read as evidence that a value names a
person, so a word that names something else is no evidence. A name the
list lacks is simply not read by it; the reader's own shapes still read
it where its capitals do.

HOW IT IS READ. `taxonomy._a_name_by_its_given_name`: a value of no
figure whose words, folded, hold one of these names is a name where it
is that one word alone, or where the same value written with each word
opening with a capital is a name written whole by the reader's own
rule. A column is then held only as before: at least
`taxonomy.NAMES_AT_LEAST` different values read as names, and half of
the different values read or more.

Guarantees: a fixed, sorted, duplicate-free set of 2,369 names in small
ASCII letters; no I/O.
"""

# THE NAMES, in small ASCII letters, sorted, one space between them.
_LISTED = """
aaliyah aarav aaron abby abdelrahman abdul abdulaziz abdullah abdulrahman abebe abel abena abhishek abigail
abiodun aboubacar abraham abu achieng ada adaeze adam adama addie adebayo adela adelaide adele adelina adeline
adewale adeyemi aditi aditya adnan adolfo adrian adriana adrienne adwoa agata agnes agnieszka ahlam ahmad ahmed
ahn aidan aiden aileen aine aisha aissatou aiyana ajay akash akiko akinyi akio akira akosua akua alan alana
alassane alastair albert alberta alberto aldo alec alejandra alejandro alejo aleksandar aleksander aleksandra
alemayehu alemu alessandra alessandro alessia alex alexa alexander alexandra alexandria alexei alexis alfonsina
alfonso alfred alfreda alfredo ali alice alicia alina alisha alison alissa aliyah alla allan allen allison
allyson alma almaz alondra alonzo alphonse alton alvaro alvin alyssa amadou amal amanda amani amara amarjit
amelia amelie amin amina aminata amir amira amit amitabh amna amos amparo amy ana anabel anahi anais analyn
anand ananth ananya anastasia anatoly anders andre andrea andreas andrei andres andrew andy angela angelina
angelo angie anh anika anil anita anjali anke ann anna annabelle anne anneliese annette annie anselmo anthony
antoine antoinette anton antonella antonia antonio anupama anwar anya aoi aoibheann aoife araceli aracely arash
archie aria ariana ariel arjun arlene armando arnav arnel arnold arnulfo aron arthur arturo arun arvind asad
asha ashley ashok ashton ashwin asif asma astrid aubrey audrey augusto aurelie aurelio ava avery aviva avraham
axel aya ayana ayesha ayman ayodele ayse ayumi aziz azucena babajide babatunde bahram bailey balaji baljit bao
barbara barry bartholomew bartosz bashir beata beatrice beatriz becky bekele belinda bella ben benedetta
benedict benita benito benjamin bennett benoit bernadette bernard bernardo bernd bernice bert bertha beryl
bessie beth bethany betsy betty betzaida beulah beverly bhavna bianca bilal billie billy binh bintou birgit
birgitta bjorn blake blanca bobbie bobby bogdan bolaji bonnie boris boubacar bozena bradley brady brandi brandon
brayden brenda brendan brent brett brian briana brianna bridget bridie brielle brigitte britney britt brittany
brody brooke bruce bruno bryan bryant bryce bryson burak byron caden caleb callie calvin cameron camila camille
camilo candace candelaria caoimhe cara carina carl carla carlo carlos carlton carly carmela carmelo carmen carol
carole caroline carolyn carrie carson casey cassandra cassidy catalina catarina cathal catherine cathy cecil
cecilia cedric celeste celestino celia celine cem cesar chaim chana chandan chandra chang charlene charles
charlie charlotte cheikh chelsea cheryl chester chiamaka chiara chidi chidinma chinedu chinonso chinwe chioma
chiyo chizoba chloe chris christa christian christina christine christophe christopher christy chukwuemeka chun
chuy ciara ciaran cindy ciro claire clara clarence clarissa claude claudette claudia claudine claudio clayton
clement clifford clifton clint clinton clyde colby cole colette colin colleen collin colm colton concepcion
connie connor conor conrad consuelo cora cordelia corey corinne cormac cornelius cory cosimo coumba courtney
craig cristian cristina cristobal cuong curtis cynthia cyrus dagmar dagmawi daiki daisuke daithi dalal dale
dalia damian damien damon dana daniel daniela danielle danilo danny dante daphne dario darius dariush dariusz
darla darlene darnell darrell darren darryl darshan daryl dashawn dave david davide davis dawit dean deandre
debbie deborah debra declan dee deepa deepak deepika deirdre deja delaney delbert delfina delia delilah della
delores delphine demarcus demetrio demetrius dena denis denise deniz dennis denzel derek derrick deshawn desmond
detlef devin devon devonte devorah dewey dexter diana diane dianne didier diego dieter digna dimitri dina dinesh
dionisio dionne dirk divya dmitri dmitry dohyun dolly domenico dominic dominique don donal donald donna donnie
dora doreen doris dorota dorothy doug douglas dragan duane duc dustin dwayne dwight dylan eamon earl easton
ebere ebony eddie edgar edgardo edith edmund edna eduardo edward edwin effie efrain efua egon eileen eimear
einar eitan ekene eladio elaine elba elbert eleanor elena eli eliana elias elif elijah elio elisa elisabeth
elise eliseo eliza elizabeth elke ella ellen ellie elliot elliott ellis elmer elodia elodie eloise elsa elsie
elvira elvis elzbieta emanuel emanuele emeka emery emeterio emi emiko emil emile emilia emiliano emilio emily
emine emma emmanuel emmett emre eneida enrique enzo eoin epifanio erasmo eric erica erick erik erika erin ernest
ernestine ernesto errol esi eskil esmeralda esperanza esra essie esteban estela estella estelle esther ethan
ethel etta ettore eugene eugenia eula eunice eunji eunjung eusebio eva evan evangeline evaristo evelyn everett
everleigh everly evgeny eyerusalem ezekiel ezra fabian fabien fabio fabrizio faisal fannie farah fares farhad
farid farouk fatih fatima fatma fatoumata fausto fawzi faye federico fei felicia feliciano felipe felix femi
feng fergal fernanda fernando fidel fikru filippo filomena finbar fiona florencio florian florinda floyd folake
folasade franca frances francesca francesco francine francis francisco franco francois franklin fred freda
freddie frederick frida frieda friedrich fumiko funmilayo gabriel gabriela gabriella gabrielle gaetano gail
galina ganesan ganesh gareth garrett gary gaspar gaston gaurav gavin geeta gemma genaro genet genevieve gennady
geoffrey george georgina gerald geraldine gerard gerardo gertrude ghada giacomo gianluca gianna gilbert gilberto
gilda gillian gina gino giorgio giovanni girma gisela giselle giulia giulio giuseppe gladys glen glenda glenn
gloria golnaz gopal gopinath goran gordon graciela grady graham grainne grayson graziella grazyna greg gregg
gregorio gregory greta gretchen greyson grzegorz guadalupe guang guillaume guillermo guiying gul gunnar gunther
guo gurpreet gustav gustavo gwen gwendolyn habib hadi hai hailey haitham haiyan hakan hakim haley halina hamid
hamza hana hanan haneen hanh hani hank hannah hannelore hans hao haoran harish harjit harold haroun harper
harpreet harriet harrison harry haruka haruki haruto harvey hasan hassan hatem hatice hattie hayden hector heidi
heike heinz helen helena helene helga helmut hemant henrietta henry herbert heriberto herman herve hesham hideki
hien hieu higinio hikaru hilario hilda hilde hina hiroki hiroko hiromi hiroshi hisham hitomi hiwot hoa hoang
hollie homer hong horace horst hortensia howard hua hubert huda hudson hugh hugo hui humberto huong husain
huseyin hussein huy hyejin hyunjoo hyunwoo ian ibrahim ibrahima ida ifeoma ignacio igor ikenna ilana ilaria ilse
imad imani imelda imogene imran indira ines inez ingeborg ingrid inna inocencio irene irina irma irvin irving
isaac isabel isabella isabelle isaiah isha isidro isla ismael ismail issa ivan ivana ivette ivo iwona jace jacek
jacinta jacinto jacob jacqueline jacques jada jaden jadwiga jagdish jaime jake jamal james jameson jamie jamil
jana jane janelle janet janice janie janina janine jaquan jared jaroslaw jarrod jasbir jasmine jason jaswinder
javier jawad jaxon jaxson jay jaya jayakumar jayden jean jeanette jeanne jeannie jeff jeffery jeffrey jelena
jenna jennie jennifer jenny jens jeremiah jeremy jermaine jerome jerry jerzy jesse jessica jessie jesus jesusa
jia jian jiang jianguo jianhua jie jiho jihoon jill jillian jim jimmie jimmy jin jing jinwoo jisoo jiwoo jiyeon
jiyoung joan joann joanna joanne joaquin jocelyn jodi jody joe joel joey johanna johannes john johnathan johnnie
johnny jolanta jon jonah jonathan jordyn jorge jorgen jose josefina joseph josephine josh joshua josiah josiane
josue joyce juan juana juanita judith judy julia julian juliana julie julien julio julius junjie junko junseo
jurgen justin justine juvencio jyoti kadiatou kai kaitlyn kaito kamal kamala kamau kamil kana kaori kara karam
karan kareem karen kari karim karin karina karl karla karthik kate katelyn katherine kathleen kathryn kathy
katie katrina katsumi kavita kavya kay kayden kayla kaylee kayode kazuki kazuo keiko keisha keita keith kelechi
kelley kelli kellie kelly kelsey kemal ken kendall kendra kenichi kenji kennedy kenneth kenny kenta kerry
kerstin keshawn kevin khadija khaled khalid khalil khanh khloe khoa kiara kidist kieran kim kimberly kinsley
kipchoge kiprop kirill kirk kirsten kishore kiyoshi kjell klaus kofi kojo kourosh kris krishna krishnan krista
kristen kristi kristin kristina kristine kristopher krystyna krzysztof kuldeep kumar kumiko kurt kwabena kwame
kwesi kyle kylie lacey ladan laetitia lakisha lakshmi lalita lamar lamine landon lanette lara larisa larry lars
latasha latifa latisha latoya laura laureen lauren laurence laurent laurie lavern laverne lawrence layla lea
leah leandro leann leanne lech lee lei leif leila leilani leland lena leo leon leona leonard leonardo leonel
leonid leonor leopoldo lerato leroy leslie lester leszek leticia levi lewis leyla liam liang librada lidia lila
lili lillian lillie lin lina linda lindiwe lindsay lindsey ling linh linnea lionel lisa liu lizbeth lloyd logan
lois lola lonnie lora loraine lorena lorenzo loretta lori lorna lorraine lothar louis louisa louise lourdes
lubna luca lucas lucia luciano lucien lucille lucinda lucio lucy lucyna luigi luis luisa luke lula luna lupe
luther lydia lynda lynette lynn lyudmila mabel macario mackenzie madeline madelyn madhu mae maeve magdalena
maggie magnus mahendra mahesh mahmoud mahmud mai mairead majid makayla makoto malak malcolm malgorzata malik
mamadou mami mana mandla mandy manfred manish manoj manon manpreet mansour manuel manuela marc marcel marcela
marcelino marcella marcello marcelo marcia marco marcos marcus marek margaret margarita margarito margaux margie
maria mariah mariam mariama marian mariana marianne maribel maricel marie marija mariko marilou marilyn marina
mario marion marisa marisol marissa marites mariusz marjorie marla marlene marlon marquis marsha marshall marta
martha martin martina marty marvin marwa mary maryam maryann masahiro masako masao masato massimo mateusz
mathieu matilda matt matteo matthew mattie maureen maurice mauricio maurizio mavis maxime maximino maxine maya
maysa mayumi meena meera megan meghan megumi mehdi mehmet mei meiling meir melanie melba melinda melissa melva
melvin mercedes meredith meron mesfin mia micah michael michaela michele michelle michiko miguel mikayla mike
mikhail mila milagros milan mildred milica milton mindy ming minh minji minjun minnie minoru minseo miranda
mireille mirella miriam miroslaw misaki mitchell miyuki modesto mohamed mohammad mohammed mohan mohsen moises
molly mona monica monika monique morgan morris moses moshe mounir moussa muhammad mukesh munir murali murat
muriel mustafa muthu myra myron myungsook nabil nadezhda nadia nadim nadine nagarajan naji najib nam nancy naoki
naoko naomi naresh nasrin nasser natalia natalie natasha nathalie nathan nathaniel navdeep nawal neelam neha
neil nell nellie nelson nemesio nenad nestor nevaeh neville ngoc ngozi nguyet nhung nia niall niamh nicanor
nicholas nichole nicola nicolas nicole nikhil nikita nikki nikola nikolai niloufar nils nina ning nirmala nisha
nizar njeri nkechi nnamdi noah noam nobuko noel noelle noemi noemie nolan nomvula noor nora norberto noriko
norma norman nour oanh obdulia obiageli obinna octavio odessa odile odilia ofelia oguz oisin oksana olaf oleg
olga oliver olivia ollie olumide oluwaseun oluwatobi omar omari omer orazio oren osama osamu oscar oswaldo
otieno otilia otis oumar ousmane owen ozlem pablo padma padraig paige paisley pamela pankaj paola paramjit
parisa parvati pascuala pasquale patricia patricio patrick patsy paul paula paulette pauline paulino pavel pedro
peggy penelope peng percy perry pete peter petra petronila peyton philip philippe phillip phoebe phong phuc
phuong phyllis piero pierre pieter piotr piper pooja porfirio prabhu pradeep prakash pramod pranav prasad prem
preston priscilla priya prudencio pushpa qasim qian qiang qing quan quang quentin quincy quinn quoc rachael
rachel radha radhika rafael raffaele raghav raghavan ragnar rahul rainer raj rajan rajendra rajesh rajinder
rajiv rakesh ralph ramaswamy ramesh rami ramiro ramon ramona ramya randall randy rani rania raquel rasha rashad
rashid raul ravi raymond raymonde reagan reba rebecca rebekah reem refugio reginald regis reid reiko reinhard
rekha remy ren renata renate renato renee rex reyna reynaldo reza rhonda riad ricardo richard rick ricky ridwan
rigoberto riku riley rima rina rinku rita ritu rivka robbie robert roberta roberto robin rocco rochelle rocio
rodel roderick rodney rodolfo rodrigo rogelio roger rohan rohit roisin roland rolando rolf romeo ron ronald
ronan rong ronnie rory rosa rosalie rosalind rosalinda rosalyn rosaria rosario rosaura roscoe rosemarie rowena
roxanne roy roya ruben rudolph rudy rufino rufus rui ruslan russell ruth ryan ryo ryota ryszard ryusei saad
sabah sabine sabino sabri sabrina sachiko sachin sadia sadie saeed safa sagrario sakiko saleh salim salma
salvador salvatore samantha sameer sami samia samir samira sammy samuel sanaa sandra sandrine sandro sangeeta
sanjay sanjeev santiago santos santosh saoirse sara sarah saravanan sarita sasha satomi satoshi saturnino saul
savita sawyer scarlett scott seamus sean sebastian sebastien seema segun selamawit selena selin selvam senthil
seojun seoyeon serafin serena serge sergei sergio serkan seth seungmin severino seydou shadi shan shana shane
shani shanice shaniqua shannon shanti shari sharif sharmila sharon shaun shauna shawn shawna sheila shelby
shelia shelley shelly sheng sheri sherman sherri sherry sheryl shigeru shilpa shinji shiori shira shirin shirley
shiva shlomo shobha shota shreya shu shyam sibusiso siddharth sidney siegfried sigrid silvana silverio silvia
sima simon simona simone simran sinead siobhan sipho sita sivakumar sixto skylar slawomir smita sneha snezana
sofia soheila solange solomon solveig sonal sonia sonja sooyoung sophia sophie sota souleymane soyeon spencer
stacey stacy stanislav stanislaw stanley stefan stefanie stefano stella sten stephan stephanie stephen steve
steven stig stuart suad subhash subramanian sudha suha sukhwinder sultan sumit sunanda sundar sungmin sunhee
sunil sunita supriya suresh susan susana susanne suzanne svante sven svetlana swati sydney sylvester sylvia
sylvie tabitha tadashi tadeo tadeusz takashi takeshi takumi talia tam tamar tamara tamer tami tamika tammy tania
tanisha tanvi tanya tao tara tarek tariq tasha tatiana tatsuya ted teddy temitope teodoro teresa teri terrance
terrell terrence terri terry tesfaye tetsuya thabo thaddeus thandeka thandiwe thanh thao thelma themba theodore
theresa thi thibault thierry thomas thuy tiburcio tien tiffany tigist tim timothy tina ting tiziana tobi tobias
todd tolga tom tomas tomasz tommie tommy tomoko toni tony tonya torbjorn torsten toshiro tracey traci tracy
trang travis trent trevon trevor tricia trinh trisha tristan troy trudy trung tuan tunde tuyet tyler tyrell
tyrone tyson uchenna udo ulf ulises ulrike uma umberto umesh ursula urszula usha uwe vadim valente valentin
valentina valeriano valerie valerio valery vanessa varun vasant vasily velma venkat venkatesh vernon veronica
vesna vicente vicki vickie victoria vidya vijay vijayakumar vikram viktor vinay vincent vinh vinod virgil vishal
vitaly vittoria vittorio vivian vladimir volker wael waldemar waleed walid walter walther wambui wanda wanjiru
warren wayne wei weiwei wen wendell wendy werner wesley whitney wieslaw wilbert wilbur wilfred wilfredo wilhelm
wilhelmina willard william willie wilma winifred winston wojciech wolfgang wyatt xavier xia xian xiang xiao
xiaohong xiaoli xiaoming xiaowei xiaoyan ximena xin xiu xiulan xiuying xuan xue yaa yaakov yadira yael yahya yan
yang yannick yanyan yaroslav yash yasir yasmin yasmine yasser yasuko yaw yesenia yetunde yichen ying yitzchak
yogesh yohannes yoko yolanda yolotzin yonatan yong yosef yoshiko yoshiro younes younghee youngho yousef youssef
yuan yuhan yuka yukari yuki yuko yulia yumi yun yuna yuri yusuf yusuke yuto yuxuan yuying yves yvette yvonne
zachary zahra zaid zainab zakaria zane zanele zara zbigniew zdzislaw zeinab zelda zeljko zenaida zewdu zeynep
zhanna zhen zheng zhi zhiqiang zhong ziad zihan zixuan zodwa zoe zoey zofia zoila zoran zuri
"""

# THE WORDS NEVER LISTED, though each is a given name somewhere: ordinary
# words, months and weekdays' abbreviations, units' and tests'
# abbreviations, colours, gems, flowers and herbs, virtues, seasons and weather,
# places, roles and words a clinical label holds. The gate file holds the
# list apart from them.
_STOPPED = """
ama amber angel angelica april art august aurora austin autumn baker bill brandy brooklyn buck candy carolina
carter cash chad chance charity chase china chip clay cleveland cliff constance cooper coral crystal dag daisy
dakota dallas dat dawn denver destiny dong drew dulce dung dusty eve faith fern fisher flora florence florida
frank gang gene genesis georgia grace grant guy harmony hazel heather holly hope houston hung hunter india iris
israel ivory ivy jackson jade jan jordan joy jun june junior kent king lan lance lane lily lincoln loan loc
london long madison major mala mark mason mats max maxim may melody mercy miles misty montana nick ole olive
opal orlando paris parker pascal pat patience pearl per perla phoenix ping porter precious primitivo prince
princess prudence queen rain raven ray regina reina remedios rich river rob rocky rod roman rose royal ruby rune
said sandy savannah sierra skip sky son spring star sterling storm sue summer sunny tan taylor thu tor trinidad
trinity turner urbano vera viola violet virginia wade walker will winter yen young
"""

GIVEN_NAMES: "frozenset[str]" = frozenset(_LISTED.split())
STOP: "frozenset[str]" = frozenset(_STOPPED.split())

# THE LETTERS A NAME IS FOLDED THROUGH (`fold`): each plain letter beside
# the small Latin letters with a mark read as it; then the letters read as
# two, and the blocks of combining marks set aside (a name stored
# decomposed, `Jose` and U+0301).
_MARKED_BY_PLAIN = (
    ("a", "àáâãäåāăą"), ("c", "çćĉċč"), ("d", "ďđð"), ("e", "èéêëēĕėęě"), ("g", "ĝğġģ"), ("h", "ĥħ"),
    ("i", "ìíîïĩīĭįı"), ("j", "ĵ"), ("k", "ķ"), ("l", "ĺļľŀł"), ("n", "ñńņň"), ("o", "òóôõöøōŏő"), ("r", "ŕŗř"),
    ("s", "śŝşš"), ("t", "ţťŧ"), ("u", "ùúûüũūŭůűų"), ("w", "ŵ"), ("y", "ýÿŷ"), ("z", "źżž"),
)
_FOLDED = {**{marked: plain for plain, letters in _MARKED_BY_PLAIN for marked in letters},
           "æ": "ae", "œ": "oe", "ß": "ss", "þ": "th"}
_COMBINING = ((0x0300, 0x036F), (0x1AB0, 0x1AFF), (0x1DC0, 0x1DFF), (0x20D0, 0x20FF), (0xFE20, 0xFE2F))


def fold(word: str) -> str:
    """A word as the list is read: in small letters, each marked Latin letter its plain letter (`José` -> `jose`, `Zoë` -> `zoe`, `Bjørn` -> `bjorn`), each combining mark set aside. Guarantees: a fixed function of the text. Raises TypeError for a word that is not text. No I/O."""
    if not isinstance(word, str):
        raise TypeError("a word must be text")
    out = ""
    for character in word.lower():
        code = ord(character)
        if any(low <= code <= high for low, high in _COMBINING):
            continue
        out = out + (_FOLDED[character] if character in _FOLDED else character)
    return out
