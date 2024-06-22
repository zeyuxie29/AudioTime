# AudioCap-Strong
[![arXiv](https://img.shields.io/badge/arXiv-2308.05734-brightgreen.svg?style=flat-square)]() 
[![githubio](https://img.shields.io/badge/GitHub.io-Audio_Samples-blue?logo=Github&style=flat-square)](https://zeyuxie29.github.io/AudioCap-Strong/)

 We present a strongly aligned audio-text dataset, AudioCap-Strong. 
 It provides text annotations rich in temporal information such as timestamps, duration, frequency, and ordering, covering almost all aspects of temporal control. 
 Additionally, we offer a comprehensive test set and evaluation metrics STEAM to assess the temporal control performance of various models. 

 ## Dataset
 Audio samples can be found in the [AudioCap-Strong-Demo](https://zeyuxie29.github.io/AudioCap-Strong/). There are four types of alignment signals:
1. Ordering: "A yip occurs, **followed** by a bleat after a short pause."
2. Duration: "A water tap or faucet ran **for 4.33 seconds**."
3. Frequency: "Sanding occurs **once**, followed by throat clearing **twice**."
4. Timestamp: "An explosion occurs **from 0.947 to 2.561 seconds**, and then breaking sounds are heard **from 4.368 to 5.790 seconds**."


You can download the data from [AudioCap-Strong(train)](https://drive.google.com/file/d/1F26ta621Y8dUe19XVCxtSpl_2meDUtbS/view?usp=sharing) and [AudioCap-Strong(test)](https://drive.google.com/file/d/1Xdpc7oY2oK4edUJCUW-vknQaNTBOpE1T/view?usp=sharing). 
The directory structure is:
```
AudioCap-Strong/
├── train/
│   ├── train5000_ordering/
│   │   ├── audio/
│   │   │   ├── syn_1.wav
│   │   │   ├── syn_2.wav
│   │   │   ├── ...
│   │   │   └── syn_5000.wav
│   │   └── ordering_captions.json
│   ├── ...   
│   └── train5000_timestamp/
└── test/
```
The JSON files contain annotations, including **audio_id**, **metadata**, and **GPT-generated captions**. The dataset statistics are shown in the figure below.
 ![image](https://github.com/zeyuxie29/AudioCap-Strong/assets/137248520/64ba5c46-0d80-4291-8b35-beda48b85b49)






## STEAM：Strongly TEmporally-Aligned evaluation Metric
STEAM is a text-based metric that  evaluates **whether the generated audio segments meet the control requirements specified by the input text.**
STEAM assesses control performance based on detected timestamps and the control signal provided by the input free text.
The testing script is available at [STEAMtool](https://github.com/zeyuxie29/AudioCap-Strong/tree/main/STEAMtool). 

* Ordering: To determine whether the audio generates events A and B in the specified order, quantified by the **error rate**.
* Duration / frequency: Calculate the **absolute error** between the event duration/frequency in the generated audio and the value specified in the text, averaged over the total number of events.
* Timestamp: To measure the accuracy of controlling audio timestamps. **Segment F1**, a common metric in sound event detection tasks, is calculated using the detected and specified on- & off-set.

### Install
```shell
git clone https://github.com/zeyuxie29/AudioCap-Strong.git
cd STEAMtool
pip install -e .
```

Download the audio-text grounding (ATG) model [checkpoint](https://drive.google.com/file/d/1lnkX3AUhFiPvqUZVm-W558sIgyOmHgOZ/view?usp=sharing),
and put it in the path */STEAMtool/steam/grounding_tool/grounding_ckpt/*.

### Evaluation
```python
  python steam/runner/steam_eval.py -p {generated_path} -t {task_name}
```
Where {generated_path} is the path to the generated audio files, and the audio file names need to correspond with the names in the caption files under */STEAMtool/data*. 
{task_name} denotes the task type, with four tasks: "timestamp", "duration", "frequency", and "ordering"(default).

### Result
We test some currently influential TTA generation models.
![image](https://github.com/zeyuxie29/AudioCap-Strong/assets/137248520/8ecb227d-0cf3-4677-ad96-1a22e6881399)

