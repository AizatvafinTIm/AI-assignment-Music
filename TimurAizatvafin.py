import pretty_midi
from pretty_midi import Note
from random import randint
from itertools import permutations
from random import choice


# Calculate octave of give melody. Takes one .mid file
def get_octave(mid):
    unique_note = set(mid.instruments[0].notes[i].pitch for i in range(len(mid.instruments[0].notes)))
    mean_note = (min(unique_note))
    return pretty_midi.note_number_to_name(mean_note)[-1]


# Generating all possible keys by using formula
def creating_keys(notes, formula):
    keys = {}
    for i in range(len(notes)):
        main = i
        key = [notes[i]]
        for j in formula:
            key.append(notes[(i + j) % 12])
            i += j
        key.pop(-1)
        keys[notes[main]] = key
    return keys


# Choosing the most relevant key for our accompaniment
def get_key(keys, pitches):
    # Getting name of notes from melody
    symbol_notes = [pretty_midi.note_number_to_name(pitches[i])[0:-1] for i in range(len(pitches))]
    # Create unique notes which was used
    symbol_notes = set(symbol_notes)
    res = []
    max_corr = 0
    for key in keys.values():
        temp = symbol_notes.intersection(set(key))
        # Which key has the biggest intersection with notes from melody, would be key of accompaniment
        if len(temp) > max_corr:
            max_corr = len(temp)
            res = key
    return res


# Getting individual and gives the score to him
def fitness(x):
    # Getting all chords from accompaniment
    chords = x.numbers_to_symbols()
    res = 0
    for chord in chords:
        comb = []
        for note in chord:
            comb.append(x.key.index(note))
        comb.sort()
        check = comb.copy()
        number = comb[0]
        comb = list(map(lambda x: x - number, check))
        # Checking whether this chord is sus4 or not
        if comb == [0, 3, 4]:
            if number in [0, 2, 4]:
                res += 2
        # Checking whether this chord is sus2 or not
        if comb == [0, 1, 4]:
            if number in [0, 3, 5]:
                res += 2
        # Checking whether this chord is triad or not
        if comb == [0, 2, 4] or comb == [0, 3, 5] or comb == [0, 2, 5]:
            res += 3

    return res


# Checks all chord how they are relevant to the melody
def checking_relevance(x):
    triads = x.generate_triads()
    chords = x.numbers_to_symbols()
    res = 0
    result = []
    # Checking for triads
    for chord in chords:
        for triad in triads:
            if len(triad.intersection(chord)) == len(triad):
                res += 1
                result.append(1)
                break
            else:
                result.append(0)

    return res, result


# Individual is kind of person of our population. It creates and holds one accompaniment to the melody
class Individual:
    # Constructor
    def __init__(self, notes_from_track, key, octave, quarter):
        # Holds chords [[Note(...), Note(...), Note(...)], [...],...]
        self.individual = []
        # To catch timings float
        self.quarter = quarter
        # To keep track the fact that our chord consist this note of melody. So, I guarantee that chord will consist
        # one note from melody
        self.notes_from_track = notes_from_track
        # Key of melody
        self.key = key
        # Octave of future accompaniment
        self.octave = octave
        # To give timings for chords
        self.temp = self.quarter
        self.played = False
        self.main_notes = []
        # There is a creation of accompaniment
        self.initialization()

    # Here is initialization of accompaniment occurs
    def initialization(self):
        # Iterate through all notes
        for i in range(len(self.notes_from_track)):
            note = self.notes_from_track[i]
            # Condition to give a timing to chord
            if note.start < self.temp:
                if not self.played:
                    # Creating Chord
                    symbol_pitch = pretty_midi.note_number_to_name(note.pitch)[0:-1]  # Symbol
                    self.chord_pitches = choice(self.generating_relevant_chords(symbol_pitch))
                    self.chord = []
                    self.chord.append(Note(velocity=note.velocity,
                                           pitch=pretty_midi.note_name_to_number(
                                               f'{self.chord_pitches[0]}{int(self.octave) - 1}'),
                                           start=self.temp - self.quarter,
                                           end=self.temp))
                    self.chord.append(Note(velocity=note.velocity,
                                           pitch=pretty_midi.note_name_to_number(
                                               f'{self.chord_pitches[1]}{int(self.octave) - 1}'),
                                           start=self.temp - self.quarter,
                                           end=self.temp))
                    self.chord.append(Note(velocity=note.velocity,
                                           pitch=pretty_midi.note_name_to_number(
                                               f'{self.chord_pitches[2]}{int(self.octave) - 1}'),
                                           start=self.temp - self.quarter,
                                           end=self.temp))
                    self.individual.append(self.chord)
                    self.main_notes.append(symbol_pitch)
                    self.played = True
            else:
                self.played = False
                # Reaching right timing for chord
                while self.temp < note.start:
                    self.temp += self.quarter
                # Creating chord
                symbol_pitch = pretty_midi.note_number_to_name(note.pitch)[0:-1]
                self.chord_pitches = choice(self.generating_relevant_chords(symbol_pitch))
                self.chord = []
                self.chord.append(Note(velocity=note.velocity,
                                       pitch=pretty_midi.note_name_to_number(
                                           f'{self.chord_pitches[0]}{int(self.octave) - 1}'),
                                       start=self.temp - self.quarter,
                                       end=self.temp))
                self.chord.append(Note(velocity=note.velocity,
                                       pitch=pretty_midi.note_name_to_number(
                                           f'{self.chord_pitches[1]}{int(self.octave) - 1}'),
                                       start=self.temp - self.quarter,
                                       end=self.temp))
                self.chord.append(Note(velocity=note.velocity,
                                       pitch=pretty_midi.note_name_to_number(
                                           f'{self.chord_pitches[2]}{int(self.octave) - 1}'),
                                       start=self.temp - self.quarter,
                                       end=self.temp))
                self.individual.append(self.chord)
                self.main_notes.append(symbol_pitch)
                self.played = True

    # Here is a generating of any type of chord but with 3 three notes where one of them from melody
    def generating_relevant_chords(self, symbol_pitch):
        self.current_combs = []
        temp_key = self.key.copy()
        temp_key.remove(symbol_pitch)
        self.current_key = list(permutations(temp_key, 2))
        for case in self.current_key:
            temp = [elem for elem in case]
            temp.insert(0, symbol_pitch)
            self.current_combs.append(temp.copy())
            temp.pop(0)
            temp.insert(1, symbol_pitch)
            self.current_combs.append(temp.copy())
            temp.pop(1)
            temp.append(symbol_pitch)
            self.current_combs.append(temp.copy())
            temp.pop(-1)
        return self.current_combs

    # Generating triads
    def generate_triads(self):
        triad = [0, 2, 4]
        triads = []
        for i in range(len(self.key)):
            a = set()
            for j in triad:
                a.add(self.key[(i + j) % 7])
            triads.append(a)
        return triads

    # Converting accompaniment to chars
    def numbers_to_symbols(self):
        return [self.chord_to_symbols(chord) for chord in self.individual]

    # Converting chord to chars
    def chord_to_symbols(self, chord):
        return set(pretty_midi.note_number_to_name(note.pitch)[0:-1] for note in chord)

    # Mutating of accompaniment. It sees some problems of accompaniment and trying to fix them if it can
    def mutating(self, result):
        # Mutating is not always may occur
        if randint(1, 100) > 98:
            triads = self.generate_triads()
            main_note_idx = 0
            new_individual = []
            # Iterate over accompaniment and if it sees that one of chords is failed just trying to fix it by
            # selecting another
            for chord, score in zip(self.individual, result):
                if score == 0:
                    chord_symbols = self.chord_to_symbols(chord)
                    main_note_pitch = pretty_midi.note_name_to_number(
                        f'{self.main_notes[main_note_idx]}{int(self.octave) - 1}')
                    note = None
                    for ch_note in chord:
                        if ch_note.pitch == main_note_pitch:
                            note = ch_note
                    for triad in triads:
                        if len(triad.intersection(chord_symbols)) == 2 and self.main_notes[main_note_idx] in triad:
                            triad = list(triad)
                            # Creating new chord
                            self.chord = []
                            self.chord.append(Note(velocity=note.velocity,
                                                   pitch=pretty_midi.note_name_to_number(
                                                       f'{triad[0]}{int(self.octave) - 1}'),
                                                   start=note.start,
                                                   end=note.end))
                            self.chord.append(Note(velocity=note.velocity,
                                                   pitch=pretty_midi.note_name_to_number(
                                                       f'{triad[1]}{int(self.octave) - 1}'),
                                                   start=note.start,
                                                   end=note.end))
                            self.chord.append(Note(velocity=note.velocity,
                                                   pitch=pretty_midi.note_name_to_number(
                                                       f'{triad[2]}{int(self.octave) - 1}'),
                                                   start=note.start,
                                                   end=note.end))
                    new_individual.append(self.chord)
                    break
                main_note_idx += 1

            # Updating accompaniment
            self.individual = new_individual


# Evolution makes simulation of evolution
class Evolution:
    # Constructor
    def __init__(self, epoches, pool_size, notes_from_track, key, octave, quater):
        self.epoches = epoches
        self.pool_size = pool_size
        self.notes_from_track = notes_from_track
        self.key = key
        self.octave = octave
        self.quater = quater
        self.individuals = [Individual(notes_from_track, key, octave, quater) for _ in range(pool_size)]

    # Run the world
    def run(self):
        while self.epoches > 0:
            self.individuals.sort(key=lambda x: fitness(x))
            # Getting parents
            self.parents = self.get_parents()
            # Making crossing
            for i, j in zip(self.parents['fathers'], self.parents['mothers']):
                off1, off2 = self.crossing(self.individuals[i], self.individuals[j])
                self.replace_parents(i, j, off1, off2)
                # Making mutating
                off1.mutating(checking_relevance(off1))
                off2.mutating(checking_relevance(off2))
            # Decreasing number of generations
            self.epoches -= 1

    # Crossing
    def crossing(self, father: Individual, mother: Individual):
        offspring1 = Individual(father.notes_from_track, father.key, father.octave, father.quarter)
        offspring2 = Individual(father.notes_from_track, father.key, father.octave, father.quarter)
        offspring2.chord = father.chord[:len(father.chord) // 2] + mother.chord[len(mother.chord) // 2:]
        return offspring1, offspring2

    # When parents made a reproduction their places will take child
    def replace_parents(self, father, mother, off1, off2):
        self.individuals[father] = off1
        self.individuals[mother] = off2

    # Getting some pairs which are gonna make offsprings
    def get_parents(self):
        self.pairs = randint(0, len(self.individuals) // 4)

        self.parents = {'mothers': [], 'fathers': []}

        i = 0
        while i < self.pairs:
            index = randint(0, len(self.individuals) - 2)
            if index not in self.parents['mothers']:
                self.parents['mothers'].append(index)
            i += 1
        i = 0
        while i < self.pairs:
            index = randint(0, len(self.individuals) - 2)
            if index not in self.parents['mothers'] and index not in self.parents['fathers']:
                self.parents['fathers'].append(index)
            i += 1
        return self.parents


# Which song will be play
input = 'input1.mid'
#input = 'input2.mid'
#input = 'input3.mid'

# Creating a mid file
track = pretty_midi.PrettyMIDI(input)

# Getting quater
quarter = track.get_beats()[1] - track.get_beats()[0]

# Getting notes from given melody
notes_from_track = track.instruments[0].notes

pitch_from_notes = []

# These notes are needed to generate all possible keys
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Formula to generate keys
formula_to_generate_key = [2, 2, 1, 2, 2, 2, 1]

for note in notes_from_track:
    pitch_from_notes.append(note.pitch)

# Creating all possible keys
KEYS = creating_keys(notes, formula_to_generate_key)

# Getting relevant key for melody
key = get_key(KEYS, pitch_from_notes)

# Calling constructor of Evolution
evo = Evolution(epoches=1000, pool_size=100, notes_from_track=notes_from_track, key=key, octave=get_octave(track),
                quater=quarter)

# Running the world
evo.run()

# Getting the bes individual
individ = evo.individuals[-1]

# Completing the task:)
for chord in individ.individual:
    for note in chord:
        track.instruments[0].notes.append(note)
track.write('nice.mid')
