# enable heartstone game log

> ref: https://bbs.nga.cn/read.php?tid=11838545&rand=607

- windows
   - `C:\Users\<user>\AppData\Local\Blizzard\Hearthstone`
   - `%LOCALAPPDATA%/Blizzard/Hearthstone`
- macos
   - `~/Library/Preferences/Blizzard/Hearthstone`

```
# log.config
[Achievements]
LogLevel=1
FilePrinting=true
ConsolePrinting=true
ScreenPrinting=false

[Power]
LogLevel=1
FilePrinting=true
ConsolePrinting=true
ScreenPrinting=false
```

```
# POWER.log
- EntityID
   - Game: 1
   - FirstPlayer: 2
   - SecondPlayer: 3
   - FirstPlayerSuite: 4-33
   - SecondPlayerSuite: 34-63
   - FirstPlayerHero: 64
   - FirstPlayerHeroSkill: 65
   - SecondPlayerHero: 66
   - SecondPlayerHeroSkill: 67
   - FirstPlayerDrawFirstCard: 68


enumID  name  中文名称  type  value  内容  注释
2  TAG_SCRIPT_DATA_NUM_1  脚本数据编号  int  N    平行类别多个衍生物的内部编码，该标签仅在卡扎库斯的各种药水衍生物中使用过
32  TRIGGER_VISUAL  扳机视觉效果  int  1    
45  HEALTH  生命值  int  N    
47  ATK  攻击力  int  N    
48  COST  费用  int  N    
114  ELITE  精英  int  1    橙卡卡面
183  CARD_SET  卡集  int  2  基础  
        3  经典  
        4  荣誉室  
        5  任务  
        8  测试  
        12  NAXX  
        13  GVG  
        14  BRM  
        15  TGT  
        16  Credits  
        17  英雄皮肤  
        18  乱斗  
        20  LOE  
        21  WOG  
        23  KARA  
        25  MSG  
        27  JUG  
184  CARDTEXT_INHAND  卡牌描述(手牌中)  locString      
185  CARDNAME  卡牌名称  locString      
187  DURABILITY  耐久度  int  N    
189  WINDFURY  风怒  int  1    
190  TAUNT  嘲讽  int  1    
191  STEALTH  潜行  int  1    
192  SPELLPOWER  法术伤害  int  1    
194  DIVINE_SHIELD  圣盾  int  1    
197  CHARGE  冲锋  int  1    
199  CLASS  职业    1  未知  仅有一张英雄技能卡牌群居雏龙(TB_BRMA10_3H)用到了该职业编码。
        2  德鲁伊  
        3  猎人  
        4  法师  
        5  圣骑士  
        6  牧师  
        7  潜行者  
        8  萨满  
        9  术士  
        10  战士  
        11  梦境牌  包含伊瑟拉的五张梦境牌和一张未知的乱斗模式状态牌再来一张(TB_MP_02e)。
        12  中立  
200  CARDRACE  种族  int  8  兽人  仅包含一张未实装乱斗卡牌纳迪娅，曼科里克之妻(TB_MnkWf01)。
        14  鱼人  
        15  恶魔  
        17  机械  
        18  元素  
        20  野兽  
        21  图腾  
        23  海盗  
        24  龙  
201  FACTION  阵营  int  1  部落  
        2  联盟  
        3  无  
202  CARDTYPE  类型  int  3  英雄/首领  
        4  随从  多个衍生物区分时，随从牌的CardID后多有一个后缀m，即minion
        5  法术  多个衍生物区分时，法术牌的CardID后多有一个后缀s，即spell
        6  状态  状态牌的CardID后多有一个后缀e，即enchantment
        7  武器  
        10  英雄技能  英雄技能牌的CardID后多有一个后缀hp，即hero power
203  RARITY  稀有度  int  1  普通  白
        2  基础  无
        3  稀有  蓝
        4  史诗  紫
        5  传说  橙
205  SUMMONED  归降的  int  1    仅包含一张状态牌，即来自被精神控制改变控制权的随从身上的状态：精神控制EX1_tk31
208  FREEZE  冰冻  int  1    
212  ENRAGED  激励  int  1    
215  OVERLOAD  过载  int  1    
217  DEATHRATTLE  亡语  int  1    
218  BATTLECRY  战吼  int  1    
219  SECRET  奥秘  int  1    
220  COMBO  连击  int  1    
227  CANT_ATTACK  无法攻击  int  1    
240  IMMUNE  免疫  int  1    
251  AttackVisualType  攻击特效类型  int  1    效果未知
        2    效果未知
        3    效果未知
        4    效果未知
        5    效果未知
        6    效果未知
        7    效果未知
        8    效果未知
        9    效果未知
268  DevState  摧毁阶段    2    摧毁相关
293  MORPH  变形状态  int  1    该标签指示变形相关的状态牌。目前包含三个变形相关的状态。
296  OVERLOAD_OWED  过载值  int  N    当前回合过载水晶数
311  CANT_BE_TARGETED_BY_SPELLS  无法成为法术的目标  int  1    无法成为指向型法术的目标
321  COLLECTIBLE  可收集的  int  1    
325  TARGETING_ARROW_TEXT  指向型随从技能文本  LocString      
330  ENCHANTMENT_BIRTH_VISUAL  状态视觉特效/产生时  int  1    普通贴片类
        2    有特殊动画和红色数值的减益
        3    交换攻击力与生命值、改变身材，白色数值
331  ENCHANTMENT_IDLE_VISUAL  状态视觉特效/持续时  int  1    普通贴片类
        2    有特殊动画和红色数值的减益
        3    交换攻击力与生命值、改变身材，白色数值
332  CANT_BE_TARGETED_BY_HERO_POWERS  无法成为英雄技能的目标  int  1    
335  InvisibleDeathrattle  隐藏亡语  int  1    大多来自首领牌。当首领转换阶段时，前一个形态被移除触发亡语替换为新的形态。
338  TAG_ONE_TURN_EFFECT  单回合效果  int  1    单回合效果大都为状态牌。其CardID后多有一个后缀o，即one turn effect。
339  SILENCE  沉默  int  1    
342  ARTISTNAME  插画师  string      
349  ImmuneToSpellpower  免疫法术伤害  int  1    即不受法术伤害加成的伤害性法术(包括不加成单体伤害的奥术飞弹和复仇之怒等)。
350  ADJACENT_BUFF  相邻增益  int  1    共包含恐狼前锋、火舌图腾在内的4张增加相邻随从攻击力的随从牌。
351  FLAVORTEXT  趣味文本/背景描述  LocString      
362  AURA  光环  int  1    
363  POISONOUS  剧毒  int  1    
364  HOW_TO_EARN  如何获得  LocString      
365  HOW_TO_EARN_GOLDEN  如何获得金色版本  LocString      
367  AI_MUST_PLAY  AI必须使用  int  1    大多为冒险模式和乱斗模式中首领的英雄技能或状态牌。在符合条件时会自动使用。
370  AFFECTED_BY_SPELL_POWER  受法术伤害影响  int  1    包括部分受法术伤害加成的法术和英雄技能。
377  TOPDECK  牌库顶  int  1    指抽到时触发特效的卡牌(即从牌库顶离开时触发)，包括烈焰巨兽、地雷等
380  HERO_POWER  英雄技能  int  1    
388  SPARE_PART  零件牌  int  1    包含GVG中的7张零件牌和3个相关状态。
389  FORGETFUL  愚钝  int  1    50%几率攻击错误的敌人。
396  HEROPOWER_DAMAGE  英雄技能_法术伤害  int  1    仅包含一张卡牌，英雄之魂AT_003
401  EVIL_GLOW  恶魔光环  int  1    包括BRM中的5张龙血之痛牌和5张相应的状态牌，以及诅咒LOE_007t
402  HIDE_STATS  隐藏卡牌数据  int  1    即隐藏随从费用身材以及使英获得异能雄等。包括非随从以及相关的英雄技能(猛烈凝视、颤栗等)等。
403  INSPIRE  激励  int  1    
404  RECEIVES_DOUBLE_SPELLDAMAGE_BONUS  法术伤害享受双倍伤害加成  int  1    仅一张牌：奥术冲击
415  DISCOVER  发现  int  1    有意思的是，虽然发现异能的卡牌有很多，但是该标签下只有一个随从：盛气凌人
424  RITUAL  仪式牌  int  1    包含所有克苏恩体系卡牌和一张安戈洛卡牌：水晶核心。
426  APPEAR_FUNCTIONALLY_DEAD  显示功能性死亡  int  1    仅包含一张首领牌神庙逃亡。该首领没有套牌，也没有生命值，无法被指定。隐藏生命值100。
441  JADE_GOLEM  青玉魔像  int  1    只有两张中立的青玉体系随从(青玉之灵、艾雅黑掌)用到了该标签。
443  CHOOSE_ONE  抉择  int  1    
448  UNTOUCHABLE  不可触及的  int  1    所有持续存在的非随从(也就是说不包括神秘传送门)、猛犸年乱斗中的所有法术(不包括抉择)和一个隐藏状态。
456  CANT_BE_FATIGUED  不会进入疲劳状态  int  1    包含两个英雄牌：卡拉赞中的黑棋国王KAR_a10_Boss2H和乱斗中的黑棋国王KAR_a10_Boss2H_TB。
457  AUTOATTACK  自动攻击  int  1    包含两个随从牌派对捣蛋鬼TB_MammothParty_m001、TB_MammothParty_m001_alt
462  QUEST  任务  int  1    9张任务牌

470  FINISH_ATTACK_SPELL_ON_DAMAGE  攻击结束额外造成法术伤害  int  1    金手指纳克斯
476  MULTIPLE_CLASSES  多职业  int  1    9张中立家族牌。
480  MULTI_CLASS_GROUP  多职业家族  int  1    同上
482  GRIMY_GOONS  污手党  int  1    3张中立污手党卡牌
483  JADE_LOTUS  玉莲帮  int  1    3张中立玉莲帮卡牌
484  KABAL  暗金教  int  1    3张中立暗金教卡牌
535  QUEST_PROGRESS_TOTAL  任务进程计数器  int  1    9张任务牌
537  1    int  1    蛮鱼勇士所独有的特殊标签
542  1    int  1    同上
676  1    int  1    9张任务牌，未知标签
标签TAG  数据类型  注释  
ZONE  string  区域，包括HAND、DECK、PLAY、SECRET、GRAVEYARD、SETASIDE、WEAPON、REMOVEDFROMGAME  
    HAND  手牌区
    DECK  牌库区
    PLAY  战场
    SECRET  奥秘区
    GRAVEYARD  墓地
    SETASIDE  除外区
      
    REMOVEDFROMGAME  从游戏中移除
CONTROLLER  int  控制者，主副玩家  
ENTITY_ID  int  实体ID  
PREMIUM  bool  衍生物  
ATTACHED  int  附着，指示状态牌的附着目标  
DAMAGE  int  所受伤害  
ZONE_POSITION  int  区域内的位置顺序  
NUM_ATTACKS_THIS_TURN  int  本回合攻击次数  
CREATOR  int  创建者  
FORCED_PLAY  bool  直接置入战场  
TO_BE_DESTROYED  bool  待摧毁  
CUSTOM_KEYWORD_EFFECT  int  为关键字制定的特殊效果，如瑟拉金之种的叶子效果  
EXTRA_ATTACKS_THIS_TURN  int  回合内额外攻击  
TAG_LAST_KNOWN_COST_IN_HAND  int  使用之前的实际费用  
HERO_ENTITY  int  英雄实体  
MAXHANDSIZE  int  手牌上限  
STARTHANDSIZE  int  初始手牌数  
PLAYER_ID  int  玩家ID  
TEAM_ID  int  合作ID  
FIRST_PLAYER  bool  标记先手玩家  
MAXRESOURCES  int  法力水晶上限  
MULLIGAN_STATE  string  调度阶段，分为INPUT、WAITING、DONE、DEALING四个步骤  
STEP  string  步骤：BEGIN_MULLIGAN、MAIN_READY、MAIN_START_TRIGGER等  
    BEGIN_MULLIGAN  调度开始
    MAIN_READY  主游戏-准备
    MAIN_START_TRIGGERS  主游戏-触发器
    MAIN_START  主游戏-步骤开始
    MAIN_ACTION  主游戏-动作，如PLAY、TRIGGER、POWER等事件
    MAIN_COMBAT  主游戏-战斗
    MAIN_END  主游戏-步骤结束
    MAIN_CLEANUP  主游戏-清除
    MAIN_NEXT  主游戏-下一步骤
    FINAL_GAMEOVER  最后阶段-游戏终结
    FINAL_WRAPUP  最后阶段-收尾
NEXT_STEP  string  提示下一个STEP  
NUM_TURNS_LEFT  bool  激活当前玩家所剩余回合数，1或0  
CURRENT_PLAYER  int  当前玩家  
TURN  int  回合计数器  
NUM_TURNS_IN_PLAY  int  实体在场上的回合数  
RESOURCES  int  当前玩家水晶  
NUM_CARDS_DRAWN_THIS_TURN  int  本回合内抽牌数  
TIMEOUT  int  回合时长=75s  
EXHAUSTED  bool  疲惫，首回合内无法攻击  
JUST_PLAYED  bool  标记刚打出的牌  
LAST_CARD_PLAYED  int  上一张打出的牌  
RESOURCES_USED  int  当前玩家回合内已使用水晶数  
NUM_RESOURCES_SPENT_THIS_GAME  int  当前玩家游戏内已使用水晶数  
NUM_CARDS_PLAYED_THIS_TURN  int  当前玩家回合内已打出卡牌数  
NUM_MINIONS_PLAYED_THIS_TURN  int  当前玩家回合内已作出动作数  
COMBO_ACTIVE  bool  连击激活  
DISPLAYED_CREATOR  int  左侧对战信息栏显示创建者  
NUM_FRIENDLY_MINIONS_THAT_ATTACKED_THIS_TURN  int  本回合内进行攻击的友方随从数目  
PROPOSED_ATTACKER  int  指定的进攻方  
PROPOSED_DEFENDER  int  指定的承受方，即PROPOSED_ATTACKER的目标  
ATTACKING  bool  正进行攻击  
DEFENDING  bool  正承受攻击  
PREDAMAGE  int  预伤害，即将承受的伤害数  
LAST_AFFECTED_BY  int  上次给予影响的目标  
DAMAGE  int  伤害值  
NUM_MINIONS_PLAYER_KILLED_THIS_TURN  int  玩家回合内杀死的随从数  
NUM_MINIONS_KILLED_THIS_TURN  int  回合内死亡的随从数  
NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_TURN  int  回合内死亡的友方随从数  
NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_GAME  int  游戏内累计死亡的友方随从数  
CARD_TARGET  int  卡牌目标  
PREHEALING  int  预治疗值，即将产生的治疗量  
HEROPOWER_ACTIVATIONS_THIS_TURN  bool  回合内英雄技能激活  
NUM_TIMES_HERO_POWER_USED_THIS_GAME  int  当前玩家游戏内英雄技能累计使用次数  
STATE  string  声明：COMPLETE、RUNNING  
PALYSTATE  string  游戏声明：CONCEDED、LOST、WON、PLAYING  
GOLD_REWARD_STATE  bool  金币奖励动画阶段  
QUEST_PROGRESS_TOTAL  int  任务进程完成总数  
QUEST_PROGRESS  int  任务进程计数器  
QUEST_CONTRIBUTOR  bool  任务触发来源，即标记触发任务的随从  
TAG_SCRIPT_DATA_NUM_1  int  卡牌脚本数据1  视觉与动画效果相关
TAG_SCRIPT_DATA_NUM_2  int  卡牌脚本数据2  视觉与动画效果相关
KAZAKUS_POTION_POWER_1  int  卡扎库斯药水能力1  
KAZAKUS_POTION_POWER_2  int  卡扎库斯药水能力2  
ADDITIONAL_PLAY_REQS_1    额外施放顺序规定1  卡扎库斯药水
ADDITIONAL_PLAY_REQS_2    额外施放顺序规定2  卡扎库斯药水
变量  注释    
Count  计数器    
GameEntity  游戏实体    
Player  玩家实体    
Entity  实体  实体类内涵变量成员：[name，id，zone，zonePos，cardId，player]  
  zonePos  区域位置顺序，等同于ZONE_POSITION  
mainEntity  主实体  变量成员同上  
tag  标签  详见TAG列表  
value  赋值    
TaskCount  任务计数器    
TaskList  任务列表序号    
BlockType  语句块类型：包括PLAY、POWER、TRIGGER、ATTACK、DEATHS、FATIGUE    
    PLAY  打出
    POWER  卡牌效果结算
    ATTACK  攻击
    TRIGGER  触发
    DEATHS  死亡
    FATIGUE  疲劳
ChoiceType  选择类型：包括GENERAL、MULLIGAN    
    GENERAL  普通选项：发现等效果提供的选项，包括卡扎库斯和卡利莫斯等
    MULLIGAN  调度选项
CountMin  选择操作可选下限    
CountMax  选择操作可选上限    
Source  选择选项来源卡牌，如提供发现效果的卡牌    
m_chosenEntities[ ]  已选中实体：选择操作中被选中的选项实体    
EntitiesCount  实体计数器：选择操作中被选中的实体数目    
ID  ID    
ParentID  父序列ID    
PreviousID  前一序列ID    
Block Start  (null)    
Block end  (null)    
m_currentTaskList  当前任务列表序号    
EffectCardId  受影响卡牌ID    
EffectIndex  效果索引    
Target  目标    
option 后接变量  选项描述  变量成员：type，mainEntity，error，errorParam  
  type=  END_TURN  结束回合
    POWER  卡牌效果
  error=  INVALID  无效
    NONE  无
    REQ_YOUR_TURN  需要在己方回合
    REQ_ENOUGH_MANA  需要足够的法力水晶
    REQ_ATTACK_GREATER_THAN_0  需要攻击力大于0
    REQ_NOT_EXHAUSTED_ACTIVATE  需要疲惫状态未生效
    REQ_NOT_MINION_JUST_PLAYED  需要不是刚打出的随从
target 后接变量  error=  REQ_ENEMY_TARGET  需要敌方目标
    REQ_HERO_OR_MINION_TARGET  需要英雄或随从目标
    REQ_MINION_TARGET  需要随从目标
    NONE  无
命令字  注释    
CREATE_GAME  创建游戏，即新一局游戏开始    
FULL_ENTITY - Creating  链接creating变量，完整实体创建，游戏载入、衍生物产生时定义每个实体    
TAG_CHANGE  标签变更，每个事件发生后的标签更新    
BLOCK_START  语句块开始，即事件开始    
BLOCK_END  语句块结束，即事件结束    
SHOW_ENTITY - Updating  链接updating变量，显示刚创建的实体的详细标签列表    
META_DATA - Meta  链接mata变量，如META_DATA - Meta=TARGET Data=0 Info=1；第二行接指针变量，如Info[0]    
  Meta=  DAMAGE  伤害
    TARGET  目标
    SHOW_BIG_CARD  显示大卡
    HISTORY_TARGET  历史目标
HIDE_ENTITY  隐藏实体    
WAIT  出现在玩家从发现等异能中选择卡牌的选择序列中    
BEGIN  同上    
END WAIT  同上    
      
option 0  操作选择序号    
target 0  目标选择序号    
序列  注释
GameState  游戏声明序列
GameState.DebugPrintPowerList  游戏声明-能力列表调试输出列表，后接变量Count，记录列表内的命令数
GameState.DebugPrintPower  游戏声明-能力列表调试输出
GameState.DebugPrintOptions  游戏声明-选项列表调试输出
GameState.DebugPrintEntityChoices  游戏声明-实体选择调试输出，后接指针变量等。如第一行：id=5 Player=细川蓝 TaskList=179 ChoiceType=GENERAL CountMin=1 CountMax=1
ChoiceCardMgr.WaitThenShowChoices  从卡牌管理器选择-等待并显示所选卡牌，如：id=5 WAIT for taskList 179
GameState.SendChoices  游戏声明-发送选择
GameState.DebugPrintEntitiesChosen  游戏声明-被选中的实体调试输出
ChoiceCardMgr.WaitThenHideChoicesFromPacket  从卡牌管理器选择-等待并隐藏选项组剩余选项
PowerTaskList  能力任务列表：即卡牌等实体效果生效相关的任务列表
PowerTaskList.DebugDump  能力任务列表-调试序列数据储存，后接数据变量，如“ID=1 ParentID=0 PreviousID=0 TaskCount=68”，表示该powertasklist编号ID=1，父序列ID=0，上一列表ID=0，列表内任务数count=68
PowerTaskList.DebugPrintPower  游戏声明-能力列表调试输出
PowerProcessor.PrepareHistoryForCurrentTaskList  能力处理器-为当前任务列表创建历史记录，后接变量m_currentTaskList=5，显示当前任务列表序号
PowerProcessor.EndCurrentTaskList  能力处理器-结束当前任务列表，紧跟上一条语句
PowerSpellController [taskListId= ].InitPowerSpell  法术能力施放控制器-初始法术能力施放
  一个例子： PowerSpellController [taskListId=460].InitPowerSpell() - FAILED to attach task list to spell Kazakus_Discover_FX_Screen(Clone) (YoggSaronSpell) for Card [name=卡扎库斯 id=13 zone=PLAY zonePos=4 cardId=CFM_621 player=1]
  卡扎库斯的每个发现选项后都会出现这个语句
如下是一个完整的选择序列：  
GameState.DebugPrintEntityChoices() - id=5 Player=细川蓝 TaskList=179 ChoiceType=GENERAL CountMin=1 CountMax=1  
GameState.DebugPrintEntityChoices() - Source=[name=龙人侦测者 id=69 zone=PLAY zonePos=2 cardId=CFM_605 player=2]  
GameState.DebugPrintEntityChoices() - Entities[0]=[name=火球术 id=75 zone=SETASIDE zonePos=0 cardId=CS2_029 player=2]  
GameState.DebugPrintEntityChoices() - Entities[1]=[name=寒冰屏障 id=76 zone=SETASIDE zonePos=0 cardId=EX1_295 player=2]  
GameState.DebugPrintEntityChoices() - Entities[2]=[name=法力浮龙 id=77 zone=SETASIDE zonePos=0 cardId=NEW1_012 player=2]  
ChoiceCardMgr.WaitThenShowChoices() - id=5 WAIT for taskList 179  
PowerProcessor.EndCurrentTaskList() - m_currentTaskList=179  
ChoiceCardMgr.WaitThenShowChoices() - id=5 BEGIN  
GameState.SendChoices() - id=5 ChoiceType=GENERAL  
GameState.SendChoices() - m_chosenEntities[0]=[name=寒冰屏障 id=76 zone=SETASIDE zonePos=0 cardId=EX1_295 player=2]  
GameState.DebugPrintEntitiesChosen() - id=5 Player=细川蓝 EntitiesCount=1  
GameState.DebugPrintEntitiesChosen() - Entities[0]=[name=寒冰屏障 id=76 zone=SETASIDE zonePos=0 cardId=EX1_295 player=2]  
ChoiceCardMgr.WaitThenHideChoicesFromPacket() - id=5 END WAIT
```
