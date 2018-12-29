import copy
import itertools
from music21.note import Note
from music21.pitch import Pitch
from music21.chord import Chord
from music21.roman import RomanNumeral
from music21.key import Key
from music21.clef import BassClef, TrebleClef
from music21.stream import Stream, Part, Score, Measure, Voice

SOPRANO_RANGE = (Pitch('C4'), Pitch('G5'))
ALTO_RANGE = (Pitch('G3'), Pitch('C5'))
TENOR_RANGE = (Pitch('C3'), Pitch('G4'))
BASS_RANGE = (Pitch('F2'), Pitch('C4'))


def voiceNote(noteName, pitchRange):
    '''Generates voicings for a note in a given pitch range.'''
    lowerOctave = pitchRange[0].octave
    upperOctave = pitchRange[1].octave
    for octave in range(lowerOctave, upperOctave + 1):
        n = Pitch(noteName + str(octave))
        if pitchRange[0] <= n <= pitchRange[1]:
            yield n


def _voiceTriadUnordered(noteNames):
    assert len(noteNames) == 3
    for tenor, alto, soprano in itertools.permutations(noteNames, 3):
        for sopranoNote in voiceNote(soprano, SOPRANO_RANGE):
            altoMin = max((ALTO_RANGE[0], sopranoNote.transpose('-P8')))
            altoMax = min((ALTO_RANGE[1], sopranoNote))
            for altoNote in voiceNote(alto, (altoMin, altoMax)):
                tenorMin = max((TENOR_RANGE[0], altoNote.transpose('-P8')))
                tenorMax = min((TENOR_RANGE[1], altoNote))
                for tenorNote in voiceNote(tenor, (tenorMin, tenorMax)):
                    yield Chord([tenorNote, altoNote, sopranoNote])


def _voiceChord(noteNames):
    assert len(noteNames) == 4
    bass = noteNames.pop(0)
    for chord in _voiceTriadUnordered(noteNames):
        for bassNote in voiceNote(bass, BASS_RANGE):
            if bassNote <= chord.bass():
                chord4 = copy.deepcopy(chord)
                chord4.add(bassNote)
                yield chord4


def voiceChord(chord):
    '''Generates four-part voicings for a fifth or seventh chord.

    The bass note is kept intact, though other notes (and doublings) are
    allowed to vary between different voicings. Intervals between adjacent
    non-bass parts are limited to a single octave.
    '''
    noteNames = [pitch.name for pitch in chord.pitches]
    if chord.containsSeventh():
        yield from _voiceChord(noteNames)
    elif chord.inversion() == 2:
        noteNames.append(noteNames[0]) # must double the fifth
        yield from _voiceChord(noteNames)
    else:
        yield from _voiceChord(noteNames + [chord.root().name]) # double the root
        yield from _voiceChord(noteNames + [chord.third.name]) # double the third
        yield from _voiceChord(noteNames + [chord.fifth.name]) # double the fifth


def showChords(chords):
    '''Displays a sequence of chords on a four-part score.

    Soprano and alto parts are displayed on the top (treble) clef, while tenor
    and bass parts are displayed on the bottom (bass) clef, with correct stem
    directions.
    '''
    voices = [Voice() for _ in range(4)]
    for chord in chords:
        bass, tenor, alto, soprano = [Note(p) for p in chord.pitches]
        bass.stemDirection = alto.stemDirection = 'down'
        tenor.stemDirection = soprano.stemDirection = 'up'
        voices[0].append(soprano)
        voices[1].append(alto)
        voices[2].append(tenor)
        voices[3].append(bass)

    female = Part([TrebleClef(), voices[0], voices[1]])
    male = Part([BassClef(), voices[2], voices[3]])
    score = Score([female, male])
    score.show()


def showVoicings(key, numeral):
    '''Displays all the valid voicings of a roman numeral in a key.'''
    chord = RomanNumeral(numeral, key)
    showChords(voiceChord(chord))


def main():
    print(list(voiceChord(RomanNumeral('V7'))))
    showVoicings('G', 'V')


if __name__ == '__main__':
    main()
