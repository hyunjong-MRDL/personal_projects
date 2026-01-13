from pathlib import Path

def patient_listing(root):
    """Data organization (Listing ALL patients in a dictionary)"""
    patients_to_analyze = dict()
    root_path = Path(root)

    for datatype_path in root_path.iterdir():
        if not datatype_path.is_dir():
            continue

        subdirs = [p for p in datatype_path.iterdir() if p.is_dir()]
        
        if len(subdirs) == 1:
            """Case 1: Most simple case"""
            patients_to_analyze[datatype_path.name] = subdirs
        else:
            if not any("education" in str(directory) for directory in subdirs):
                """Case 2: Multiple patients"""
                IDs = [p for p in datatype_path.iterdir() if p.is_dir()]
                patients_to_analyze[datatype_path.name] = IDs
            else:
                """Case 3: Training information included"""
                trained = datatype_path / "education"
                untrained = datatype_path / "non-education"
                trained_IDs = [p for p in trained.iterdir() if p.is_dir()]
                untrained_IDs = [p for p in untrained.iterdir() if p.is_dir()]
                patients_to_analyze[f"{datatype_path.name}_trained"] = trained_IDs
                patients_to_analyze[f"{datatype_path.name}_untrained"] = untrained_IDs
    return patients_to_analyze

def read_field_data(field_path):
    """How to read a field-data (all data are field-data)"""
    """Multiple fields are applied to the patients in each fraction"""
    data_Times, data_Amps = [], []
    beam_Times, beam_States = [], []
    THICK_cnt, thin_cnt = 0, 0
    data_flag, beam_flag  = False, False

    with open(field_path, "r") as file: # Open file
        for line in file:
            if "=============" in line:
                THICK_cnt += 1
            if "-------------" in line:
                thin_cnt += 1
            
            ### Read time-data
            if (THICK_cnt >= 4) and (thin_cnt == 1):
                if data_flag and line == "\n": data_flag = False
                if data_flag:
                    time, amplitude = line.strip().split("\t")
                    data_Times.append(float(time))
                    data_Amps.append(float(amplitude) * 10.0) # cm to mm
                if (THICK_cnt >= 4 and thin_cnt <= 1) and ("Amplitude" in line): data_flag = True
            
            ### Read beam-data
            if (THICK_cnt >= 6):
                if beam_flag and line == "\n": break
                elif beam_flag:
                    time, state = line.strip().split("\t")
                    beam_Times.append(float(time))
                    beam_States.append(int(state))
                elif ("Time" in line): beam_flag = True

    return (data_Times, data_Amps), (beam_Times, beam_States)