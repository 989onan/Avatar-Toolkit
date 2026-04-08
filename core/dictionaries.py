# GPL Licence

# Bone names from https://github.com/triazo/immersive_scaler/
# Note from @989onan: Please make sure to make your names are lowercase in this array, or it will never find a match. I banged my head metaphorically till I figured that out...
# Note2: Remove all "_", ".", and " " (space) from your values array or it will also not ever find a match!!!!
# Taken from Tuxedo/Cats

def simplify_bonename(name: str) -> str:
    """Simplify bone name by removing spaces, underscores, dots and converting to lowercase"""
    return name.lower().translate(dict.fromkeys(map(ord, u" _.")))

bone_names = {
    # Right side bones
    "right_shoulder": [
        "rightshoulder", "shoulderr", "rshoulder", "valvebipedbip01rclavicle",
        "右肩", "肩.r", "肩+.r", "右肩+", "右肩", "右肩＋", "肩+r", "肩+右", "ik_肩.r"
    ],
    "right_arm": [
        "rightarm", "armr", "rarm", "upperarmr", "rupperarm", "rightupperarm",
        "uparmr", "ruparm", "valvebipedbip01rupperarm", "右腕", "腕.r", "右腕", "ik_腕.r"
    ],
    "right_elbow": [
        "rightelbow", "elbowr", "relbow", "lowerarmr", "rightlowerarm",
        "rlowerarm", "lowarmr", "rlowarm", "forearmr", "rforearm",
        "valvebipedbip01rforearm", "右ひじ", "ひじ.r", "ik_ひじ.r"
    ],
    "right_wrist": [
        "rightwrist", "wristr", "rwrist", "handr", "righthand", "rhand",
        "valvebipedbip01rhand", "右手首", "手首.r", "ik_手首.r"
    ],
    "pinkie_0_r": [
        "littlefinger0r", "pinkie0r", "rpinkie0", "pinkiemetacarpalr", "右小指０"
    ],
    "pinkie_1_r": [
        "littlefinger1r", "pinkie1r", "rpinkie1", "pinkieproximalr",
        "valvebipedbip01rfinger4", "右小指１"
    ],
    "pinkie_2_r": [
        "littlefinger2r", "pinkie2r", "rpinkie2", "pinkieintermediater",
        "valvebipedbip01rfinger41", "右小指２"
    ],
    "pinkie_3_r": [
        "littlefinger3r", "pinkie3r", "rpinkie3", "pinkiedistalr",
        "valvebipedbip01rfinger42", "右小指３"
    ],
    "ring_0_r": [
        "ringfinger0r", "ring0r", "rring0", "ringmetacarpalr", "右薬指０"
    ],
    "ring_1_r": [
        "ringfinger1r", "ring1r", "rring1", "ringproximalr",
        "valvebipedbip01rfinger3", "右薬指１"
    ],
    "ring_2_r": [
        "ringfinger2r", "ring2r", "rring2", "ringintermediater",
        "valvebipedbip01rfinger31", "右薬指２"
    ],
    "ring_3_r": [
        "ringfinger3r", "ring3r", "rring3", "ringdistalr",
        "valvebipedbip01rfinger32", "右薬指３"
    ],
    "middle_0_r": [
        "middlefinger0r", "middle0r", "rmiddle0", "middlemetacarpalr", "右中指０"
    ],
    "middle_1_r": [
        "middlefinger1r", "middle1r", "rmiddle1", "middleproximalr",
        "valvebipedbip01rfinger2", "右中指１"
    ],
    "middle_2_r": [
        "middlefinger2r", "middle2r", "rmiddle2", "middleintermediater",
        "valvebipedbip01rfinger21", "右中指２"
    ],
    "middle_3_r": [
        "middlefinger3r", "middle3r", "rmiddle3", "middledistalr",
        "valvebipedbip01rfinger22", "右中指３"
    ],
    "index_0_r": [
        "indexfinger0r", "index0r", "rindex0", "indexmetacarpalr", "右人差指０"
    ],
    "index_1_r": [
        "indexfinger1r", "index1r", "rindex1", "indexproximalr",
        "valvebipedbip01rfinger1", "右人差指１"
    ],
    "index_2_r": [
        "indexfinger2r", "index2r", "rindex2", "indexintermediater",
        "valvebipedbip01rfinger11", "右人差指２"
    ],
    "index_3_r": [
        "indexfinger3r", "index3r", "rindex3", "indexdistalr",
        "valvebipedbip01rfinger12", "右人差指３"
    ],
    "thumb_0_r": [
        "thumb0r", "rthumb0", "thumbmetacarpalr", "右親指０"
    ],
    "thumb_1_r": [
        "thumb1r", "rthumb1", "thumbproximalr", "valvebipedbip01rfinger0", "右親指１"
    ],
    "thumb_2_r": [
        "thumb2r", "rthumb2", "thumbintermediater", "valvebipedbip01rfinger01", "右親指２"
    ],
    "thumb_3_r": [
        "thumb3r", "rthumb3", "thumbdistalr", "valvebipedbip01rfinger02", "右親指３"
    ],
    "right_leg": [
        "rightleg", "legr", "rleg", "upperlegr", "rupperleg", "thighr",
        "rightupperleg", "uplegr", "rupleg", "valvebipedbip01rthigh",
        "右足", "足.r", "ik_足.r"
    ],
    "right_knee": [
        "rightknee", "kneer", "rknee", "lowerlegr", "rightlowerleg",
        "rlowerleg", "lowlegr", "rlowleg", "calfr", "rcalf",
        "valvebipedbip01rcalf", "右ひざ", "ひざ.r", "すね.r", "ik_ひざ.r"
    ],
    "right_ankle": [
        "rightankle", "ankler", "rankle", "rightfoot", "footr", "rfoot",
        "rightfeet", "feetright", "rfeet", "feetr", "valvebipedbip01rfoot",
        "右足首", "足首.r", "ik_足首.r"
    ],
    "right_toe": [
        "righttoe", "toeright", "toer", "rtoe", "toesr", "rtoes",
        "valvebipedbip01rtoe0", "右つま先", "つま先.r", "ik_つま先.r"
    ],

    # Left side bones
    "left_shoulder": [
        "leftshoulder", "shoulderl", "lshoulder", "valvebipedbip01lclavicle",
        "左肩", "肩.l", "肩+.l", "左肩+", "左肩", "左肩＋", "肩+l", "肩+左", "ik_肩.l"
    ],
    "left_arm": [
        "leftarm", "arml", "larm", "upperarml", "lupperarm", "leftupperarm",
        "uparml", "luparm", "valvebipedbip01lupperarm", "左腕", "腕.l", "左腕", "ik_腕.l"
    ],
    "left_elbow": [
        "leftelbow", "elbowl", "lelbow", "lowerarml", "leftlowerarm",
        "llowerarm", "lowarml", "llowarm", "forearml", "lforearm",
        "valvebipedbip01lforearm", "左ひじ", "ひじ.l", "すね.l", "ik_ひじ.l"
    ],
    "left_wrist": [
        "leftwrist", "wristl", "lwrist", "handl", "lefthand", "lhand",
        "valvebipedbip01lhand", "左手首", "手首.l", "ik_手首.l"
    ],
    "pinkie_0_l": [
        "pinkiefinger0l", "pinkie0l", "lpinkie0", "pinkiemetacarpall", "左小指０"
    ],
    "pinkie_1_l": [
        "littlefinger1l", "pinkie1l", "lpinkie1", "pinkieproximall",
        "valvebipedbip01lfinger4", "左小指１"
    ],
    "pinkie_2_l": [
        "littlefinger2l", "pinkie2l", "lpinkie2", "pinkieintermediatel",
        "valvebipedbip01lfinger41", "左小指２"
    ],
    "pinkie_3_l": [
        "littlefinger3l", "pinkie3l", "lpinkie3", "pinkiedistall",
        "valvebipedbip01lfinger42", "左小指３"
    ],
    "ring_0_l": [
        "ringfinger0l", "ring0l", "lring0", "ringmetacarpall", "左薬指０"
    ],
    "ring_1_l": [
        "ringfinger1l", "ring1l", "lring1", "ringproximall",
        "valvebipedbip01lfinger3", "左薬指１"
    ],
    "ring_2_l": [
        "ringfinger2l", "ring2l", "lring2", "ringintermediatel",
        "valvebipedbip01lfinger31", "左薬指２"
    ],
    "ring_3_l": [
        "ringfinger3l", "ring3l", "lring3", "ringdistall",
        "valvebipedbip01lfinger32", "左薬指３"
    ],
    "middle_0_l": [
        "middlefinger0l", "middle_0l", "lmiddle0", "middlemetacarpall", "左中指０"
    ],
    "middle_1_l": [
        "middlefinger1l", "middle_1l", "lmiddle1", "middleproximall",
        "valvebipedbip01lfinger2", "左中指１"
    ],
    "middle_2_l": [
        "middlefinger2l", "middle_2l", "lmiddle2", "middleintermediatel",
        "valvebipedbip01lfinger21", "左中指２"
    ],
    "middle_3_l": [
        "middlefinger3l", "middle_3l", "lmiddle3", "middledistall",
        "valvebipedbip01lfinger22", "左中指３"
    ],
    "index_0_l": [
        "indexfinger0l", "index0l", "lindex0", "indexmetacarpall", "左人差指０"
    ],
    "index_1_l": [
        "indexfinger1l", "index1l", "lindex1", "indexproximall",
        "valvebipedbip01lfinger1", "左人差指１"
    ],
    "index_2_l": [
        "indexfinger2l", "index2l", "lindex2", "indexintermediatel",
        "valvebipedbip01lfinger11", "左人差指２"
    ],
    "index_3_l": [
        "indexfinger3l", "index3l", "lindex3", "indexdistall",
        "valvebipedbip01lfinger12", "左人差指３"
    ],
    "thumb_0_l": [
        "thumb0l", "lthumb0", "thumbmetacarpall", "左親指０"
    ],
    "thumb_1_l": [
        "thumb1l", "lthumb1", "thumbproximall", "valvebipedbip01lfinger0", "左親指１"
    ],
    "thumb_2_l": [
        "thumb2l", "lthumb2", "thumbintermediatel", "valvebipedbip01lfinger01", "左親指２"
    ],
    "thumb_3_l": [
        "thumb3l", "lthumb3", "thumbdistall", "valvebipedbip01lfinger02", "左親指３"
    ],
    "left_leg": [
        "leftleg", "legl", "lleg", "upperlegl", "lupperleg", "thighl",
        "leftupperleg", "uplegl", "lupleg", "valvebipedbip01lthigh",
        "左足", "足.l", "ik_足.l"
    ],
    "left_knee": [
        "leftknee", "kneel", "lknee", "lowerlegl", "leftlowerleg",
        "llowerleg", "lowlegl", "llowleg", "calfl", "lcalf",
        "valvebipedbip01lcalf", "左ひざ", "ひざ.l", "すね.l", "ik_ひざ.l"
    ],
    "left_ankle": [
        "leftankle", "anklel", "lankle", "leftfoot", "footl", "lfoot",
        "leftfeet", "feetleft", "lfeet", "feetl", "valvebipedbip01lfoot",
        "左足首", "足首.l", "ik_足首.l"
    ],
    "left_toe": [
        "lefttoe", "toeleft", "toel", "ltoe", "toesl", "ltoes",
        "valvebipedbip01ltoe0", "左つま先", "つま先.l", "ik_つま先.l"
    ],

    # Central bones
    "hips": [
        "pelvis", "hips", "hip", "valvebipedbip01pelvis", "腰", "ik_腰"
    ],
    "spine": [
        "torso", "spine", "valvebipedbip01spine", "脊椎", "ik_脊椎"
    ],
    "chest": [
        "chest", "valvebipedbip01spine1", "胸", "ik_胸"
    ],
    "upper_chest": [
        "upperchest", "valvebipedbip01spine4", "上胸", "ik_上胸"
    ],
    "neck": [
        "neck", "valvebipedbip01neck1", "首", "ik_首"
    ],
    "head": [
        "head", "valvebipedbip01head1", "頭", "ik_頭"
    ],
    "left_eye": [
        "eyeleft", "lefteye", "eyel", "leye", "左目", "ik_左目"
    ],
    "right_eye": [
        "eyeright", "righteye", "eyer", "reye", "右目", "ik_右目"
    ],
    "breast_1_l": [
        "j_sec_l_bust1", "breast1_l", "leftbreast1", "lbreast1", "bust1_l"
    ],
    "breast_2_l": [
        "j_sec_l_bust2", "breast2_l", "leftbreast2", "lbreast2", "bust2_l"
    ],
    "breast_3_l": [
        "j_sec_l_bust3", "breast3_l", "leftbreast3", "lbreast3", "bust3_l"
    ],
    "breast_1_r": [
        "j_sec_r_bust1", "breast1_r", "rightbreast1", "rbreast1", "bust1_r"
    ],
    "breast_2_r": [
        "j_sec_r_bust2", "breast2_r", "rightbreast2", "rbreast2", "bust2_r"
    ],
    "breast_3_r": [
        "j_sec_r_bust3", "breast3_r", "rightbreast3", "rbreast3", "bust3_r"
    ]
}

# Add VRM bone name variations  
bone_names.update({
    'hips': bone_names['hips'] + ['jbipchips', 'jhips', 'vrmhips', 'leftupperleg', 'rightupperleg'],
    'spine': bone_names['spine'] + ['jbipcspine', 'jspine', 'vrmspine'],
    'chest': bone_names['chest'] + ['jbipcchest', 'jchest', 'vrmchest', 'upperchest'],
    'upper_chest': bone_names['upper_chest'] + ['jbipcupperchest', 'jupperchest', 'vrmupperchest', 'upperchest'],
    'neck': bone_names['neck'] + ['jbipcneck', 'jneck', 'vrmneck'],
    'head': bone_names['head'] + ['jbipchead', 'jhead', 'vrmhead', 'lefteye', 'righteye'],
    
    # VRM arms - both simplified patterns
    'left_shoulder': bone_names['left_shoulder'] + ['jbipllshoulder', 'jlshoulder', 'jbiplshoulder', 'leftshoulder', 'jbipllclavicle'],
    'left_arm': bone_names['left_arm'] + ['jbiplupperarm', 'jlupperarm', 'leftupperarm'],
    'left_elbow': bone_names['left_elbow'] + ['jbipllforearm', 'jlforearm', 'jbipllowerarm', 'leftlowerarm'],
    'left_wrist': bone_names['left_wrist'] + ['jbipllhand', 'jlhand', 'jbiplhand', 'lefthand'],
    
    'right_shoulder': bone_names['right_shoulder'] + ['jbiprlshoulder', 'jrshoulder', 'jbiprshoulder', 'rightshoulder', 'jbiprrclavicle'],
    'right_arm': bone_names['right_arm'] + ['jbiprrupperarm', 'jrupperarm', 'jbiprupperarm', 'rightupperarm'],
    'right_elbow': bone_names['right_elbow'] + ['jbiprrforearm', 'jrforearm', 'jbiprforearm', 'jbiprlowerarm', 'rightlowerarm'],
    'right_wrist': bone_names['right_wrist'] + ['jbiprrhand', 'jrhand', 'jbiprhand', 'righthand'],
    
    # VRM legs - both simplified patterns
    'left_leg': bone_names['left_leg'] + ['jbiplupperleg', 'jlupperleg', 'leftupperleg'],
    'left_knee': bone_names['left_knee'] + ['jbipllowerleg', 'jllowerleg', 'leftlowerleg'],
    'left_ankle': bone_names['left_ankle'] + ['jbipllfoot', 'jlfoot', 'jbiplfoot', 'leftfoot'],
    'left_toe': bone_names['left_toe'] + ['jbiplltoe', 'jltoe', 'jbipltoebase', 'lefttoes'],
    
    'right_leg': bone_names['right_leg'] + ['jbiprrupperleg', 'jrupperleg', 'jbiprupperleg', 'rightupperleg'],
    'right_knee': bone_names['right_knee'] + ['jbiprrlowerleg', 'jrlowerleg', 'jbiprlowerleg', 'rightlowerleg'],
    'right_ankle': bone_names['right_ankle'] + ['jbiprrfoot', 'jrfoot', 'jbiprfoot', 'rightfoot'],
    'right_toe': bone_names['right_toe'] + ['jbiprrtoe', 'jrtoe', 'jbiprtoebase', 'righttoes'],
    
    # VRM eyes
    'left_eye': bone_names['left_eye'] + ['jbipcleye', 'jleye', 'jadjlfaceeye'],
    'right_eye': bone_names['right_eye'] + ['jbipcreye', 'jreye', 'jadjrfaceeye'],
    
    # VRM jaw
    'jaw': ['jaw', 'mandible', 'lowerjaw', 'chin', 'あご', 'ik_あご'],
    
    # Breast bones
    'breast_1_l': bone_names['breast_1_l'] + ['jbipcbreast1l', 'jlbreast1', 'jseclbust1'],
    'breast_2_l': bone_names['breast_2_l'] + ['jbipcbreast2l', 'jlbreast2', 'jseclbust2'],
    'breast_3_l': bone_names['breast_3_l'] + ['jbipcbreast3l', 'jlbreast3', 'jseclbust3'],
    'breast_1_r': bone_names['breast_1_r'] + ['jbipcbreast1r', 'jrbreast1', 'jsecrbust1'],
    'breast_2_r': bone_names['breast_2_r'] + ['jbipcbreast2r', 'jrbreast2', 'jsecrbust2'],
    'breast_3_r': bone_names['breast_3_r'] + ['jbipcbreast3r', 'jrbreast3', 'jsecrbust3'],
    
    # VRM fingers - Left (including Little finger variations)
    'thumb_0_l': bone_names['thumb_0_l'] + ['jbipllthumb0', 'jlthumb0', 'jbipllthumbmetacarpal', 'jlthumbmetacarpal', 'leftthumbmetacarpal'],
    'thumb_1_l': bone_names['thumb_1_l'] + ['jbipllthumb1', 'jlthumb1', 'jbiplthumb1', 'leftthumbproximal'],
    'thumb_2_l': bone_names['thumb_2_l'] + ['jbipllthumb2', 'jlthumb2', 'jbiplthumb2', 'leftthumbintermediate'],
    'thumb_3_l': bone_names['thumb_3_l'] + ['jbipllthumb3', 'jlthumb3', 'jbiplthumb3', 'leftthumbdistal'],
    
    'index_1_l': bone_names['index_1_l'] + ['jbipllindex1', 'jlindex1', 'jbiplindex1', 'leftindexproximal'],
    'index_2_l': bone_names['index_2_l'] + ['jbipllindex2', 'jlindex2', 'jbiplindex2', 'leftindexintermediate'],
    'index_3_l': bone_names['index_3_l'] + ['jbipllindex3', 'jlindex3', 'jbiplindex3', 'leftindexdistal'],
    
    'middle_1_l': bone_names['middle_1_l'] + ['jbipllmiddle1', 'jlmiddle1', 'jbiplmiddle1', 'leftmiddleproximal'],
    'middle_2_l': bone_names['middle_2_l'] + ['jbipllmiddle2', 'jlmiddle2', 'jbiplmiddle2', 'leftmiddleintermediate'],
    'middle_3_l': bone_names['middle_3_l'] + ['jbipllmiddle3', 'jlmiddle3', 'jbiplmiddle3', 'leftmiddledistal'],
    
    'ring_1_l': bone_names['ring_1_l'] + ['jbipllring1', 'jlring1', 'jbiplring1', 'leftringproximal'],
    'ring_2_l': bone_names['ring_2_l'] + ['jbipllring2', 'jlring2', 'jbiplring2', 'leftringintermediate'],
    'ring_3_l': bone_names['ring_3_l'] + ['jbipllring3', 'jlring3', 'jbiplring3', 'leftringdistal'],
    
    'pinkie_1_l': bone_names['pinkie_1_l'] + ['jbipllpinky1', 'jlpinky1', 'jbipllittle1', 'jbipllpinkie1', 'leftlittleproximal'],
    'pinkie_2_l': bone_names['pinkie_2_l'] + ['jbipllpinky2', 'jlpinky2', 'jbipllittle2', 'jbipllpinkie2', 'leftlittleintermediate'],
    'pinkie_3_l': bone_names['pinkie_3_l'] + ['jbipllpinky3', 'jlpinky3', 'jbipllittle3', 'jbipllpinkie3', 'leftlittledistal'],
    
    # VRM fingers - Right (including Little finger variations)
    'thumb_0_r': bone_names['thumb_0_r'] + ['jbiprthumb0', 'jrthumb0', 'jbiprthumbmetacarpal', 'jrthumbmetacarpal', 'rightthumbmetacarpal'],
    'thumb_1_r': bone_names['thumb_1_r'] + ['jbiprthumb1', 'jrthumb1', 'jbiprrrthumb1', 'rightthumbproximal'],
    'thumb_2_r': bone_names['thumb_2_r'] + ['jbiprthumb2', 'jrthumb2', 'jbiprrrthumb2', 'rightthumbintermediate'],
    'thumb_3_r': bone_names['thumb_3_r'] + ['jbiprthumb3', 'jrthumb3', 'jbiprrrthumb3', 'rightthumbdistal'],
    
    'index_1_r': bone_names['index_1_r'] + ['jbiprindex1', 'jrindex1', 'jbiprrrindex1', 'rightindexproximal'],
    'index_2_r': bone_names['index_2_r'] + ['jbiprindex2', 'jrindex2', 'jbiprrrindex2', 'rightindexintermediate'],
    'index_3_r': bone_names['index_3_r'] + ['jbiprindex3', 'jrindex3', 'jbiprrrindex3', 'rightindexdistal'],
    
    'middle_1_r': bone_names['middle_1_r'] + ['jbiprmiddle1', 'jrmiddle1', 'jbiprrmiddle1', 'rightmiddleproximal'],
    'middle_2_r': bone_names['middle_2_r'] + ['jbiprmiddle2', 'jrmiddle2', 'jbiprrmiddle2', 'rightmiddleintermediate'],
    'middle_3_r': bone_names['middle_3_r'] + ['jbiprmiddle3', 'jrmiddle3', 'jbiprrmiddle3', 'rightmiddledistal'],
    
    'ring_1_r': bone_names['ring_1_r'] + ['jbiprring1', 'jrring1', 'jbiprrrring1', 'rightringproximal'],
    'ring_2_r': bone_names['ring_2_r'] + ['jbiprring2', 'jrring2', 'jbiprrrring2', 'rightringintermediate'],
    'ring_3_r': bone_names['ring_3_r'] + ['jbiprring3', 'jrring3', 'jbiprrrring3', 'rightringdistal'],
    
    'pinkie_1_r': bone_names['pinkie_1_r'] + ['jbiprpinky1', 'jrpinky1', 'jbiprlittle1', 'jbiprrrpinky1', 'rightlittleproximal'],
    'pinkie_2_r': bone_names['pinkie_2_r'] + ['jbiprpinky2', 'jrpinky2', 'jbiprlittle2', 'jbiprrrpinky2', 'rightlittleintermediate'],
    'pinkie_3_r': bone_names['pinkie_3_r'] + ['jbiprpinky3', 'jrpinky3', 'jbiprlittle3', 'jbiprrrpinky3', 'rightlittledistal']
})

# array taken from cats
dont_delete_these_main_bones = [
    'Hips', 'Spine', 'Chest', 'Upper Chest', 'Neck', 'Head',
    'Left leg', 'Left knee', 'Left ankle', 'Left toe',
    'Right leg', 'Right knee', 'Right ankle', 'Right toe',
    'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist',
    'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist',
    'LeftEye', 'RightEye', 'Eye_L', 'Eye_R',
    'Left leg 2', 'Right leg 2',

    'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
    'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
    'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
    'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
    'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',

    'Thumb0_R', 'Thumb1_R', 'Thumb2_R',
    'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
    'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
    'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
    'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',
]

resonite_translations = {
    'hips': "Hips",
    'spine': "Spine",
    'chest': "Chest",
    'neck': "Neck",
    'head': "Head",
    'left_eye': "Eye.L",
    'right_eye': "Eye.R",
    'right_leg': "UpperLeg.R",
    'right_knee': "Calf.R",
    'right_ankle': "Foot.R",
    'right_toe': 'Toes.R',
    'right_shoulder': "Shoulder.R",
    'right_arm': "UpperArm.R",
    'right_elbow': "ForeArm.R",
    'right_wrist': "Hand.R",
    'left_leg': "UpperLeg.L",
    'left_knee': "Calf.L",
    'left_ankle': "Foot.L",
    'left_toe': "Toes.L",
    'left_shoulder': "Shoulder.L",
    'left_arm': "UpperArm.L",
    'left_elbow': "ForeArm.L",
    'left_wrist': "Hand.L",
    'pinkie_1_l': "pinkie1.L",
    'pinkie_2_l': "pinkie2.L",
    'pinkie_3_l': "pinkie3.L",
    'ring_1_l': "ring1.L",
    'ring_2_l': "ring2.L",
    'ring_3_l': "ring3.L",
    'middle_1_l': "middle1.L",
    'middle_2_l': "middle2.L",
    'middle_3_l': "middle3.L",
    'index_1_l': "index1.L",
    'index_2_l': "index2.L",
    'index_3_l': "index3.L",
    'thumb_1_l': "thumb1.L",
    'thumb_2_l': "thumb2.L",
    'thumb_3_l': "thumb3.L",
    'pinkie_1_r': "pinkie1.R",
    'pinkie_2_r': "pinkie2.R",
    'pinkie_3_r': "pinkie3.R",
    'ring_1_r': "ring1.R",
    'ring_2_r': "ring2.R",
    'ring_3_r': "ring3.R",
    'middle_1_r': "middle1.R",
    'middle_2_r': "middle2.R",
    'middle_3_r': "middle3.R",
    'index_1_r': "index1.R",
    'index_2_r': "index2.R",
    'index_3_r': "index3.R",
    'thumb_1_r': "thumb1.R",
    'thumb_2_r': "thumb2.R",
    'thumb_3_r': "thumb3.R"
}



standard_bones = {
    # Core Structure
    'hips': 'Hips',
    'spine': 'Spine',
    'chest': 'Chest',
    'upper_chest': 'UpperChest',
    'neck': 'Neck',
    'head': 'Head',
    
    # Arms
    'left_shoulder': 'Shoulder_L',
    'left_arm': 'UpperArm_L',
    'left_elbow': 'LowerArm_L',
    'left_wrist': 'Hand_L',
    'right_shoulder': 'Shoulder_R',
    'right_arm': 'UpperArm_R',
    'right_elbow': 'LowerArm_R',
    'right_wrist': 'Hand_R',
    
    # Legs
    'left_leg': 'UpperLeg_L',
    'left_knee': 'LowerLeg_L',
    'left_ankle': 'Foot_L',
    'left_toe': 'Toe_L',
    'right_leg': 'UpperLeg_R',
    'right_knee': 'LowerLeg_R',
    'right_ankle': 'Foot_R',
    'right_toe': 'Toe_R',
    
    # Fingers Left
    'thumb_1_l': 'Thumb_L',
    'thumb_2_l': 'Thumb_L.001',
    'thumb_3_l': 'Thumb_L.002',
    'index_1_l': 'Index_L',
    'index_2_l': 'Index_L.001',
    'index_3_l': 'Index_L.002',
    'middle_1_l': 'Middle_L',
    'middle_2_l': 'Middle_L.001',
    'middle_3_l': 'Middle_L.002',
    'ring_1_l': 'Ring_L',
    'ring_2_l': 'Ring_L.001',
    'ring_3_l': 'Ring_L.002',
    'pinkie_1_l': 'Pinky_L',
    'pinkie_2_l': 'Pinky_L.001',
    'pinkie_3_l': 'Pinky_L.002',
    
    # Fingers Right
    'thumb_1_r': 'Thumb_R',
    'thumb_2_r': 'Thumb_R.001',
    'thumb_3_r': 'Thumb_R.002',
    'index_1_r': 'Index_R',
    'index_2_r': 'Index_R.001',
    'index_3_r': 'Index_R.002',
    'middle_1_r': 'Middle_R',
    'middle_2_r': 'Middle_R.001',
    'middle_3_r': 'Middle_R.002',
    'ring_1_r': 'Ring_R',
    'ring_2_r': 'Ring_R.001',
    'ring_3_r': 'Ring_R.002',
    'pinkie_1_r': 'Pinky_R',
    'pinkie_2_r': 'Pinky_R.001',
    'pinkie_3_r': 'Pinky_R.002',
    
    # Eyes
    'left_eye': 'Eye_L',
    'right_eye': 'Eye_R',
    
    # Breast bones
    'breast_1_l': 'Breast1_L',
    'breast_2_l': 'Breast2_L',
    'breast_3_l': 'Breast3_L',
    'breast_1_r': 'Breast1_R',
    'breast_2_r': 'Breast2_R',
    'breast_3_r': 'Breast3_R'
}

bone_hierarchy = [
    ('Hips', 'Spine'),
    ('Spine', 'Chest'),
    ('Chest', 'UpperChest'),
    ('UpperChest', 'Neck'),
    ('Neck', 'Head'),
    ('Head', 'Eye_L'),
    ('Head', 'Eye_R'),
    
    # Left Arm Chain
    ('UpperChest', 'Shoulder_L'),
    ('Shoulder_L', 'UpperArm_L'),
    ('UpperArm_L', 'LowerArm_L'),
    ('LowerArm_L', 'Hand_L'),
    
    # Right Arm Chain
    ('UpperChest', 'Shoulder_R'),
    ('Shoulder_R', 'UpperArm_R'),
    ('UpperArm_R', 'LowerArm_R'),
    ('LowerArm_R', 'Hand_R'),
    
    # Left Leg Chain
    ('Hips', 'UpperLeg_L'),
    ('UpperLeg_L', 'LowerLeg_L'),
    ('LowerLeg_L', 'Foot_L'),
    ('Foot_L', 'Toe_L'),
    
    # Right Leg Chain
    ('Hips', 'UpperLeg_R'),
    ('UpperLeg_R', 'LowerLeg_R'),
    ('LowerLeg_R', 'Foot_R'),
    ('Foot_R', 'Toe_R')
]

finger_hierarchy = {
    'left': [
        ('Hand_L', 'Thumb_L', 'Thumb_L.001', 'Thumb_L.002'),
        ('Hand_L', 'Index_L', 'Index_L.001', 'Index_L.002'),
        ('Hand_L', 'Middle_L', 'Middle_L.001', 'Middle_L.002'),
        ('Hand_L', 'Ring_L', 'Ring_L.001', 'Ring_L.002'),
        ('Hand_L', 'Pinky_L', 'Pinky_L.001', 'Pinky_L.002')
    ],
    'right': [
        ('Hand_R', 'Thumb_R', 'Thumb_R.001', 'Thumb_R.002'),
        ('Hand_R', 'Index_R', 'Index_R.001', 'Index_R.002'),
        ('Hand_R', 'Middle_R', 'Middle_R.001', 'Middle_R.002'),
        ('Hand_R', 'Ring_R', 'Ring_R.001', 'Ring_R.002'),
        ('Hand_R', 'Pinky_R', 'Pinky_R.001', 'Pinky_R.002')
    ]
}

acceptable_bone_hierarchy = [
    # Right side chain
    ('Hips', 'Chest'),
    ('Chest', 'Shoulder.R'),
    ('Shoulder.R', 'Arm.R'),
    ('Arm.R', 'Elbow.R'),
    ('Elbow.R', 'Wrist.R'),
    ('Hips', 'Leg.R'),
    ('Leg.R', 'Knee.R'),
    ('Knee.R', 'Foot.R'),
    ('Foot.R', 'Toes.R'),
    
    # Left side chain
    ('Chest', 'Shoulder.L'),
    ('Shoulder.L', 'Arm.L'),
    ('Arm.L', 'Elbow.L'),
    ('Elbow.L', 'Wrist.L'),
    ('Hips', 'Leg.L'),
    ('Leg.L', 'Knee.L'),
    ('Knee.L', 'Foot.L'),
    ('Foot.L', 'Toes.L'),

    # Head and Eyes
    ('Chest', 'Neck'),
    ('Neck', 'Head'),
    ('Head', 'Eye_L'),
    ('Head', 'Eye_R'),
    ('Head', 'LeftEye'),
    ('Head', 'RightEye'),
    ('Head', 'Eye.L'),
    ('Head', 'Eye.R'),
        
    # Unity humanoid naming
    ('Hips', 'Spine'),
    ('Spine', 'Chest'),
    ('Chest', 'UpperChest'),
    ('UpperChest', 'Neck'),
    ('Neck', 'Head'),
    ('Head', 'LeftEye'),
    ('Head', 'RightEye'),
    
    # Old standard bone hierarchy patterns
    ('UpperChest', 'UpperArm.L'),
    ('UpperArm.L', 'LowerArm.L'),
    ('LowerArm.L', 'Hand.L'),
    ('UpperChest', 'UpperArm.R'),
    ('UpperArm.R', 'LowerArm.R'),
    ('LowerArm.R', 'Hand.R'),
    ('Hips', 'UpperLeg.L'),
    ('UpperLeg.L', 'LowerLeg.L'),
    ('LowerLeg.L', 'Foot.L'),
    ('Foot.L', 'Toes.L'),
    ('Hips', 'UpperLeg.R'),
    ('UpperLeg.R', 'LowerLeg.R'),
    ('LowerLeg.R', 'Foot.R'),
    ('Foot.R', 'Toes.R'),
    
    # New standard bone hierarchy patterns (with shoulders)
    ('UpperChest', 'Shoulder_L'),
    ('Shoulder_L', 'UpperArm_L'),
    ('UpperArm_L', 'LowerArm_L'),
    ('LowerArm_L', 'Hand_L'),
    ('UpperChest', 'Shoulder_R'),
    ('Shoulder_R', 'UpperArm_R'),
    ('UpperArm_R', 'LowerArm_R'),
    ('LowerArm_R', 'Hand_R'),
    ('Hips', 'UpperLeg_L'),
    ('UpperLeg_L', 'LowerLeg_L'),
    ('LowerLeg_L', 'Foot_L'),
    ('Foot_L', 'Toe_L'),
    ('Hips', 'UpperLeg_R'),
    ('UpperLeg_R', 'LowerLeg_R'),
    ('LowerLeg_R', 'Foot_R'),
    ('Foot_R', 'Toe_R'),
    
]

acceptable_bone_names = {
    'hips': ['Hips', 'pelvis', 'root', 'Root', 'ROOT'],
    'chest': ['Chest', 'spine1', 'Spine1', 'spine_01', 'SPINE1', 'Spine01'],
    'neck': ['Neck', 'neck_01', 'Neck01'],
    'head': ['Head', 'head_01', 'Head01'],
    'eye_l': ['Eye_L', 'LeftEye', 'lefteye', 'eye_left', 'EyeLeft', 'Eye.L'],
    'eye_r': ['Eye_R', 'RightEye', 'righteye', 'eye_right', 'EyeRight', 'Eye.R'],
    
    'shoulder_r': ['Shoulder.R', 'clavicle_r', 'ClavicleRight', 'RightShoulder', 'Shoulder_R'],
    'arm_r': ['Arm.R', 'upperarm_r', 'UpperArmRight', 'RightArm', 'UpperArm.R', 'UpperArm_R'],
    'elbow_r': ['Elbow.R', 'lowerarm_r', 'ForearmRight', 'RightForeArm', 'LowerArm.R', 'LowerArm_R'],
    'wrist_r': ['Wrist.R', 'hand_r', 'HandRight', 'RightHand', 'Hand.R', 'Hand_R'],
    'leg_r': ['Leg.R', 'thigh_r', 'ThighRight', 'RightLeg', 'RightUpLeg', 'UpperLeg.R', 'UpperLeg_R'],
    'knee_r': ['Knee.R', 'calf_r', 'CalfRight', 'RightShin', 'RightLowerLeg', 'LowerLeg.R', 'LowerLeg_R'],
    'foot_r': ['Foot.R', 'foot_r', 'FootRight', 'RightFoot', 'Foot_R'],
    'toes_r': ['Toes.R', 'ball_r', 'ToeRight', 'RightToeBase', 'Toe_R'],
    
    'shoulder_l': ['Shoulder.L', 'clavicle_l', 'ClavicleLeft', 'LeftShoulder', 'Shoulder_L'],
    'arm_l': ['Arm.L', 'upperarm_l', 'UpperArmLeft', 'LeftArm', 'UpperArm.L', 'UpperArm_L'],
    'elbow_l': ['Elbow.L', 'lowerarm_l', 'ForearmLeft', 'LeftForeArm', 'LowerArm.L', 'LowerArm_L'],
    'wrist_l': ['Wrist.L', 'hand_l', 'HandLeft', 'LeftHand', 'Hand.L', 'Hand_L'],
    'leg_l': ['Leg.L', 'thigh_l', 'ThighLeft', 'LeftLeg', 'LeftUpLeg', 'UpperLeg.L', 'UpperLeg_L'],
    'knee_l': ['Knee.L', 'calf_l', 'CalfLeft', 'LeftShin', 'LeftLowerLeg', 'LowerLeg.L', 'LowerLeg_L'],
    'foot_l': ['Foot.L', 'foot_l', 'FootLeft', 'LeftFoot', 'Foot_L'],
    'toes_l': ['Toes.L', 'ball_l', 'ToeLeft', 'LeftToeBase', 'Toe_L'],
    
    # Add finger bones for left hand
    'thumb_0_l': ['Thumb0_L', 'Thumb0.L'],
    'thumb_1_l': ['Thumb1_L', 'Thumb1.L', 'Thumb_L'],
    'thumb_2_l': ['Thumb2_L', 'Thumb2.L', 'Thumb_L.001'],
    'thumb_3_l': ['Thumb3_L', 'Thumb3.L', 'Thumb_L.002'],
    'index_1_l': ['IndexFinger1_L', 'IndexFinger1.L', 'Index1.L', 'Index_L'],
    'index_2_l': ['IndexFinger2_L', 'IndexFinger2.L', 'Index2.L', 'Index_L.001'],
    'index_3_l': ['IndexFinger3_L', 'IndexFinger3.L', 'Index3.L', 'Index_L.002'],
    'middle_1_l': ['MiddleFinger1_L', 'MiddleFinger1.L', 'Middle1.L', 'Middle_L'],
    'middle_2_l': ['MiddleFinger2_L', 'MiddleFinger2.L', 'Middle2.L', 'Middle_L.001'],
    'middle_3_l': ['MiddleFinger3_L', 'MiddleFinger3.L', 'Middle3.L', 'Middle_L.002'],
    'ring_1_l': ['RingFinger1_L', 'RingFinger1.L', 'Ring1.L', 'Ring_L'],
    'ring_2_l': ['RingFinger2_L', 'RingFinger2.L', 'Ring2.L', 'Ring_L.001'],
    'ring_3_l': ['RingFinger3_L', 'RingFinger3.L', 'Ring3.L', 'Ring_L.002'],
    'pinky_1_l': ['Pinky1_L', 'Pinky1.L', 'Pinky_L'],
    'pinky_2_l': ['Pinky2_L', 'Pinky2.L', 'Pinky_L.001'],
    'pinky_3_l': ['Pinky3_L', 'Pinky3.L', 'Pinky_L.002'],
    
    # Add finger bones for right hand
    'thumb_0_r': ['Thumb0_R', 'Thumb0.R', 'ThumbO_R'],
    'thumb_1_r': ['Thumb1_R', 'Thumb1.R', 'Thumb_R'],
    'thumb_2_r': ['Thumb2_R', 'Thumb2.R', 'Thumb_R.001'],
    'thumb_3_r': ['Thumb3_R', 'Thumb3.R', 'Thumb_R.002'],
    'index_1_r': ['IndexFinger1_R', 'IndexFinger1.R', 'Index1.R', 'Index_R'],
    'index_2_r': ['IndexFinger2_R', 'IndexFinger2.R', 'Index2.R', 'Index_R.001'],
    'index_3_r': ['IndexFinger3_R', 'IndexFinger3.R', 'Index3.R', 'Index_R.002'],
    'middle_1_r': ['MiddleFinger1_R', 'MiddleFinger1.R', 'Middle1.R', 'Middle_R'],
    'middle_2_r': ['MiddleFinger2_R', 'MiddleFinger2.R', 'Middle2.R', 'Middle_R.001'],
    'middle_3_r': ['MiddleFinger3_R', 'MiddleFinger3.R', 'Middle3.R', 'Middle_R.002'],
    'ring_1_r': ['RingFinger1_R', 'RingFinger1.R', 'Ring1.R', 'Ring_R'],
    'ring_2_r': ['RingFinger2_R', 'RingFinger2.R', 'Ring2.R', 'Ring_R.001'],
    'ring_3_r': ['RingFinger3_R', 'RingFinger3.R', 'Ring3.R', 'Ring_R.002'],
    'pinky_1_r': ['Pinky1_R', 'Pinky1.R', 'Pinky_R'],
    'pinky_2_r': ['Pinky2_R', 'Pinky2.R', 'Pinky_R.001'],
    'pinky_3_r': ['Pinky3_R', 'Pinky3.R', 'Pinky_R.002'],
    
    'breast_upper_1_l': ['BreastUpper1_L', 'BreastUpper1.L'],
    'breast_upper_2_l': ['BreastUpper2_L', 'BreastUpper2.L'],
    'breast_upper_1_r': ['BreastUpper1_R', 'BreastUpper1.R'],
    'breast_upper_2_r': ['BreastUpper2_R', 'BreastUpper2.R'],

    # Little finger bones
    'little_finger_1_l': ['LittleFinger1_L', 'LittleFinger1.L'],
    'little_finger_2_l': ['LittleFinger2_L', 'LittleFinger2.L'],
    'little_finger_3_l': ['LittleFinger3_L', 'LittleFinger3.L'],
    'little_finger_1_r': ['LittleFinger1_R', 'LittleFinger1.R'],
    'little_finger_2_r': ['LittleFinger2_R', 'LittleFinger2.R'],
    'little_finger_3_r': ['LittleFinger3_R', 'LittleFinger3.R'],

    'ear_upper_l': ['UpperEar.L', 'Upper Ear.L', 'Upper Ear_L'],
    'ear_upper_r': ['UpperEar.R', 'Upper Ear.R', 'Upper Ear_R'],
    'ear_lower_l': ['LowerEar.L', 'Lower Ear.L', 'Lower Ear_L'],
    'ear_lower_r': ['LowerEar.R', 'Lower Ear.R', 'Lower Ear_R'],

    'ears_upper': ['Ears Upper', 'EarsUpper', 'ears_upper'],
    'ears_lower': ['Ears Lower', 'EarsLower', 'ears_lower']
}

rigify_unity_names = {
    "DEF-spine": "Hips",
    "DEF-spine.001": "Spine",
    "DEF-spine.002": "Chest",
    "DEF-spine.003": "UpperChest",
    "DEF-neck": "Neck",
    "DEF-head": "Head",
    "DEF-shoulder.L": "LeftShoulder",
    "DEF-upper_arm.L": "LeftUpperArm",
    "DEF-forearm.L": "LeftLowerArm",
    "DEF-hand.L": "LeftHand",
    "DEF-shoulder.R": "RightShoulder",
    "DEF-upper_arm.R": "RightUpperArm",
    "DEF-forearm.R": "RightLowerArm",
    "DEF-hand.R": "RightHand",
    "DEF-thigh.L": "LeftUpperLeg",
    "DEF-shin.L": "LeftLowerLeg",
    "DEF-foot.L": "LeftFoot",
    "DEF-toe.L": "LeftToes",
    "DEF-thigh.R": "RightUpperLeg",
    "DEF-shin.R": "RightLowerLeg",
    "DEF-foot.R": "RightFoot",
    "DEF-toe.R": "RightToes"
}

rigify_basic_unity_names = {
    "spine": "Hips",
    "spine.001": "Spine",
    "spine.002": "Chest",
    "spine.003": "UpperChest",
    "neck": "Neck",
    "head": "Head",
    "shoulder.L": "LeftShoulder",
    "upper_arm.L": "LeftUpperArm",
    "forearm.L": "LeftLowerArm",
    "hand.L": "LeftHand",
    "shoulder.R": "RightShoulder",
    "upper_arm.R": "RightUpperArm",
    "forearm.R": "RightLowerArm",
    "hand.R": "RightHand",
    "thigh.L": "LeftUpperLeg",
    "shin.L": "LeftLowerLeg",
    "foot.L": "LeftFoot",
    "toe.L": "LeftToes",
    "thigh.R": "RightUpperLeg",
    "shin.R": "RightLowerLeg",
    "foot.R": "RightFoot",
    "toe.R": "RightToes"
}

rigify_unnecessary_bones = [
    'face',
    'ear.l', 'ear.r',
    'forehead',
    'cheek.t.l', 'cheek.t.r',
    'cheek.b.l', 'cheek.b.r',
    'brow.t.l', 'brow.t.r',
    'brow.b.l', 'brow.b.r',
    'jaw',
    'chin',
    'nose',
    'temple.l', 'temple.r',
    'teeth',
    'lip',
    'lid',
    'heel',
    'pelvis.'
]

# Non-standard bone mappings to standard bones
non_standard_mappings = {
    'hips': [
        'mixamorig:Hips', 'mixamorig_Hips', 
        'ORG-spine', 'spine', 'root',
        'hip', 'pelvis'
    ],
    'spine': [
        'mixamorig:Spine', 'mixamorig_Spine',
        'ORG-spine.001', 'spine.001',
        'abdomenLower', 'lowerback'
    ],
    'chest': [
        'mixamorig:Spine1', 'mixamorig_Spine1',
        'ORG-spine.002', 'spine.002',
        'abdomenUpper', 'upperback', 'spine1'
    ],
    'upper_chest': [
        'mixamorig:Spine2', 'mixamorig_Spine2',
        'ORG-spine.003', 'spine.003',
        'chestLower', 'chest', 'spine2'
    ],
    'neck': [
        'mixamorig:Neck', 'mixamorig_Neck',
        'ORG-spine.004', 'spine.004', 'neck',
        'neckLower'
    ],
    'head': [
        'mixamorig:Head', 'mixamorig_Head',
        'ORG-spine.005', 'spine.005', 'face', 'head'
    ],
    
    'left_shoulder': [
        'mixamorig:LeftShoulder', 'mixamorig_LeftShoulder',
        'ORG-shoulder.L', 'shoulder.L',
        'lCollar', 'lShldr', 'lClavicle'
    ],
    'left_arm': [
        'mixamorig:LeftArm', 'mixamorig_LeftArm',
        'ORG-upper_arm.L', 'upper_arm.L',
        'lShldrBend', 'lShldrTwist', 'lArm', 'UpperArm.L'
    ],
    'left_elbow': [
        'mixamorig:LeftForeArm', 'mixamorig_LeftForeArm',
        'ORG-forearm.L', 'forearm.L',
        'lForearmBend', 'lElbow', 'lForeArm', 'LowerArm.L'
    ],
    'left_wrist': [
        'mixamorig:LeftHand', 'mixamorig_LeftHand',
        'ORG-hand.L', 'hand.L',
        'lHand', 'lWrist', 'Hand.L'
    ],
    
    'right_shoulder': [
        'mixamorig:RightShoulder', 'mixamorig_RightShoulder',
        'ORG-shoulder.R', 'shoulder.R',
        'rCollar', 'rShldr', 'rClavicle'
    ],
    'right_arm': [
        'mixamorig:RightArm', 'mixamorig_RightArm',
        'ORG-upper_arm.R', 'upper_arm.R',
        'rShldrBend', 'rShldrTwist', 'rArm', 'UpperArm.R'
    ],
    'right_elbow': [
        'mixamorig:RightForeArm', 'mixamorig_RightForeArm',
        'ORG-forearm.R', 'forearm.R',
        'rForearmBend', 'rElbow', 'rForeArm', 'LowerArm.R'
    ],
    'right_wrist': [
        'mixamorig:RightHand', 'mixamorig_RightHand',
        'ORG-hand.R', 'hand.R',
        'rHand', 'rWrist', 'Hand.R'
    ],
    
    'left_leg': [
        'mixamorig:LeftUpLeg', 'mixamorig_LeftUpLeg',
        'ORG-thigh.L', 'thigh.L',
        'lThighBend', 'lThigh', 'UpperLeg.L',
        'LeftUpperLeg'
    ],
    'left_knee': [
        'mixamorig:LeftLeg', 'mixamorig_LeftLeg',
        'ORG-shin.L', 'shin.L',
        'lShin', 'lKnee', 'lLeg', 'LowerLeg.L'
    ],
    'left_ankle': [
        'mixamorig:LeftFoot', 'mixamorig_LeftFoot',
        'ORG-foot.L', 'foot.L',
        'lFoot', 'lAnkle', 'Foot.L'
    ],
    'left_toe': [
        'mixamorig:LeftToeBase', 'mixamorig_LeftToeBase',
        'ORG-toe.L', 'toe.L',
        'lToe', 'Toes.L', 'LeftToeBase'
    ],
    
    'right_leg': [
        'mixamorig:RightUpLeg', 'mixamorig_RightUpLeg',
        'ORG-thigh.R', 'thigh.R',
        'rThighBend', 'rThigh', 'UpperLeg.R',
        'RightUpperLeg'
    ],
    'right_knee': [
        'mixamorig:RightLeg', 'mixamorig_RightLeg',
        'ORG-shin.R', 'shin.R',
        'rShin', 'rKnee', 'rLeg', 'LowerLeg.R'
    ],
    'right_ankle': [
        'mixamorig:RightFoot', 'mixamorig_RightFoot',
        'ORG-foot.R', 'foot.R',
        'rFoot', 'rAnkle', 'Foot.R'
    ],
    'right_toe': [
        'mixamorig:RightToeBase', 'mixamorig_RightToeBase',
        'ORG-toe.R', 'toe.R',
        'rToe', 'Toes.R', 'RightToeBase'
    ],
    
    'thumb_1_l': [
        'mixamorig:LeftHandThumb1', 'mixamorig_LeftHandThumb1',
        'ORG-thumb.01.L', 'thumb.01.L',
        'lThumb1'
    ],
    'thumb_2_l': [
        'mixamorig:LeftHandThumb2', 'mixamorig_LeftHandThumb2',
        'ORG-thumb.02.L', 'thumb.02.L',
        'lThumb2'
    ],
    'thumb_3_l': [
        'mixamorig:LeftHandThumb3', 'mixamorig_LeftHandThumb3',
        'ORG-thumb.03.L', 'thumb.03.L',
        'lThumb3'
    ],
    
    'index_1_l': [
        'mixamorig:LeftHandIndex1', 'mixamorig_LeftHandIndex1',
        'ORG-f_index.01.L', 'f_index.01.L',
        'lIndex1'
    ],
    'index_2_l': [
        'mixamorig:LeftHandIndex2', 'mixamorig_LeftHandIndex2',
        'ORG-f_index.02.L', 'f_index.02.L',
        'lIndex2'
    ],
    'index_3_l': [
        'mixamorig:LeftHandIndex3', 'mixamorig_LeftHandIndex3',
        'ORG-f_index.03.L', 'f_index.03.L',
        'lIndex3'
    ],
    
    'middle_1_l': [
        'mixamorig:LeftHandMiddle1', 'mixamorig_LeftHandMiddle1',
        'ORG-f_middle.01.L', 'f_middle.01.L',
        'lMid1'
    ],
    'middle_2_l': [
        'mixamorig:LeftHandMiddle2', 'mixamorig_LeftHandMiddle2',
        'ORG-f_middle.02.L', 'f_middle.02.L',
        'lMid2'
    ],
    'middle_3_l': [
        'mixamorig:LeftHandMiddle3', 'mixamorig_LeftHandMiddle3',
        'ORG-f_middle.03.L', 'f_middle.03.L',
        'lMid3'
    ],
    
    'ring_1_l': [
        'mixamorig:LeftHandRing1', 'mixamorig_LeftHandRing1',
        'ORG-f_ring.01.L', 'f_ring.01.L',
        'lRing1'
    ],
    'ring_2_l': [
        'mixamorig:LeftHandRing2', 'mixamorig_LeftHandRing2',
        'ORG-f_ring.02.L', 'f_ring.02.L',
        'lRing2'
    ],
    'ring_3_l': [
        'mixamorig:LeftHandRing3', 'mixamorig_LeftHandRing3',
        'ORG-f_ring.03.L', 'f_ring.03.L',
        'lRing3'
    ],
    
    'pinkie_1_l': [
        'mixamorig:LeftHandPinky1', 'mixamorig_LeftHandPinky1',
        'ORG-f_pinky.01.L', 'f_pinky.01.L',
        'lPinky1'
    ],
    'pinkie_2_l': [
        'mixamorig:LeftHandPinky2', 'mixamorig_LeftHandPinky2',
        'ORG-f_pinky.02.L', 'f_pinky.02.L',
        'lPinky2'
    ],
    'pinkie_3_l': [
        'mixamorig:LeftHandPinky3', 'mixamorig_LeftHandPinky3',
        'ORG-f_pinky.03.L', 'f_pinky.03.L',
        'lPinky3'
    ],
    
    'thumb_1_r': [
        'mixamorig:RightHandThumb1', 'mixamorig_RightHandThumb1',
        'ORG-thumb.01.R', 'thumb.01.R',
        'rThumb1'
    ],
    'thumb_2_r': [
        'mixamorig:RightHandThumb2', 'mixamorig_RightHandThumb2',
        'ORG-thumb.02.R', 'thumb.02.R',
        'rThumb2'
    ],
    'thumb_3_r': [
        'mixamorig:RightHandThumb3', 'mixamorig_RightHandThumb3',
        'ORG-thumb.03.R', 'thumb.03.R',
        'rThumb3'
    ],
    
    'index_1_r': [
        'mixamorig:RightHandIndex1', 'mixamorig_RightHandIndex1',
        'ORG-f_index.01.R', 'f_index.01.R',
        'rIndex1'
    ],
    'index_2_r': [
        'mixamorig:RightHandIndex2', 'mixamorig_RightHandIndex2',
        'ORG-f_index.02.R', 'f_index.02.R',
        'rIndex2'
    ],
    'index_3_r': [
        'mixamorig:RightHandIndex3', 'mixamorig_RightHandIndex3',
        'ORG-f_index.03.R', 'f_index.03.R',
        'rIndex3'
    ],
    
    'middle_1_r': [
        'mixamorig:RightHandMiddle1', 'mixamorig_RightHandMiddle1',
        'ORG-f_middle.01.R', 'f_middle.01.R',
        'rMid1'
    ],
    'middle_2_r': [
        'mixamorig:RightHandMiddle2', 'mixamorig_RightHandMiddle2',
        'ORG-f_middle.02.R', 'f_middle.02.R',
        'rMid2'
    ],
    'middle_3_r': [
        'mixamorig:RightHandMiddle3', 'mixamorig_RightHandMiddle3',
        'ORG-f_middle.03.R', 'f_middle.03.R',
        'rMid3'
    ],
    
    'ring_1_r': [
        'mixamorig:RightHandRing1', 'mixamorig_RightHandRing1',
        'ORG-f_ring.01.R', 'f_ring.01.R',
        'rRing1'
    ],
    'ring_2_r': [
        'mixamorig:RightHandRing2', 'mixamorig_RightHandRing2',
        'ORG-f_ring.02.R', 'f_ring.02.R',
        'rRing2'
    ],
    'ring_3_r': [
        'mixamorig:RightHandRing3', 'mixamorig_RightHandRing3',
        'ORG-f_ring.03.R', 'f_ring.03.R',
        'rRing3'
    ],
    
    'pinkie_1_r': [
        'mixamorig:RightHandPinky1', 'mixamorig_RightHandPinky1',
        'ORG-f_pinky.01.R', 'f_pinky.01.R',
        'rPinky1'
    ],
    'pinkie_2_r': [
        'mixamorig:RightHandPinky2', 'mixamorig_RightHandPinky2',
        'ORG-f_pinky.02.R', 'f_pinky.02.R',
        'rPinky2'
    ],
    'pinkie_3_r': [
        'mixamorig:RightHandPinky3', 'mixamorig_RightHandPinky3',
        'ORG-f_pinky.03.R', 'f_pinky.03.R',
        'rPinky3'
    ],
    
    'left_eye': [
        'mixamorig:LeftEye', 'mixamorig_LeftEye',
        'ORG-eye.L', 'eye.L',
        'lEye', 'Eye.L'
    ],
    'right_eye': [
        'mixamorig:RightEye', 'mixamorig_RightEye',
        'ORG-eye.R', 'eye.R',
        'rEye', 'Eye.R'
    ]
}

for category, mappings in non_standard_mappings.items():
    if category in bone_names:
        bone_names[category].extend(mappings)
    else:
        bone_names[category] = mappings


# Since data set is very poisoned by bone names that aren't simplified (And as such will not map properly using the function) we will just force convert them to the proper format at the end here. - @989onan
for standard, mappings in bone_names.items():
    for i in range(len(mappings)):
        bone_names[standard][i] = simplify_bonename(mappings[i])

# Create reverse lookup dictionary (conversion/translation)
reverse_bone_lookup = {}
for preferred_name, name_list in bone_names.items():
    for name in name_list:
        reverse_bone_lookup[name] = preferred_name
