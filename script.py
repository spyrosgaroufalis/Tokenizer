# strings in python are unicode code points
# ord() returns unicode code point of a character
# ord() cant return unicode code point of a string
# chr() is the opposite of ord() and returns charactes
# thats why we create a list
x = ord('h')
# print(x)
y = "Hello everyone! 2 + 2 = 4 capish?"
z = "Now we need a longer string for further testing, if you are interested then you need to keep reading this script. LLM stands for Long and Large lawn Mower. If you do not believe me then look up: Earh is round with proof."
# print([ord(c) for c in y]) # []-> list


# unicode is always changing, and has large library
# we need stableness, so we use encoding
# we can use UTF-8, UTF-16, UTF-32
# utf8 is more backwards compatible with ascii, and is more efficient for english text
# utf16,32 has more wasteful tokens

# print(list(y.encode("utf-8")))
# print(list(y.encode("utf-16")))
# print(list(y.encode("utf-32")))

# these are byte strings ->
# 256 tokens in utf-8
# we want longer library size 
# we use byte pairing algorithm 
# we compress tokens that are common by replacing them 
# and create a new token for the concatenation 

zenc = z.encode("utf-8") # raw bytes
zlist = list(zenc) # list of bytes
# print(zlist)
# print(zenc)

# Now, we need to create a def for finding pairs and 
# adding new tokens in the library capish?

# Pairs: {(98, 101), (115, 32), (104, 32),
def allpairs(tokens):
    pairs = set()
    for i in range(len(tokens)-1):
        pairs.add((tokens[i], tokens[i+1]))
    return pairs

pairs = allpairs(zlist)
# print(f"Pairs: {pairs}")

# Frequent Pairs: {(111, 119): 2, (32, 119): 2,
def frequent_pairs(tokens):
    counts = {}
    for i in range(len(tokens)-1):
        pair = (tokens[i], tokens[i+1])
        if pair in counts: 
            counts[pair] += 1
        else:
            counts[pair] = 1
    # 2nd step
    # freq = ()
    freq = {}
    for pair in counts:
        if counts[pair] > 1:
            # freq.append(pair)
            freq[pair] = counts[pair]
    return freq

# we can do it with a collections.Counter which creates a dict of counts
# def frequent_pairs(tokens):
#     counts = Counter()
#     for i in range(len(tokens)-1):
#         pair = (tokens[i], tokens[i+1])
#         counts[pair] += 1
#     # filter
#     freq = {pair for pair, count in counts.items() if count > 1}
#     return freq

freqpairs = frequent_pairs(zlist)
# print(f"Frequent Pairs: {freqpairs}")


# now we need to replace the most frequent pair with a new token

top_pair = max(freqpairs, key=freqpairs.get)
print(f"Top Pair: {top_pair} with count {freqpairs[top_pair]}")

def merge_pair(tokens, pair, new_token):
    merged_tokens = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
            merged_tokens.append(new_token)
            i += 2
        else:
            merged_tokens.append(tokens[i])
            i += 1
    return merged_tokens

new_token = max(zlist) + 1 # new token is the next integer after the max byte value
zlist = merge_pair(zlist, top_pair, new_token)
# print(f"New Tokens: {zlist}")
# print(f"New length: {len(zlist)}")
# print(f"Original length: {len(zlist) + freqpairs[top_pair]}") # original length is new length + count of merged pairs

# now we need to iterate this process
# lets say we want to do it 10 times ( 256+10 = 266 tokens)


vocab_size = 266
num_merges = vocab_size - 256 # we start with 256 tokens in utf-8
ids = zlist
for _ in range(num_merges):
    pairs = allpairs(ids)
    freqpairs = frequent_pairs(ids)
    if not freqpairs:
        break
    top_pair = max(freqpairs, key=freqpairs.get)
    new_token = max(ids) + 1
    # print(f"Merging pair: {top_pair} with count {freqpairs[top_pair]} into new token {new_token}")
    ids = merge_pair(ids, top_pair, new_token)
# print(f"Final Tokens: {ids}")
# print(f"Final length: {len(ids)}")

# now we need encoding and decoding functions



# first way: It looks for the first pair in your vocabulary and replaces every instance of it in the entire text. Then it moves to the second pair, then the third, and so on
# flawd bec:
# It assumes the vocab is perfectly ordered by priority. It doesn't check if merging "Pair B" first would have been better than "Pair A" based on the current state of the string.
# It is generally faster but less robust if the vocabulary isn't strictly pre-sorted by the merge rank.

# def encode(text, vocab):
#     tokens = list(text.encode("utf-8"))
#     for pair, token in vocab.items():
#         tokens = merge_pair(tokens, pair, token)
#     return tokens

# more robust way: In every iteration of the while loop, it scans the current tokens to find all possible pairs.
# It then picks the one that has the highest priority (the lowest index/rank in your merges dictionary)
merges = {} # this will store the mapping of pairs to new tokens
def encode(text):
    tokens = list(text.encode("utf-8"))
    while len(tokens) > 1: # because 0 or 1 str breaks the pair
        stats = frequent_pairs(tokens) # get the frequency of pairs in the current tokens
        pair = min(stats, key=lambda p: merges.get(p, float("inf"))) # get the pair with the lowest index in merges (highest priority)
        # key= lambda p is a function that takes a pair p and returns its index in merges if it exists, otherwise returns infinity (so that pairs not in merges are ignored)
        if pair not in merges:
            break
        idx = merges[pair]
        tokens = merge_pair(tokens, pair, idx)
    return tokens


encoded_tokens = encode(z)
print(f"Encoded Tokens: {encoded_tokens}")

# flawd decoding: It assumes that the tokens in the encoded list are in the same order as the merges were applied. 
# If the merges were applied in a different order, it may not decode correctly.

# def decode(tokens, vocab):
#     text = b""
#     for token in tokens:
#         if token in vocab:
#             text += vocab[token]
#         else:
#             text += bytes([token])
#     return text.decode("utf-8")


ids = list(zenc)
vocab = {idx: bytes([idx]) for idx in range(256)} # initial vocab with single byte tokens
for (p0, p1), idx in merges.items():
    vocab[idx] = vocab[p0] + vocab[p1]

def decode(encoded_tokens):
    # given list of ints we return string
    tokens = b"".join(vocab[idx] for idx in encoded_tokens)
    text = tokens.decode("utf-8")
    return text

print(f"Decoded Text: {decode(encoded_tokens)}")