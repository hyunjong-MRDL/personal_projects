import numpy as np
from app import dataloader

def beam_modification(beam_Times, beam_States):
    """Modifies beam times to handle short intervals."""
    paired_beams = sorted(zip(beam_Times, beam_States))
    
    modified_intervals = []
    current_start = None
    for time, state in paired_beams:
        if state == 1:
            current_start = time
        elif state == 0 and current_start is not None:
            interval_duration = time - current_start
            if interval_duration >= 0.1:
                modified_intervals.append(current_start)
                modified_intervals.append(time)
            current_start = None # Reset for the next interval
            
    return modified_intervals

def beam_enabling_intervals(data_Times, data_Amps, beam_Times):
    """Returns the enabled intervals and their count."""
    dt = 0.015
    total_intervals = []
    for i in range(len(beam_Times)//2):
        start_time = beam_Times[2*i]
        end_time = beam_Times[2*i+1]
        
        start_index = next((j for j, t in enumerate(data_Times) if t >= start_time), None)
        
        if start_index is None:
            continue
            
        end_index = next((j for j, t in enumerate(data_Times) if t >= end_time), len(data_Times))
        
        interval = data_Amps[start_index:end_index]
        if interval:
            total_intervals.append(interval)

    return total_intervals, len(total_intervals)

def avg_lvl_per_interval(Amps):
    """Calculates the average level per interval."""
    if not Amps:
        return 0.0
    return np.sum(Amps) / len(Amps)

def reproducibility(avg_levels):
    """Calculates reproducibility as max - min."""
    if not avg_levels:
        return 0.0
    return max(avg_levels) - min(avg_levels)

def error_per_interval(Amps):
    """Calculates the vertical error per interval."""
    dt = 0.015
    Times = [t*dt for t in range(len(Amps))]
    if len(Amps) < 2:
        return 0.0
    slope, _ = np.polyfit(Times, Amps, deg=1)
    duration = dt * ( len(Amps) - 1 )
    return abs(slope) * duration

def stability(errors):
    """Calculates stability as the maximum error."""
    if not errors:
        return 0.0
    return max(errors)

def compute_fraction_metrics(list_of_field_series):
    per_field_levels, per_field_errors = [], []
    for (data_Times, data_Amps), (beam_Times, beam_States) in list_of_field_series:
        modified_beam_Times = beam_modification(beam_Times, beam_States)
        enabled_intervals, num_intervals = beam_enabling_intervals(data_Times, data_Amps, modified_beam_Times)
        total_intv_levels, total_intv_errors = 0, 0
        
        if num_intervals == 0:
            continue

        for intv in range(num_intervals):
            average_level = avg_lvl_per_interval(enabled_intervals[intv])
            vertical_error = error_per_interval(enabled_intervals[intv])
            total_intv_levels += average_level
            total_intv_errors += vertical_error
        
        per_field_levels.append((total_intv_levels / num_intervals))
        per_field_errors.append((total_intv_errors / num_intervals))

    if not per_field_levels or not per_field_errors:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    inter_reprod = reproducibility(per_field_levels)
    inter_stab = stability(per_field_errors)
    level_mean, error_mean = np.mean(per_field_levels), np.mean(per_field_errors)
    level_std, error_std = np.std(per_field_levels), np.std(per_field_errors)
    return round(inter_reprod, 4), round(level_mean, 4), round(level_std, 4), round(inter_stab, 4), round(error_mean, 4), round(error_std, 4)

def batch_processing(total_patients):
    total_results = dict()
    for patient_path in total_patients:
        curr_ID = patient_path.name
        patient_results = dict()
        
        fractions = sorted([f for f in patient_path.iterdir() if f.is_dir()], key=lambda x: int(x.name))
        
        for fx_path in fractions:
            per_fraction_data = []
            fields = sorted([f for f in fx_path.iterdir() if f.is_file()], key=lambda x: x.name)
            
            for fld_data in fields:
                per_fraction_data.append(fld_data)
                
            fx_result = compute_fraction_metrics([dataloader.read_field_data(f) for f in per_fraction_data])
            patient_results[fx_path.name] = fx_result
            
        total_results[curr_ID] = patient_results
        
    return total_results