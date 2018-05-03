# -*- coding: UTF-8 -*-
'''
Created on 05.11.2010

@author: SIGIESEC
'''
class DocumentModel(object):
    pass

class FormattingElement(object):
    pass

class Link(FormattingElement):

    def __init__(self, text, link_target):
        self.__text = text
        self.__link_target = link_target
        
    def __eq__(self, other):
        return type(self)==type(other) and \
            self.get_link_target() == other.get_link_target() and \
            self.get_text() == other.get_text()
            
    def __hash__(self):
        return hash((self.__text, hash(self.__link_target)))

    def get_text(self):
        return self.__text


    def get_link_target(self):
        return self.__link_target


    def set_text(self, value):
        self.__text = value


    def set_link_target(self, value):
        self.__link_target = value


    def del_text(self):
        del self.__text


    def del_link_target(self):
        del self.__link_target

    text = property(get_text, set_text, del_text, "Description of the link")
    link_target = property(get_link_target, set_link_target, del_link_target, "Target URL of the Link")

