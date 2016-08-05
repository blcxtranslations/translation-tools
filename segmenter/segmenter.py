#!/usr/bin/python
# -*- coding: utf-8 -*-

import marisa_trie


class ChineseDict:
  def __init__(self):
    self.dict = {}
    self.trie = []
    self.longest = 0

    self.init_cedict()
    self.init_cust_dict()
    self.trie = marisa_trie.Trie(self.trie)

    self.longest += 1

  def init_cedict(self):
    dict_file = open('cedict_ts.u8', 'r').read()
    dict_file = dict_file.split('\n')
    dict_file = filter(None, dict_file)
    dict_file = [line for line in dict_file if not line.startswith('#')]
    for line in dict_file:
      words = line.split(' ')
      sound = '[' + line.split('[')[1].split(']')[0] + ']'
      line0 = words[0].decode('utf-8')
      line1 = words[1].decode('utf-8')
      self.trie.append(line0) # Traditional
      self.trie.append(line1) # Traditional
      self.dict[line0] = sound
      self.dict[line1] = sound
      self.calc_longest(len(line0))
      self.calc_longest(len(line1))

  def init_cust_dict(self):
    dict_file = open('custom.dict', 'r').read()
    dict_file = dict_file.split('\n')
    dict_file = filter(None, dict_file)
    for line in dict_file:
      line = line.split(', ')
      word = line[0].decode('utf-8')
      defn = line[1]
      self.trie.append(word) # Traditional
      self.dict[word] = defn
      self.calc_longest(len(word))

  def calc_longest(self, length):
    if length > self.longest:
      self.longest = length

  def longest(self):
    return self.longest

  def findword(self, word):
    if word in self.trie:
      return True, self.dict[word]
    else:
      return False, "Not Found"


class Segmenter:
  def __init__(self):
    self.dict = ChineseDict()

  def process(self, filename):
    file = open(filename, 'r').read()
    file = file.split('\n')
    file = filter(None, file)
    segments = []
    for f in file:
      segments.append(self.segment(f))
    return segments

  def segment(self, file):
    pos = 0
    defns = []
    while pos < len(file):
      chars = range(1, self.dict.longest)
      chars.reverse()
      found = False
      for i in chars:
        word = file[pos : pos + i * 3].decode('utf-8')
        found, defn = self.dict.findword(word)
        if found:
          defns.append(defn)
          pos += i * 3
          break
      if not found:
        pos += 3
    print defns
    return defns


segmenter = Segmenter()
segmenter.process('test.txt')
