#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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
    self.line_width = 50

  def process(self, infile = None, outfile = None):
    if infile:
      file = open(infile, 'r')
    else:
      file = sys.stdin
    contents = file.read().split('\n')
    file.close()
    contents = filter(None, contents)
    segments = ""
    for sentence in contents:
      segment = self.segment(sentence)
      segments += self.construct(sentence, segment)
      break
    if outfile:
      file = open(outfile, 'w')
    else:
      file = sys.stdout
    file.write(segments.encode('utf-8'))
    file.close()

  def construct(self, sentence, segment):
    return '=' * self.line_width + '\n' + sentence.decode('utf-8') + '\n' + '-' * self.line_width+ '\n' + segment + '\n' + '=' * self.line_width + '\n\n'

  def segment(self, file):
    pos = 0
    line = ""
    words = ""
    defns = ""
    while pos < len(file):
      chars = range(1, self.dict.longest)
      chars.reverse()
      found = False
      for i in chars:
        word = file[pos : pos + i * 3]
        word = word.decode('utf-8')
        found, defn = self.dict.findword(word)
        if found:
          defn += ' | '
          if len(defns) / self.line_width < (len(defns) + len(defn)) / self.line_width:
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

    return line[:-1]



if __name__ == "__main__":
  segmenter = Segmenter()
  argc = len(sys.argv)
  if argc == 3:
    segmenter.process(sys.argv[1], sys.argv[2])
  if argc == 2:
    segmenter.process(sys.argv[1])
  else:
    segmenter.process()
