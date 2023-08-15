# How to run WavJourney?
1. Install environment by following the bash scripts in `EnvsSetup/`
2. Start API services; The service logs are in the folder of `logs/`
 ```bash
 python scripts/start_services.py
  ```
3. Run AudioJourney client; The results of scripts and audio are in the folder of `output/[datetime]_[instruction text]/`
 ```bash
 conda activate AudioJourney
 python audiojourney_cli.py -f --instruction "News channel BBC broadcast about Trump playing street fighter 6 against Biden"
 ```
4. Kill the API services
 ```bash
python scripts/kill_services.py
  ```

5. Start the UI
 ```bash
sh scripts/start_ui.sh
  ```

  
# Voice Presets
You can add voice presets to WavJourney to customize the voice actors. Simply provide the voice id, the description and a sample wav file, and WavJourney will pick the voice automatically based on the audio script.

Predefined system voice presets are in `data/voice_presets`, whereas session voice presets are in each session's individual folder. See the example below:

- 📂 **project_folder**
  - 📂 **data**
    - 📂 **voice_presets** <-- system voice presets
      - 📄 **metadata.json** <-- system voice preset metadata
      - 📂 **npz**
  - 📂 **output**
    - 📂 **sessions**
      - 📂 **session_1**
        - 📂 **voice_presets** <-- session voice presets
          - 📄 **metadata.json** <-- session voice preset metadata
          - 📂 **npz**
      - 📂 **session_2**
      - **...**

## Add voice to system voice presets via command line
It's recommended to manage voice presets via UI. However if you want to add voice to voice presets via command line. Run the script below:
```bash
python add_voice_preset.py --id "id" --desc "description" --wav-path path/to/wav --session-id session-id
```
if `session-id` is set to '', then you are adding to system voice presets
