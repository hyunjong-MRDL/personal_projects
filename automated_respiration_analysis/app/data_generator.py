import pathlib
import random
from datetime import datetime, timedelta

def generate_random_data(root_dir, num_patients):
    """
    Generates a sample data directory with random patient IDs and data
    that matches the format expected by the dataloader.py script.
    """
    root_path = pathlib.Path(root_dir)
    
    # Create the root directory
    root_path.mkdir(parents=True, exist_ok=True)
    
    data_types = ["STATIC", "ARC"]
    
    for _ in range(num_patients):
        # 1. Randomly assign data type
        data_type = random.choice(data_types)
        
        # 2. Randomly assign patient number (ID_date_datanum)
        patient_id_num = random.randint(10000, 99999)
        random_date = datetime.now() - timedelta(days=random.randint(1, 365))
        date_str = random_date.strftime("%y%m%d")
        datanum = random.randint(1, 99)
        datanum_str = f"{datanum:02d}"
        
        patient_name = f"{patient_id_num}_{date_str}_{datanum_str}"
        
        patient_path = root_path / data_type / patient_name
        
        # 3. Create 4 fractions per patient
        for fraction_num in range(1, 5):
            fraction_path = patient_path / str(fraction_num)
            
            # 4. Create 4 fields per fraction
            for field_num in range(1, 5):
                field_path = fraction_path / f"field{field_num}.txt"
                field_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate some random data points for amplitude
                amplitude_data = []
                num_data_points = 50 + random.randint(-10, 10) # 40-60 points
                for i in range(num_data_points):
                    time = 0.015 * i
                    amplitude = 0.5 + 0.3 * random.uniform(-1, 1) # Random amplitude around 0.5
                    amplitude_data.append(f"{time:.3f}\t{amplitude:.3f}")

                # Generate random beam times
                beam_times = []
                num_beams = random.randint(1, 3) # 1 to 3 beams
                for i in range(num_beams):
                    start_time = random.uniform(0.1, (num_data_points * 0.015) - 0.2)
                    end_time = start_time + random.uniform(0.1, 0.5)
                    beam_times.append(f"{start_time:.2f}\t1")
                    beam_times.append(f"{end_time:.2f}\t0")

                # Combine everything into the file content
                content = f"""
=================
Session Information
=================
-----------------
Amplitude Data
-----------------
=================
Time\tAmplitude
-----------------
{"\n".join(amplitude_data)}

=================
Beam Data
=================
-----------------
Time\tState
-----------------
{"\n".join(beam_times)}

"""
                field_path.write_text(content)
                
    print(f"Generated {num_patients} patients with randomized data at: {root_path.resolve()}")

if __name__ == "__main__":
    generate_random_data("./data", 5)