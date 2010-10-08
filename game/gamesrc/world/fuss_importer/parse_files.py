#!/usr/bin/env python

from django.conf import settings

# SmaugFUSS keyed area files are a mess, turn them to xml
import xml.dom.minidom
import os.path

element_defs = {}
element_defs["#ROOM"] = ("room", "#ENDROOM")
element_defs["#FUSSAREA"] = ("area", "#ENDAREA")
element_defs["#AREADATA"] = ("area_data", "#ENDAREADATA")
element_defs["#EXDESC"] = ("exdesc", "#ENDEXDESC")
element_defs["#MOBILE"] = ("mobile", "#ENDMOBILE")
element_defs["#MUDPROG"] = ("mudprog", "#ENDPROG")
element_defs["#OBJECT"] = ("object", "#ENDOBJECT")
element_defs["#EXIT"] = ("exit", "#ENDEXIT")
element_defs["#HELPS"] = ("help", "#$")
element_defs["#PLAYER"] = ("player", "End")
element_defs["#CLAN"] = ("clan", "End")
element_defs["#COLORTHEME"] = ("colortheme", "End")
element_defs["#SKILL"] = ("skill", "#ENDSKILL")
element_defs["#COMMAND"] = ("command", "#ENDCOMMAND")
element_defs["#HERB"] = ("herb", "#ENDHERB")
element_defs["#LIQUID"] = ("liquid", "#ENDLIQUID")
element_defs["#SOCIAL"] = ("social", "#ENDSOCIAL")
element_defs["#SYSTEM"] = ("system", "#ENDSYSTEM")
element_defs["#TIME"] = ("time", "#ENDTIME")

key_defs = {}

def log(txt):
    #print txt
    pass

multivalued = []
multivalued.append(("exit", "Reset"))
multivalued.append(("room", "Reset"))
multivalued.append(("object", "Affect"))
multivalued.append(("herb", "Affect"))
multivalued.append(("race", "WhereName"))
multivalued.append(("player", "Spell"))
multivalued.append(("player", "Tongue"))
multivalued.append(("player", "Weapon"))
multivalued.append(("player", "Skill"))
multivalued.append(("class", "Skill"))
multivalued.append(("class", "Title"))
multivalued.append(("skill", "Affect"))

class KeyFile:
    def __init__(self, filename, root_element = None, sub_root_element_name=None):
	f = open(os.path.sep.join([FOREIGN_MUD_ROOT, filename]))
        self.buffer = f.read()
	f.close()
        expected_tag_stack = []
        element_stack = [root_element]

        if sub_root_element_name:
            sub_root_element = doc.createElement(sub_root_element_name)
            element_name = sub_root_element_name
            element_stack[-1].appendChild(sub_root_element)
            element_stack.append(sub_root_element)
            expected_tag_stack.append("END")
        while self.buffer:
            word = self.readword()
            if word == "#END" or word == "End" or (expected_tag_stack and expected_tag_stack[-1] == word):
                if expected_tag_stack:
	            expected_tag_stack.pop()
	            element_stack.pop()
            elif word.startswith("*"):
                # comment
                pass
	    elif word.startswith("#"):
                log("TS: %s" % expected_tag_stack)
                if word == "#HELPS":
                    while self.buffer:
                        help_level = self.readword()
                        help_keywords = self.readstring()
                        help_content = self.readstring()
                        if help_keywords == "$":
                            break
			mv_tags = element_stack[-1].getElementsByTagName("help")
			if not mv_tags:
			    mv_tag = doc.createElement("help")
			    element_stack[-1].appendChild(mv_tag)
			else:
			    mv_tag = mv_tags[0]
			val_tag = doc.createElement("help_entry")
                        val_tag.setAttribute("keywords", help_keywords)
                        val_tag.setAttribute("level", help_level)
			val_tag.appendChild(doc.createTextNode(help_content))
			mv_tag.appendChild(val_tag)
		else:
		    element_name, element_endtag = element_defs[word]
		    new_el = doc.createElement(element_name)
		    element_stack[-1].appendChild(new_el)
		    element_stack.append(new_el)
		    expected_tag_stack.append(element_endtag)
	    else:
                if word == "DefPos":
                    word = "Defpos"
                elif word == "Hpmin":
                    word = "HpMin"
                elif word == "Hpmax":
                    word = "HpMax"
                elif word == "Expbase":
                    word = "ExpBase"
                elif word == "Thirst_mod":
                    word = "Thirst_Mod"
                try:
                    key_type = key_defs[element_name][word]
                except KeyError:
                    log("Dont know what type of data %s is for %s" % (word,element_name))
                    log("rest of buffer: %s %s" % (word, self.buffer[:100]))
                    assert(False)
                if key_type == "string" or key_type == "string_nohash":
                    val = self.readstring()
                elif key_type == "str_dup":
                    val = self.readbitvector()
                elif key_type == "bitvector":
                    val = self.readbitvector()
                elif key_type == "number":
                    val = self.readword()
                elif key_type == "title":
                    val = self.readtitle()
                else:
                    log("Hrmm, don't know how to handle field type %s for %s" % (key_type,word))
                    assert(False)
                log("ATT %s,%s,%s---" % (word, key_type, val))
		if (element_name, word) in multivalued:
		    word_plural = "%ss" % word
		    mv_tags = element_stack[-1].getElementsByTagName(word_plural)
		    if not mv_tags:
			mv_tag = doc.createElement(word_plural)
			element_stack[-1].appendChild(mv_tag)
		    else:
			mv_tag = mv_tags[0]
		    val_tag = doc.createElement(word)
		    val_tag.appendChild(doc.createTextNode(val))
		    mv_tag.appendChild(val_tag)
                else:
		    if element_stack[-1].getAttribute(word):
			log("%s on %s is not multivalued!" % (word, element_name))
			assert(False)
		    else:
                        element_stack[-1].setAttribute(word, val)
    def readbitvector(self):
         self.buffer = self.buffer.lstrip()
         b = ""
         for c in self.buffer:
             if not c.isspace() or c == " ":
                 b += c
             else:
                 break
         self.buffer = self.buffer[len(b)+1:].lstrip()
	 return b
    def readword(self):
         self.buffer = self.buffer.lstrip()
         b = ""
         for c in self.buffer:
             if not c.isspace():
                 b += c
             else:
                 break
         self.buffer = self.buffer[len(b)+1:].lstrip()
	 return b
    def readstring(self):
         b = ""
         for c in self.buffer:
             if not c == "~":
                 b += c
             else:
                 break
         self.buffer = self.buffer[len(b)+1:].lstrip()
	 return b
    def readtitle(self):
         self.buffer.lstrip()
         a = self.readstring()
         b = self.readstring()
         return "%s~%s" % (a,b)

def import_from_list(dir_name, list_name, root_node, collection_node_name, sub_root_element_name = None):
    collection_node = doc.createElement(collection_node_name)
    root_node.appendChild(collection_node)
    f = open(os.path.sep.join([FOREIGN_MUD_ROOT, dir_name, list_name]))
    buf = f.read()
    f.close()
    for line in buf.split("\n"):
	if line.strip() == "$":
	    break
	else:
            KeyFile(os.path.sep.join([dir_name, line.strip()]), collection_node, sub_root_element_name)

FOREIGN_MUD_ROOT = None
doc = xml.dom.minidom.Document()

def parse_mud_root_to_dom():
    key_defs_file = open(os.path.sep.join([settings.GAME_DIR, "world", "fuss_importer", "key_data_types.txt"]))
    kdf = key_defs_file.read().strip()
    key_defs_file.close()

    for line in kdf.split("\n"):
        a,b,c = line.split(" ")
        key_defs.setdefault(b, {})[a]=c


    world = doc.createElement("world")
    doc.appendChild(world)
    import_from_list("area","area.lst", world, "areas")
    import_from_list("races","race.lst", world, "races", sub_root_element_name="race")
    import_from_list("clans","clan.lst", world, "clans")
    import_from_list("classes","class.lst", world, "classes", sub_root_element_name="class")
    KeyFile(os.path.sep.join(["player","a","Admin"]), world, sub_root_element_name="player_record")
    color_schemes = doc.createElement("color_schemes")
    world.appendChild(color_schemes)
    KeyFile(os.path.sep.join(["color","smaug"]), color_schemes)
    KeyFile(os.path.sep.join(["color","default"]), color_schemes)
    KeyFile(os.path.sep.join(["color","AFK"]), color_schemes)
    KeyFile(os.path.sep.join(["system","skills.dat"]), world, sub_root_element_name="skills")
    KeyFile(os.path.sep.join(["system","commands.dat"]), world, sub_root_element_name="commands")
    KeyFile(os.path.sep.join(["system","herbs.dat"]), world, sub_root_element_name="herbs")
    KeyFile(os.path.sep.join(["system","liquids.dat"]), world, sub_root_element_name="liquids")
    KeyFile(os.path.sep.join(["system","socials.dat"]), world, sub_root_element_name="socials")
    KeyFile(os.path.sep.join(["system","sysdata.dat"]), world)
    KeyFile(os.path.sep.join(["system","time.dat"]), world, sub_root_element_name="time")
    return doc

if __name__ == "__main__":
    FOREIGN_MUD_ROOT = "."
    parse_mud_root_to_dom()
    print doc.toprettyxml()
