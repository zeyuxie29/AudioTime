# STEAM：Strongly TEmporally-Aligned evaluation Metric
STEAM is a text-based metric that  evaluates **whether the generated audio segments meet the control requirements specified by the input text.**
STEAM assesses control performance based on detected timestamps and the control signal provided by the input free text.

* Ordering: To determine whether the audio generates events A and B in the specified order, quantified by the **error rate**.
* Duration / frequency: Calculate the **absolute error** between the event duration/frequency in the generated audio and the value specified in the text, averaged over the total number of events.
* Timestamp: To measure the accuracy of controlling audio timestamps. **Segment F1**, a common metric in sound event detection tasks, is calculated using the detected and specified on- & off-set.

## Install
```shell
git clone https://github.com/zeyuxie29/AudioCap-Strong.git
cd STEAMtool
pip install -e .
```

Download the audio-text grounding (ATG) model [checkpoint](https://drive.google.com/file/d/1lnkX3AUhFiPvqUZVm-W558sIgyOmHgOZ/view?usp=sharing),
and put it in the path */STEAMtool/steam/grounding_tool/grounding_ckpt/*.

## Evaluation
```python
  python steam/runner/steam_eval.py -p {generated_path} -t {task_name}
```
Where {generated_path} is the path to the generated audio files, and the audio file names need to correspond with the names in the caption files under */STEAMtool/data*. 
{task_name} denotes the task type, with four tasks: "timestamp", "duration", "frequency", and "ordering"(default).
