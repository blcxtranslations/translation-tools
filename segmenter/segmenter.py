#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Converts a text file or commandline input of Chinese
To definitions and pinyin for easier translation
Custom dictionaries supported but have to added manually
"""

import sys
import marisa_trie


class ChineseDict(object):
    """
    Creates a dictionary with a trie for fast lookup,
    a dict for actual definitions,
    and a dict for pinyin of words
    """
    def __init__(self):
        self.dict = {}
        self.tone = []
        self.trie = []
        self.longest = 0

        self.init_cedict()
        self.init_cust_dict()
        self.trie = marisa_trie.Trie(self.trie)

        self.longest += 1

    def init_cedict(self):
        """
        Adds cedict
        """
        dict_file = open('cedict_ts.u8', 'r').read()
        dict_file = dict_file.split('\n')
        dict_file = [entry for entry in dict_file if len(entry) > 0]
        dict_file = [entry for entry in dict_file if not entry.startswith('#')]
        for line in dict_file:
            words = line.split(' ')
            sound = line.split('[')[1].split(']')[0]
            line0 = words[0].decode('utf-8')
            line1 = words[1].decode('utf-8')
            self.trie.append(line0) # Traditional
            self.trie.append(line1) # Traditional
            self.dict[line0] = sound
            self.dict[line1] = sound
            self.calc_longest(len(line0))
            self.calc_longest(len(line1))

    def init_cust_dict(self):
        """
        Adds the user defined custom dictionary
        Assuming it is a csv with seperator ", "
        Assuming if only two items, then pinyin is missing
        """
        dict_file = open('custom.dict', 'r').read()
        dict_file = dict_file.split('\n')
        dict_file = [entry for entry in dict_file if len(entry) > 0]
        for line in dict_file:
            line = line.split(', ')
            word = line[0].decode('utf-8')
            defn = line[1]
            self.trie.append(word) # Traditional
            self.dict[word] = defn
            self.calc_longest(len(word))

    def calc_longest(self, length):
        """
        Updates the longest string every time
        Keep track so that we don't waste time looking for longer words
        """
        if length > self.longest:
            self.longest = length

    def findword(self, word):
        """
        Return the definition and pinyin of word
        """
        if word in self.trie:
            return [self.dict[word], None]
        else:
            return None


class Segmenter(object):
    """
    Given a file (stdin) in Chinese
    Segment using the dictionary
    Write out to file (stdout)
    """
    def __init__(self):
        self.dict = ChineseDict()
        self.line_width = 50

    def process(self, infile=None, outfile=None):
        """
        Break the article into pieces and segment individually
        """
        if infile:
            file_handle = open(infile, 'r')
        else:
            file_handle = sys.stdin
        contents = file_handle.read().split('\n')
        file_handle.close()
        contents = [entry for entry in contents if len(entry) > 0]
        segments = ""
        for sentence in contents:
            segment = self.segment(sentence)
            segments += self.construct(sentence, segment)
        if outfile:
            file_handle = open(outfile, 'w')
        else:
            file_handle = sys.stdout
        file_handle.write(segments.encode('utf-8'))
        file_handle.close()

    def construct(self, sentence, segment):
        """
        Concatenate the original sentence with the segment, add seperators
        """
        result = ""
        result += '=' * self.line_width + '\n'
        result += sentence.decode('utf-8') + '\n'
        result += '-' * self.line_width+ '\n'
        result += segment + '\n'
        result += '=' * self.line_width + '\n\n'
        return result

    def segment(self, segment):
        """
        Segment the sentence by searching for the largest fit
        """
        pos = 0
        line = ""
        words = ""
        defns = ""
        while pos < len(segment):
            chars = range(1, self.dict.longest)
            chars.reverse()
            found = False
            for i in chars:
                word = segment[pos : pos + i * 3]
                word = word.decode('utf-8')
                found = self.dict.findword(word)
                if found:
                    defn = found[0]
                    # tone = found[1]
                    defn += ' | '
                    factor_cur = len(defns) / self.line_width
                    factor_new = (len(defns) + len(defn)) / self.line_width
                    if factor_cur < factor_new:
                        line += words + '\n' + defns + '\n'
                        defns = ""
                        words = ""
                    words += word + (len(defn) - len(word) * 2) * ' '
                    defns += defn
                    # defns.append(defn)
                    pos += i * 3
                    break
            if not found:
                pos += 3

        line += words + '\n' + defns + '\n'
        return line[:-1]



if __name__ == "__main__":
    SEGMENTER = Segmenter()
    ARGC = len(sys.argv)
    if ARGC == 3:
        SEGMENTER.process(sys.argv[1], sys.argv[2])
    elif ARGC == 2:
        SEGMENTER.process(sys.argv[1])
    else:
        SEGMENTER.process()
