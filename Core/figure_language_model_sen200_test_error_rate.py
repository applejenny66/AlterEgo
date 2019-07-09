import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

errors = [0.9564444382985433, 0.9481111208597819, 0.948111093044281, 0.9559999863306682, 0.9345555106798807, 0.9610000133514405, 0.9301111102104187, 0.929111123085022, 0.9064444263776144, 0.9081111192703247, 0.8926666537920634, 0.8794444282849629, 0.8848888953526814, 0.8395555496215821, 0.7457778056462606, 0.6849999825159708, 0.6008889039357503, 0.4863333463668823, 0.4098888913790385, 0.3591111342112223, 0.3314444502194723, 0.2715555528799693, 0.24466667373975118, 0.23722222646077473, 0.21377778351306914, 0.21088889837265015, 0.1871111164490382, 0.18744444946448008, 0.1885555624961853, 0.1840000073115031, 0.18000000317891438, 0.16355556547641753, 0.18122223317623137, 0.17922222316265107, 0.17377777993679047, 0.17933334012826282, 0.16888888974984487, 0.16288889745871227, 0.17077778180440267, 0.18622222244739534, 0.19011111358801525, 0.15766666928927103, 0.16755555868148803, 0.1754444420337677, 0.17077778279781342, 0.16966667175292968, 0.15488889316717783, 0.1777777850627899, 0.1788888951142629, 0.1483333374063174]
error_top_ks_orig = [[0.9564444541931152, 0.948111097017924, 0.948111093044281, 0.9559999744097392, 0.9345555265744527, 0.9610000212987264, 0.9301111062367757, 0.929111123085022, 0.9064444422721862, 0.9081111073493957, 0.8926666696866353, 0.879444436232249, 0.8848889191945394, 0.839555545647939, 0.7457777897516886, 0.6849999864896138, 0.6008888959884644, 0.48633333841959636, 0.40988889336586, 0.3591111342112223, 0.3314444382985433, 0.2715555628140767, 0.24466667970021566, 0.23722223043441773, 0.2137777864933014, 0.21088890433311464, 0.18711111148198445, 0.1874444474776586, 0.18855556547641755, 0.18400000234444935, 0.18000000913937886, 0.16355555752913156, 0.1812222202618917, 0.1792222221692403, 0.17377778391043344, 0.1793333411216736, 0.1688888947168986, 0.16288889547189075, 0.17077778279781342, 0.18622222344080608, 0.19011111160119373, 0.157666677236557, 0.16755555768807728, 0.17544444998105366, 0.1707777758439382, 0.16966666678587597, 0.15488889465729397, 0.17777778605620068, 0.17888889710108438, 0.14833333591620126], [0.9203333497047425, 0.9110000054041545, 0.9093333522478739, 0.9277777870496114, 0.9081110954284668, 0.8974444429079692, 0.9004444320996602, 0.8902222434679667, 0.8696666518847148, 0.8606666485468547, 0.8634444594383239, 0.8260000308354696, 0.8408888816833496, 0.7933333198229472, 0.7185555577278138, 0.6435555775960287, 0.5388888974984487, 0.41911111275355023, 0.36255556146303813, 0.30644445021947225, 0.2672222316265106, 0.21844445367654164, 0.18488889435927072, 0.17877778112888337, 0.1622222274541855, 0.1648888885974884, 0.13011111617088317, 0.12622222552696863, 0.1400000055631002, 0.12300000190734864, 0.13100000321865082, 0.11833333720763524, 0.1163333351413409, 0.13177777528762818, 0.11711111093560854, 0.12933333615461987, 0.11933333575725555, 0.11711111813783645, 0.12722223301728566, 0.13211111426353456, 0.12211111684640248, 0.10355555911858877, 0.11855555772781372, 0.11444444954395294, 0.12444444845120112, 0.10722222725550333, 0.10455556015173594, 0.13011111319065094, 0.12633333305517833, 0.0986666684349378], [0.8764444430669148, 0.8666666706403097, 0.864888866742452, 0.8984444618225098, 0.8554444074630737, 0.8486666321754456, 0.8694444259007772, 0.8603333473205567, 0.8328888853391011, 0.8268888711929321, 0.8320000092188518, 0.7981111248334248, 0.8041111310323079, 0.7433333198229471, 0.6801111300786337, 0.6083333452542623, 0.5054444392522176, 0.386000003417333, 0.33500000834465027, 0.27611111203829447, 0.24400000870227814, 0.1844444493452708, 0.15311111509799957, 0.14511111478010813, 0.13166666626930237, 0.13111111422379812, 0.11611111362775167, 0.10800000230471293, 0.1112222249309222, 0.1084444468220075, 0.1046666736404101, 0.09611111283302307, 0.10100000078479449, 0.10100000550349554, 0.09866666917999585, 0.10222222755352656, 0.09322222173213959, 0.09855555842320124, 0.10444445063670477, 0.11322222501039506, 0.10611111124356588, 0.08155555874109269, 0.09966667145490646, 0.0948888932665189, 0.09433333377043406, 0.08544444839159647, 0.08477778087059656, 0.1025555541117986, 0.10822222928206125, 0.08211111625035604], [0.8463333209355672, 0.8433333436648051, 0.8352222084999085, 0.8683333118756612, 0.8324444611867269, 0.8202222386995951, 0.835111125310262, 0.8372222026189168, 0.811555544535319, 0.803666639328003, 0.7981111248334248, 0.7687777717908223, 0.7762222131093343, 0.7157777667045593, 0.6624444564183553, 0.5869999925295512, 0.47833332816759744, 0.3577777922153473, 0.31288889845212303, 0.24822222987810771, 0.2235555628935496, 0.16177778045336405, 0.13600000441074372, 0.1352222243944804, 0.11477778057257335, 0.1197777767976125, 0.11366667151451111, 0.09100000113248825, 0.1010000025232633, 0.09622222334146499, 0.09077777912219366, 0.08533333788315454, 0.08744444623589516, 0.08255555679400763, 0.08944444879889488, 0.09555555979410807, 0.08522222489118576, 0.0930000031987826, 0.090444449086984, 0.0960000013311704, 0.09366666972637176, 0.07122222284475963, 0.08844444751739503, 0.08066666846474012, 0.08366666634877523, 0.07833333611488343, 0.08122222522894541, 0.08933333307504654, 0.09800000389417013, 0.07411111195882161], [0.8349999785423279, 0.8187777837117513, 0.8157777667045594, 0.8396666487058003, 0.8177778085072835, 0.8096666614214579, 0.8232222278912862, 0.82199999888738, 0.7905555685361226, 0.7831111311912536, 0.7831111311912536, 0.7564444502194723, 0.7472222089767456, 0.6963333169619242, 0.6325555801391601, 0.5693333546320597, 0.46922223369280497, 0.3388888875643412, 0.2977777858575185, 0.2341111163298289, 0.21200000445048015, 0.14822222888469697, 0.12533333599567414, 0.12888888716697694, 0.09544444680213929, 0.1093333343664805, 0.10466666569312413, 0.0815555547674497, 0.08866666803757349, 0.08188889076312383, 0.08233333428700765, 0.08033333520094553, 0.07633333578705788, 0.06488888959089915, 0.07766666760047276, 0.08288889030615489, 0.07500000347693761, 0.08333333233992259, 0.08144444972276688, 0.085777780910333, 0.08366667081912359, 0.0678888887166977, 0.07577777604262034, 0.07177777737379074, 0.0803333322207133, 0.0722222238779068, 0.07377778043349584, 0.08466666837533315, 0.0856666699051857, 0.06911111151178678], [0.8266666293144226, 0.8007777611414592, 0.8030000170071919, 0.8274444222450257, 0.7925555785497029, 0.7999999801317851, 0.7995555758476257, 0.8111110925674438, 0.7671111226081848, 0.760111137231191, 0.7687777916590373, 0.7415555596351624, 0.7241110960642497, 0.6758888959884644, 0.6242222428321839, 0.5374444802602132, 0.45255556106567385, 0.31700001160303753, 0.2768888970216115, 0.22533334096272786, 0.20044445196787516, 0.1366666704416275, 0.11566667159398397, 0.12088888982931772, 0.09100000113248825, 0.09966666748126347, 0.09911111195882162, 0.07333333442608515, 0.07988889118035634, 0.07922222365935644, 0.07766666809717813, 0.07355555693308512, 0.07277777964870134, 0.06044444541136424, 0.07022222330172857, 0.07522222350041072, 0.06833333522081375, 0.0797777791817983, 0.07788889209429423, 0.07977778067191442, 0.08255555977423985, 0.06677777767181396, 0.07088888784249624, 0.06844444374243418, 0.06877778048316638, 0.06811111296216647, 0.06488888983925184, 0.08200000127156576, 0.08100000172853469, 0.06500000183780988], [0.8094443996747335, 0.783888864517212, 0.801888906955719, 0.7968888719876607, 0.7848888993263244, 0.795888872941335, 0.7865555961926778, 0.7933333118756613, 0.750777784983317, 0.7515555659929911, 0.7598888834317525, 0.7263333559036255, 0.7116666634877523, 0.667555562655131, 0.6031111200650533, 0.522777799765269, 0.43544443845748904, 0.31233334143956504, 0.27077777981758117, 0.2206666777531306, 0.19222222367922465, 0.12866667310396832, 0.10855556031068166, 0.10444444914658864, 0.08688889294862748, 0.09466666827599207, 0.09333333224058152, 0.0677777794500192, 0.07355555693308512, 0.07922222365935644, 0.07100000083446503, 0.0666666679084301, 0.0649999998509884, 0.05877777934074402, 0.0680000012119611, 0.07388889044523239, 0.06366667101780574, 0.0775555580854416, 0.0767777810494105, 0.07177778060237566, 0.07322222292423249, 0.06155555744965871, 0.06866666575272878, 0.06711110969384511, 0.06655555839339893, 0.06300000076492628, 0.06355555579066277, 0.07844444612661998, 0.07611111402511597, 0.05900000035762787], [0.803333310286204, 0.779444408416748, 0.7972222208976746, 0.7861111124356588, 0.7798888961474101, 0.7931110978126525, 0.7848889311154683, 0.7795555432637532, 0.7407777945200602, 0.7457777857780457, 0.7405555446942648, 0.720888900756836, 0.7064444621404012, 0.6554444591204326, 0.593666668732961, 0.5111111243565877, 0.4255555470784505, 0.2991111218929291, 0.26077778538068136, 0.21622223357359568, 0.18200000127156576, 0.12377778142690658, 0.10144444902737935, 0.0994444489479065, 0.07977778166532516, 0.08866666704416275, 0.09066666513681412, 0.06533333460489908, 0.07355555693308512, 0.07255555639664332, 0.06655555715163548, 0.06555555736025175, 0.06144444470604261, 0.05766666829586029, 0.06466666708389918, 0.07055555681387583, 0.06233333696921666, 0.06844444721937179, 0.07211111336946488, 0.06933333451549212, 0.07211111138264338, 0.0591111126045386, 0.06511111184954643, 0.06111111206312974, 0.06544444635510445, 0.060777778675158815, 0.05911111161112785, 0.07600000301996866, 0.07277777989705404, 0.05900000035762787], [0.7922222177187602, 0.7772221883138021, 0.7945555369059245, 0.7861111124356588, 0.7776666680971781, 0.7817777713139852, 0.7765555898348491, 0.7723333279291789, 0.7322222391764323, 0.7377777854601543, 0.7314444422721863, 0.715666675567627, 0.7053333441416423, 0.6516666849454243, 0.5878888765970866, 0.5022222518920898, 0.4142222166061401, 0.29577778776486713, 0.24611112078030903, 0.20633334318796795, 0.17422222594420114, 0.11666666964689891, 0.09700000286102295, 0.09477778325478235, 0.07866667111714681, 0.08622222195068995, 0.08955555508534113, 0.06177777945995331, 0.06666666741172472, 0.06977777903278669, 0.0626666655143102, 0.06277777925133705, 0.05866666759053866, 0.05522222419579824, 0.058555555157363416, 0.06699999968210855, 0.0582222248117129, 0.06733333617448807, 0.06577777912219365, 0.06766666745146116, 0.0680000012119611, 0.05577777946988741, 0.060222222656011584, 0.05866666672130426, 0.06433333531022072, 0.05500000094374021, 0.0566666675110658, 0.0686666692296664, 0.07033333232005437, 0.05522222320238749], [0.7875555555025736, 0.7656666358311971, 0.7878888765970866, 0.7847777803738912, 0.7732222278912863, 0.7806666612625122, 0.7754444718360901, 0.77011110385259, 0.7242222388585409, 0.7344444553057353, 0.7258888761202494, 0.713444463411967, 0.6986666758855183, 0.6444444616635641, 0.5773333271344503, 0.4942222515741984, 0.4032222112019857, 0.28777778148651123, 0.23555556337038677, 0.19222223063309987, 0.16711111565430958, 0.11288889348506928, 0.09233333418766658, 0.09011111309130987, 0.07511111497879028, 0.08622222195068995, 0.0826666663090388, 0.05844444582859675, 0.06666666741172472, 0.06755555619796118, 0.06022222240765889, 0.05944444512327512, 0.05755555654565493, 0.05300000185767809, 0.05744444411247969, 0.06255555674433708, 0.057111113270123796, 0.06511111482977867, 0.06577777912219365, 0.06522222434480986, 0.06355555579066277, 0.05466666842500369, 0.056888889024655026, 0.05588888960580031, 0.058000001062949495, 0.05222222333153089, 0.05555555547277133, 0.06644444664319356, 0.06811110998193423, 0.05522222320238749]]
error_top_ks = [[0.9564444541931152, 0.9458888689676921, 0.9486666480700175, 0.9559999744097392, 0.9345555265744527, 0.9610000212987264, 0.9323333342870076, 0.929111123085022, 0.9103333353996277, 0.9081111073493957, 0.8904444336891174, 0.8749999721844991, 0.886222223440806, 0.840666667620341, 0.7427777806917827, 0.6644444386164348, 0.6048889080683391, 0.47322221994400027, 0.36444443662961323, 0.34344444473584496, 0.30833333134651186, 0.22133333881696066, 0.20444445212682089, 0.1853333314259847, 0.16255555947621664, 0.13955556253592175, 0.12133333583672841, 0.14311111470063528, 0.15222222755352657, 0.12188889135917028, 0.13388889133930207, 0.13422222634156544, 0.12588889052470525, 0.1253333369890849, 0.12877778063217798, 0.13977778255939483, 0.14011111160119374, 0.13555555840333303, 0.13266667524973552, 0.1373333384593328, 0.13433333337306977, 0.10744444827238718, 0.13833333551883698, 0.12811111211776732, 0.14311111370722454, 0.1232222264011701, 0.11988888879617056, 0.14544444183508556, 0.135444442431132, 0.11788889120022455], [0.9203333497047425, 0.9098888953526815, 0.9076666633288065, 0.9277777870496114, 0.9081110954284668, 0.8974444429079692, 0.8952222148577372, 0.8874444762865702, 0.8716666420300802, 0.8606666485468547, 0.8610000093777974, 0.8267778237660726, 0.8253333290417989, 0.7892222126324971, 0.7038888891537984, 0.6314444541931152, 0.5487777849038442, 0.3963333328564962, 0.3130000074704488, 0.292333330710729, 0.2553333361943563, 0.17422222594420114, 0.14266666869322459, 0.1310000052054723, 0.11588888863722484, 0.10611111521720887, 0.10233333557844163, 0.0896666685740153, 0.09855555693308513, 0.09000000208616257, 0.09333333522081375, 0.09055555711189905, 0.08177777826786041, 0.08366666932900747, 0.09177778015534083, 0.08677777846654257, 0.09177777767181397, 0.09544444878896077, 0.09966667145490646, 0.09133333563804627, 0.09133333663145701, 0.07333333417773247, 0.09033333559830983, 0.08488888839880625, 0.09022222210963567, 0.07933333466450374, 0.07922222291429838, 0.09288888921340306, 0.09711111187934876, 0.08288889030615489], [0.8764444430669148, 0.8644444425900777, 0.862666646639506, 0.8951111237208048, 0.8554444074630737, 0.8475555141766866, 0.8661111036936442, 0.8573333501815796, 0.8352221846580505, 0.8246666431427002, 0.8294444481531779, 0.7953333377838134, 0.7926666458447774, 0.7456666549046834, 0.6692222396532694, 0.5908889134724935, 0.5085555613040924, 0.36355557640393577, 0.2882222255071004, 0.25244444807370503, 0.22611111601193745, 0.14688889284928638, 0.12488889594872793, 0.12033333778381347, 0.09655555387338002, 0.0903333360950152, 0.09766666839520137, 0.0695555570224921, 0.08611111342906952, 0.08066666747132938, 0.07755555510520935, 0.07866666962703069, 0.06855555698275566, 0.06288889075318972, 0.08188889076312383, 0.07544444898764292, 0.07688889056444168, 0.08777777949968973, 0.08000000268220901, 0.07922222490111987, 0.07588888853788375, 0.06011111115415891, 0.07900000164906183, 0.07000000029802322, 0.06977777779102326, 0.0666666679084301, 0.06655555715163548, 0.07888888915379842, 0.08322222332159677, 0.06633333464463552], [0.8463333209355672, 0.8400000135103861, 0.8329999883969624, 0.8683333118756612, 0.8288888931274414, 0.8146666566530864, 0.8337777853012085, 0.8325555562973023, 0.8045555591583252, 0.799222195148468, 0.7972222407658894, 0.7704444607098897, 0.7716666380564372, 0.7138888875643412, 0.6528889020284017, 0.5638888994852702, 0.4812222500642141, 0.3355555613835653, 0.26855555971463524, 0.22755556106567382, 0.1970000018676122, 0.1273333375652631, 0.1141111175219218, 0.10622223019599915, 0.08500000337759654, 0.08922222505013148, 0.08888888756434123, 0.06222222397724787, 0.07877777914206187, 0.07599999954303106, 0.07177777836720149, 0.0672222244242827, 0.06522222186128299, 0.058000001062949495, 0.07622222155332566, 0.07166666785875957, 0.06944444626569748, 0.08144444525241852, 0.07211111237605412, 0.07200000261267027, 0.06733333443601926, 0.06011111115415891, 0.06533333510160447, 0.06244444536666075, 0.0632222222785155, 0.06011111065745354, 0.06377777904272079, 0.07311111142237982, 0.07766667008399963, 0.05900000010927518], [0.831666640440623, 0.8121110995610555, 0.8146666566530864, 0.8396666487058003, 0.8177778085072835, 0.8027777711550395, 0.8188888827959696, 0.8158888777097066, 0.7834444602330526, 0.7795555671056111, 0.7800000150998433, 0.7512222250302633, 0.7335555672645568, 0.6938888907432557, 0.628000009059906, 0.5454444805781047, 0.4512222429116567, 0.31955556869506835, 0.25555556019147235, 0.2114444504181544, 0.1843333383401235, 0.12044444928566615, 0.10355556011199951, 0.10044444998105367, 0.07900000313917796, 0.08755555798610051, 0.08399999936421712, 0.06222222397724787, 0.07466666996479035, 0.07299999942382177, 0.0667777786652247, 0.06333333427707354, 0.06166666770974795, 0.05633333449562391, 0.062444445801277955, 0.06922222326199214, 0.06255555848280589, 0.07311111316084862, 0.06933333426713943, 0.07066666856408119, 0.06733333443601926, 0.057666666557391486, 0.061777778714895246, 0.06000000076989333, 0.05933333461483319, 0.053555556138356525, 0.05777777756253878, 0.07044444680213928, 0.07033333232005437, 0.057888889064391456], [0.8233333150545756, 0.7963333209355672, 0.8030000170071919, 0.8218888640403748, 0.7878889083862305, 0.7961110949516297, 0.7978889107704162, 0.806333311398824, 0.756333327293396, 0.7584444721539815, 0.7598888913790385, 0.7368888696034749, 0.713777772585551, 0.6742222428321838, 0.6100000103314718, 0.5238889137903849, 0.42933335502942405, 0.31211111942927044, 0.2544444501399994, 0.20544445216655732, 0.17611111104488372, 0.11422222703695298, 0.09833333442608515, 0.0966666688521703, 0.07900000313917796, 0.08622222195068995, 0.0826666663090388, 0.05977777888377508, 0.07133333683013916, 0.07055555532375972, 0.06433333456516266, 0.06333333427707354, 0.06033333366115888, 0.05300000185767809, 0.059666666698952514, 0.06811111321051916, 0.06255555848280589, 0.06977778002619743, 0.06688889016707739, 0.0682222234706084, 0.06622222339113554, 0.05600000048677126, 0.06066666767001152, 0.06000000076989333, 0.05933333461483319, 0.053555556138356525, 0.05777777756253878, 0.06644444664319356, 0.07033333232005437, 0.056555556257565816], [0.8094443996747335, 0.783888864517212, 0.8005555828412374, 0.7968888719876607, 0.783222234249115, 0.7961110949516297, 0.7865555961926778, 0.7891110936800639, 0.7383333444595337, 0.7474444508552551, 0.7485555609067281, 0.7247777779897054, 0.7066666682561239, 0.6658889055252075, 0.593666688601176, 0.516111143430074, 0.42555556297302244, 0.30100001096725465, 0.25055556098620096, 0.2007777859767278, 0.17122222085793812, 0.11288889348506928, 0.09477777928113937, 0.09533333480358124, 0.07788889358441035, 0.08622222195068995, 0.0826666663090388, 0.05844444582859675, 0.06833333472410838, 0.07055555532375972, 0.0630000020066897, 0.06333333427707354, 0.05755555654565493, 0.05300000185767809, 0.05855555565406879, 0.065888890872399, 0.05977778037389119, 0.06511111482977867, 0.06577777912219365, 0.06688889140884081, 0.06488888934254647, 0.05600000048677126, 0.06066666767001152, 0.06000000076989333, 0.058000001062949495, 0.05222222333153089, 0.05555555547277133, 0.06644444664319356, 0.06922222127517065, 0.056555556257565816], [0.802222216129303, 0.7758888641993205, 0.7950000087420146, 0.7847777803738912, 0.7798888961474101, 0.7944444298744202, 0.7848889311154683, 0.7819999814033508, 0.7327777942021688, 0.7411111235618592, 0.7358888824780782, 0.7178888956705729, 0.7020000060399373, 0.652999997138977, 0.5867777903874715, 0.5072222550710043, 0.4195555607477824, 0.2952222327391307, 0.24611112078030903, 0.1972222298383713, 0.16988888879617056, 0.11288889348506928, 0.09477777928113937, 0.09400000125169754, 0.07788889358441035, 0.08622222195068995, 0.0826666663090388, 0.05844444582859675, 0.06833333472410838, 0.06755555619796118, 0.0630000020066897, 0.06111111218730609, 0.05755555654565493, 0.05300000185767809, 0.05744444411247969, 0.06255555674433708, 0.058444446822007494, 0.06511111482977867, 0.06577777912219365, 0.06522222434480986, 0.06488888934254647, 0.05466666842500369, 0.05933333411812782, 0.05755555567642053, 0.058000001062949495, 0.05222222333153089, 0.05555555547277133, 0.06644444664319356, 0.06811110998193423, 0.056555556257565816], [0.7911111076672872, 0.7758888641993205, 0.7923333247502645, 0.7847777803738912, 0.7776666680971781, 0.7831111033757527, 0.7765555898348491, 0.7739999969800313, 0.7272222439448038, 0.7344444553057353, 0.7281111200650533, 0.715666667620341, 0.7003333409627278, 0.6494444489479065, 0.5806666652361552, 0.49811113675435387, 0.4123333334922791, 0.2907777806123098, 0.23666667342185974, 0.1955555627743403, 0.1682222237189611, 0.11288889348506928, 0.09233333418766658, 0.09011111309130987, 0.07511111497879028, 0.08622222195068995, 0.0826666663090388, 0.05844444582859675, 0.06666666741172472, 0.06755555619796118, 0.06133333494265874, 0.05944444512327512, 0.05755555654565493, 0.05300000185767809, 0.05744444411247969, 0.06255555674433708, 0.058444446822007494, 0.06511111482977867, 0.06577777912219365, 0.06522222434480986, 0.06355555579066277, 0.05466666842500369, 0.056888889024655026, 0.05588888960580031, 0.058000001062949495, 0.05222222333153089, 0.05555555547277133, 0.06644444664319356, 0.06811110998193423, 0.056555556257565816], [0.7875555555025736, 0.7656666358311971, 0.7878888765970866, 0.7847777803738912, 0.7732222278912863, 0.7806666612625122, 0.7754444718360901, 0.77011110385259, 0.7242222388585409, 0.7344444553057353, 0.7258888761202494, 0.713444463411967, 0.6986666758855183, 0.6444444616635641, 0.5773333271344503, 0.4942222515741984, 0.4032222112019857, 0.28777778148651123, 0.23555556337038677, 0.19222223063309987, 0.16711111565430958, 0.11288889348506928, 0.09233333418766658, 0.09011111309130987, 0.07511111497879028, 0.08622222195068995, 0.0826666663090388, 0.05844444582859675, 0.06666666741172472, 0.06755555619796118, 0.06022222240765889, 0.05944444512327512, 0.05755555654565493, 0.05300000185767809, 0.05744444411247969, 0.06255555674433708, 0.057111113270123796, 0.06511111482977867, 0.06577777912219365, 0.06522222434480986, 0.06355555579066277, 0.05466666842500369, 0.056888889024655026, 0.05588888960580031, 0.058000001062949495, 0.05222222333153089, 0.05555555547277133, 0.06644444664319356, 0.06811110998193423, 0.05522222320238749]]

print min(errors)

plt.figure(figsize=(9, 4))
plt.subplots_adjust(left=0.06, right=0.98, bottom=0.11, top=0.92)
plt.title('Language Model Error Rate Reduction')
plt.plot(np.arange(len(errors))+1, errors[:], color='#2678b2', label='Without language model')
plt.plot(np.arange(len(errors))+1, error_top_ks[0][:], '--', color='#329f34', label='With language model')
plt.xlabel('Epoch')
plt.ylabel('Error Rate')
plt.legend()

plt.savefig('figure_language_model_sen200_error_rate.png')

plt.show()