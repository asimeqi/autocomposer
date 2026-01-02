from midiutil import MIDIFile
import random
import music21 # New library for Sheet Music conversion
import os

# --- 1. HARMONIC MAP ---
chord_map = {
    "C":   {"notes": [60, 62, 64, 65, 67], "root": 48, "neighbors": {"Em": 0.3, "F": 0.3, "G7": 0.3, "C+": 0.1}},
    "Am":  {"notes": [69, 71, 72, 74, 76], "root": 45, "neighbors": {"Dm": 0.5, "E7": 0.5}},
    "Em":  {"notes": [64, 66, 67, 69, 71], "root": 40, "neighbors": {"Am": 0.5, "B7": 0.5}},
    "F":   {"notes": [65, 67, 69, 70, 72], "root": 41, "neighbors": {"G7": 0.5, "C": 0.5, "Dm": 0.5}},
    "Dm":  {"notes": [62, 64, 65, 67, 69], "root": 50, "neighbors": {"G7": 0.8, "C": 0.2}},
    "G7":  {"notes": [67, 69, 71, 74, 77], "root": 43, "neighbors": {"C": 0.9, "Am": 0.1}}, 
    "E7":  {"notes": [64, 68, 71, 74, 76], "root": 52, "neighbors": {"Am": 0.9, "A": 0.1}}, 
    "B7":  {"notes": [59, 63, 66, 69, 71], "root": 47, "neighbors": {"Em": 0.8, "E": 0.2}}, 
    "E":   {"notes": [64, 66, 68, 69, 71], "root": 52, "neighbors": {"A": 0.5, "C#m": 0.5}},
    "C#m": {"notes": [61, 64, 66, 68, 71], "root": 49, "neighbors": {"A": 0.5, "E": 0.5}},
    "A":   {"notes": [69, 71, 73, 74, 76], "root": 45, "neighbors": {"D": 0.5, "E": 0.5}},   
    "D":   {"notes": [62, 64, 66, 67, 69], "root": 50, "neighbors": {"G7": 0.5, "A": 0.5}},  
    "C+":  {"notes": [60, 64, 68, 72],     "root": 48, "neighbors": {"F": 0.5, "Am": 0.5}}, 
}

# --- 2. STYLES (Nuanced) ---
STYLES = {
    "DOOM": {
        "tempo": (70, 90), 
        "rhythm_weights": [50, 20, 20, 0, 0, 10], 
        "inst_melody": 30, "inst_bass": 33, "bass_mode": "sustain",
    },
    "THRASH": {
        "tempo": (150, 175),
        "rhythm_weights": [10, 30, 30, 10, 20, 0], 
        "inst_melody": 29, "inst_bass": 34, "bass_mode": "pump",
    },
    "FUNK_METAL": {
        "tempo": (105, 125),
        "rhythm_weights": [20, 30, 0, 40, 10, 0], 
        "inst_melody": 7, "inst_bass": 36, "bass_mode": "octave",
    },
    "CHAOS": {
        "tempo": (120, 140),
        "rhythm_weights": [15, 15, 15, 15, 20, 20], 
        "inst_melody": 80, "inst_bass": 38, "bass_mode": "random",
    }
}

# --- 3. FACTORIES ---
def generate_dynamic_rhythm(weights):
    cells = {
        "quarter": [1,0,0,0], "eighths": [1,0,1,0], 
        "gallop":  [1,0,0,1], "offbeat": [0,0,1,0], 
        "machine": [1,1,1,1], "empty":   [0,0,0,0] 
    }
    keys = ["quarter", "eighths", "gallop", "offbeat", "machine", "empty"]
    full_pattern = []
    for _ in range(4):
        choice_key = random.choices(keys, weights=weights)[0]
        full_pattern.extend(cells[choice_key])
    return full_pattern

def generate_melodic_contour(num_notes, style_name):
    contour = []
    current_index = 0
    leap_weight = 60 if style_name == "CHAOS" else 30
    step_weight = 100 - leap_weight
    for i in range(num_notes):
        contour.append(current_index)
        move_type = random.choices(["step", "leap"], weights=[step_weight, leap_weight])[0]
        if move_type == "step": current_index += random.choice([-1, 1])
        elif move_type == "leap": current_index += random.choice([-3, -2, 2, 3])
    return contour

def get_next_chord(current_name):
    if current_name not in chord_map: return "C"
    node = chord_map[current_name]
    return random.choices(list(node["neighbors"].keys()), weights=list(node["neighbors"].values()))[0]

# --- 4. SHEET MUSIC CONVERTER ---
def convert_midi_to_sheet_music(midi_filename, xml_filename):
    """
    Reads the generated MIDI file and saves it as MusicXML for viewing.
    """
    try:
        # 1. Parse the MIDI file
        score = music21.converter.parse(midi_filename)
        
        # 2. Clean up for sheet music (Quantize to nearest 16th note)
        # This makes the "Rips/Glissandos" look cleaner on paper
        score.quantize([4], processOffsets=True, processDurations=True, inPlace=True)
        
        # 3. Save as MusicXML
        score.write('musicxml', fp=xml_filename)
        print(f"   📄 Sheet music saved: {xml_filename}")
    except Exception as e:
        print(f"   ⚠️ Could not generate sheet music: {e}")

# --- 5. THE GENERATOR ---
def generate_single_song(filename_base, song_id):
    midi_filename = f"{filename_base}.mid"
    xml_filename = f"{filename_base}.musicxml"
    
    midi = MIDIFile(5)
    
    style_name = random.choice(list(STYLES.keys()))
    style = STYLES[style_name]
    
    bpm = random.randint(style["tempo"][0], style["tempo"][1])
    midi.addTempo(0, 0, bpm)
    
    midi.addProgramChange(0, 0, 0, style["inst_melody"]) 
    midi.addProgramChange(1, 1, 0, style["inst_bass"])   
    midi.addProgramChange(2, 2, 0, 48) 
    midi.addProgramChange(3, 3, 0, 30) 
    
    current_chord = random.choice(list(chord_map.keys()))
    total_bars = 16
    cursor_time = 0.0
    
    main_rhythm = generate_dynamic_rhythm(style["rhythm_weights"])
    num_hits = sum(main_rhythm)
    motif_A = generate_melodic_contour(num_hits, style_name)
    motif_B = generate_melodic_contour(num_hits, style_name)
    
    print(f"[{song_id:02d}] Style: {style_name:<10} | BPM: {bpm} | Key: {current_chord}")

    for bar in range(total_bars):
        chord_data = chord_map[current_chord]
        scale = chord_data["notes"]
        root = chord_data["root"]
        
        # Bass
        if style["bass_mode"] == "sustain":
            midi.addNote(1, 1, root - 12, cursor_time, 4.0, 100)
        elif style["bass_mode"] == "pump":
            for i in range(8): midi.addNote(1, 1, root - 12, cursor_time + (i*0.5), 0.5, 110)
        elif style["bass_mode"] == "octave":
            for i in range(8): 
                p = root - 12 if i%2==0 else root
                midi.addNote(1, 1, p, cursor_time + (i*0.5), 0.5, 110)
        elif style["bass_mode"] == "random":
             for i in range(4):
                 if random.random() > 0.3: midi.addNote(1, 1, root-12, cursor_time+i, 1.0, 100)

        midi.addNote(2, 2, root + 12, cursor_time, 4.0, 60)
        midi.addNote(3, 3, root - 12, cursor_time, 1.0, 85)
        midi.addNote(3, 3, root - 5, cursor_time, 1.0, 85)

        # Drums (Simple Rock)
        midi.addNote(4, 9, 36, cursor_time, 1.0, 120)
        midi.addNote(4, 9, 38, cursor_time + 1.0, 1.0, 120)
        midi.addNote(4, 9, 38, cursor_time + 3.0, 1.0, 120)
        if style_name == "THRASH":
             midi.addNote(4, 9, 36, cursor_time + 2.0, 1.0, 120)
             midi.addNote(4, 9, 36, cursor_time + 2.5, 1.0, 110)
        elif style_name == "FUNK_METAL":
             midi.addNote(4, 9, 36, cursor_time + 2.5, 1.0, 110)
        for eighth in range(8):
            midi.addNote(4, 9, 42, cursor_time + (eighth * 0.5), 0.5, 90)

        # Melody
        if (bar + 1) % 4 == 3: current_contour = motif_B
        else: current_contour = motif_A

        step_duration = 0.25 
        note_index = 0
        
        for i, is_hit in enumerate(main_rhythm):
            if is_hit:
                degree = current_contour[note_index]
                note_index += 1
                
                scale_len = len(scale)
                scale_idx = degree % scale_len
                octave_shift = (degree // scale_len) * 12
                real_pitch = scale[scale_idx] + octave_shift
                note_time = cursor_time + (i * step_duration)
                
                gap_to_next = 1
                for j in range(i+1, len(main_rhythm)):
                    if main_rhythm[j] == 1: break
                    gap_to_next += 1
                max_duration = gap_to_next * step_duration

                # Style-Specific Duration
                if style_name == "THRASH":
                    if random.random() < 0.7: dur = 0.15 
                    else: dur = max_duration
                elif style_name == "DOOM":
                    if random.random() < 0.6: dur = 1.0
                    else: dur = 0.25 
                elif style_name == "CHAOS":
                    dur = random.choice([0.1, 0.25, 0.5])
                else: 
                    dur = max_duration * 0.8

                # Glissando
                if random.random() < 0.15:
                    midi.addNote(0, 0, real_pitch - 3, note_time - 0.15, 0.05, 80)
                    midi.addNote(0, 0, real_pitch - 2, note_time - 0.10, 0.05, 90)
                    midi.addNote(0, 0, real_pitch - 1, note_time - 0.05, 0.05, 100)

                midi.addNote(0, 0, real_pitch, note_time, dur, random.randint(90, 127))
        
        cursor_time += 4.0
        current_chord = get_next_chord(current_chord)

    # Save MIDI
    with open(midi_filename, "wb") as output_file:
        midi.writeFile(output_file)
        
    # Generate Sheet Music from that MIDI
    convert_midi_to_sheet_music(midi_filename, xml_filename)

if __name__ == "__main__":
    print("--- 🎼 Generating Audio + Sheet Music Batch ---")
    for i in range(1, 21):
        base_name = f"song_{i:03d}"
        generate_single_song(base_name, i)
    print("\n✅ DONE! Check your folder for .mid (Audio) and .musicxml (Sheet Music) files.")