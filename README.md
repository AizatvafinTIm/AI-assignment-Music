# Assignment: Accompaniment Generation


# Introduction

In this assignment I need to make accompaniments to the given melodies. But there was some restrictions that my program had to follow. We can generate chords that have only three notes and also use these type of chords:

- major and minor triads
- first and second inversions of major and minor triads
- diminished chords (DIM)
- suspended second chords (SUS2)
- suspended fourth chords (SUS4)

So, after getting some improvements program should get the most relevant chord accompaniment in term of score that gives fitness function.

# Algorithm overview

First of all we have to decide which object will be considered as figure of exploration. I’ve chosen to consider whole line of chords as it(accompaniment). So, my program did the following:

- Generated initial population of individuals randomly(almost)
- Repeated as many times as there were epochs
    1. Select individuals for reproduction
    2. Let them produce offsprings
    3. Mutate these offsprings
- Pick the individual with the highest fitness as solution

## Some details

In this part of repot was included such details as **Representation.**

Class **Evolution** takes how many epoch should be in our world, pool_size how many individuals in the first generation, and some params to create them.

```python
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
        self.individuals = [Individual(notes_from_track, key, octave, quater) for _ in range(pool_size)
```

Class **Individual** takes notes_from_track. This param is required to make appropriate sound.

Key is required to understand in which tonality should be our chords.

Octave is required  to understand in which octave we want hear our accompaniment.

Quater is required to take better timings for chords.

## Small description of generating individual

When Individual create chord of accompaniment:

1. Take note from melody
2. Generate all possible pairs of notes from one key
3. Put three note together in all combinations
4. Choose randomly one of them

```python
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
```

# Necessary elements of EA

## Operators

I have used mutate, crossing as separate methods and inside of them I made own **Selection** of individuals.

**Mutating** is needed to mutate our offspring after his birth. But I gave for this event some probability to happen because it just pick ups more appropriate chords for the individual and seems as cheat(a little bit).

**Crossing** is needed to cross some individuals which are taken from their population.There is simple logic, just take two random parent from individuals and let them produce offspring and it derived 1st half of accompaniment from father and the 2nd half form mother. Then parent and mother die...

## Fitness function

This function is needed to give some score to particular individual of one population.

It based on 3 things. If it see that chord is triad, function gives 3 points to one chord of individual or if it see that chord is sus2 or sus4, function gives 2 points, otherwise nothing. 

```python
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
```

## Some other params

**Number of generations** could be any, but in my program is 1000.

**Population size** also could be any, but there is 100.

There is no additional **stopping criteria** only genetic algorithm will stop when number of generations achieve his border.

# Requirements

```python
pip install pretty_midi
```

# Conclusion

The goal is to make accompaniment to the given melodies. Actually, sound of some music is not gorgeous as expected because of my knowledge in Music Theory, but anyway for me it’s fine:). I’ve implemented genetic algorithm which is able to evolve, reproduce offspring and mutate and come to the good melody!
